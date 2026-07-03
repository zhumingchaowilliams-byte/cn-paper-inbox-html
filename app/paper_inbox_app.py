#!/usr/bin/env python3
"""PySide6 desktop app for the paper inbox."""

from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from PIL import Image
from PySide6.QtCore import QThread, Signal, Qt
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QSplitter,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from process_paper_inbox import (
    DEFAULT_INBOX,
    DEFAULT_VAULT,
    PaperRecord,
    extract_pdf_metadata,
    process_folder,
    refresh_assets,
    safe_name,
    scan_inbox,
)


class Worker(QThread):
    finished_records = Signal(list)
    failed = Signal(str)

    def __init__(self, folders: list[Path], force: bool = False):
        super().__init__()
        self.folders = folders
        self.force = force

    def run(self) -> None:
        try:
            records = [process_folder(folder, DEFAULT_VAULT, force=self.force) for folder in self.folders]
            self.finished_records.emit(records)
        except Exception as exc:
            self.failed.emit(str(exc))


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("文献投递箱")
        self.resize(1320, 760)
        self.records: list[PaperRecord] = []
        self.worker: Worker | None = None
        self.status_label = QLabel("准备就绪")
        self.table = QTableWidget(0, 11)
        self.table.setHorizontalHeaderLabels(
            ["状态", "文件夹", "DOI", "题名", "页数", "补充材料", "图片", "缺图", "图片复核", "Obsidian 笔记", "HTML"]
        )
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)

        left = QWidget()
        left_layout = QVBoxLayout(left)
        left_layout.addLayout(self._build_list_buttons())
        left_layout.addWidget(self.table)

        right = self._build_rules_panel()
        splitter = QSplitter()
        splitter.addWidget(left)
        splitter.addWidget(right)
        splitter.setStretchFactor(0, 4)
        splitter.setStretchFactor(1, 1)

        layout = QVBoxLayout()
        layout.addWidget(splitter)
        layout.addWidget(self.status_label)
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        refresh_action = QAction("刷新", self)
        refresh_action.triggered.connect(self.scan)
        self.addAction(refresh_action)
        self.scan()

    def _build_list_buttons(self) -> QHBoxLayout:
        scan_btn = QPushButton("扫描投递箱")
        process_btn = QPushButton("处理选中文献")
        process_all_btn = QPushButton("处理全部新文献/失败重试")
        force_btn = QPushButton("重新处理")
        refresh_assets_btn = QPushButton("刷新图片")
        open_btn = QPushButton("打开 Obsidian 笔记")
        open_html_btn = QPushButton("打开 HTML")
        open_folder_btn = QPushButton("打开投递箱")

        scan_btn.clicked.connect(self.scan)
        process_btn.clicked.connect(self.process_selected)
        process_all_btn.clicked.connect(self.process_all_new)
        force_btn.clicked.connect(self.force_selected)
        refresh_assets_btn.clicked.connect(self.refresh_selected_assets)
        open_btn.clicked.connect(self.open_note)
        open_html_btn.clicked.connect(self.open_html)
        open_folder_btn.clicked.connect(lambda: os.startfile(str(DEFAULT_INBOX)))

        buttons = QHBoxLayout()
        for btn in [scan_btn, process_btn, process_all_btn, force_btn, refresh_assets_btn, open_btn, open_html_btn, open_folder_btn]:
            buttons.addWidget(btn)
        buttons.addStretch(1)
        return buttons

    def _build_rules_panel(self) -> QWidget:
        panel = QWidget()
        outer = QVBoxLayout(panel)

        group = QGroupBox("固定投递规则")
        layout = QVBoxLayout(group)

        rules = QLabel(
            f"学生只需要把每篇文献放进 {DEFAULT_INBOX} 的一个文件夹。\n\n"
            "推荐命名：\n"
            f"{DEFAULT_INBOX}\\任意文件夹名\\\n"
            "  正文.pdf\n"
            "  补充材料.docx / supplementary.pdf\n"
            "  图文摘要.jpg\n"
            "  图1.jpg\n"
            "  图2.jpg\n"
            "  ...\n\n"
            "也兼容：\n"
            "  supplements\\补充材料.docx\n"
            "  figures\\图1.jpg\n\n"
            "图片只按文件名插入，不做 AI 识图。11 张图就一次性放图1到图11，不需要逐张上传。"
        )
        rules.setWordWrap(True)
        layout.addWidget(rules)

        open_inbox = QPushButton(f"打开 {DEFAULT_INBOX}")
        open_inbox.clicked.connect(lambda: os.startfile(str(DEFAULT_INBOX)))
        scan_process = QPushButton("扫描并处理新文献")
        scan_process.clicked.connect(self.scan_then_process_new)
        layout.addWidget(open_inbox)
        layout.addWidget(scan_process)
        outer.addWidget(group)
        outer.addStretch(1)
        return panel

    def scan(self) -> None:
        self.records = scan_inbox(DEFAULT_INBOX, DEFAULT_VAULT)
        self.render()
        self.status_label.setText(f"已扫描 {DEFAULT_INBOX}，共 {len(self.records)} 篇")

    def render(self) -> None:
        self.table.setRowCount(len(self.records))
        for row, record in enumerate(self.records):
            values = [
                record.status,
                record.folder,
                record.doi,
                record.title,
                str(record.pages or ""),
                ", ".join(record.supplements or []),
                ", ".join(record.images or []),
                ", ".join(record.missing_figures or []),
                "; ".join(record.image_review or []),
                record.note_path,
                record.html_path,
            ]
            for col, value in enumerate(values):
                item = QTableWidgetItem(value)
                if col == 0:
                    item.setTextAlignment(Qt.AlignCenter)
                item.setToolTip(record.message or value)
                self.table.setItem(row, col, item)
        self.table.resizeColumnsToContents()

    def selected_records(self) -> list[PaperRecord]:
        rows = sorted({idx.row() for idx in self.table.selectionModel().selectedRows()})
        return [self.records[row] for row in rows]

    def choose_pdf(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, "选择正文 PDF", str(DEFAULT_INBOX), "PDF Files (*.pdf)")
        if path:
            self.selected_pdf = Path(path)
            self.pdf_label.setText(str(self.selected_pdf))
            try:
                _pages, title, doi, _text = extract_pdf_metadata(self.selected_pdf)
                if not self.task_name_edit.text().strip():
                    self.task_name_edit.setText((doi.replace("/", "_") if doi else safe_name(title, 80)))
            except Exception:
                pass

    def choose_supplements(self) -> None:
        paths, _ = QFileDialog.getOpenFileNames(
            self,
            "选择补充材料",
            str(DEFAULT_INBOX),
            "Supplement Files (*.docx *.pdf *.txt *.md)",
        )
        for path in paths:
            p = Path(path)
            if p not in self.selected_supplements:
                self.selected_supplements.append(p)
        self.refresh_task_lists()

    def choose_graphical(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self,
            "选择图文摘要",
            str(DEFAULT_INBOX),
            "Images (*.jpg *.jpeg *.png *.webp)",
        )
        if path:
            self.selected_images["图文摘要"] = Path(path)
            self.refresh_task_lists()

    def add_figure_image(self) -> None:
        label = f"图{self.figure_spin.value()}"
        path, _ = QFileDialog.getOpenFileName(
            self,
            f"选择{label}",
            str(DEFAULT_INBOX),
            "Images (*.jpg *.jpeg *.png *.webp)",
        )
        if path:
            self.selected_images[label] = Path(path)
            self.figure_spin.setValue(min(99, self.figure_spin.value() + 1))
            self.refresh_task_lists()

    def refresh_task_lists(self) -> None:
        self.supplement_list.clear()
        for path in self.selected_supplements:
            self.supplement_list.addItem(str(path))
        self.image_list.clear()
        for label, path in sorted(self.selected_images.items(), key=lambda item: self._image_key(item[0])):
            self.image_list.addItem(f"{label}: {path}")

    @staticmethod
    def _image_key(label: str) -> tuple[int, int]:
        if label == "图文摘要":
            return (0, 0)
        if label.startswith("图") and label[1:].isdigit():
            return (1, int(label[1:]))
        return (2, 999)

    def preview_images(self) -> None:
        if not self.selected_images:
            QMessageBox.information(self, "图片预览", "还没有选择图片。")
            return
        lines = []
        for label, path in sorted(self.selected_images.items(), key=lambda item: self._image_key(item[0])):
            try:
                with Image.open(path) as image:
                    lines.append(f"{label}: {path.name}  {image.width} x {image.height}")
            except Exception as exc:
                lines.append(f"{label}: {path.name}  读取失败：{exc}")
        QMessageBox.information(self, "图片预览", "\n".join(lines))

    def save_task(self) -> None:
        if not self.selected_pdf:
            QMessageBox.information(self, "提示", "请先选择正文 PDF。")
            return
        name = self.task_name_edit.text().strip()
        if not name:
            try:
                _pages, title, doi, _text = extract_pdf_metadata(self.selected_pdf)
                name = doi.replace("/", "_") if doi else safe_name(title, 80)
            except Exception:
                name = safe_name(self.selected_pdf.stem, 80)
        folder = self.unique_task_folder(safe_name(name, 100))
        folder.mkdir(parents=True, exist_ok=True)
        shutil.copy2(self.selected_pdf, folder / "正文.pdf")
        if self.selected_supplements:
            supp_dir = folder / "supplements"
            supp_dir.mkdir(exist_ok=True)
            for path in self.selected_supplements:
                shutil.copy2(path, supp_dir / path.name)
        if self.selected_images:
            fig_dir = folder / "figures"
            fig_dir.mkdir(exist_ok=True)
            for label, path in self.selected_images.items():
                shutil.copy2(path, fig_dir / f"{label}{path.suffix.lower()}")
        self.current_task_folder = folder
        self.status_label.setText(f"已保存任务：{folder}")
        self.scan()

    def unique_task_folder(self, base_name: str) -> Path:
        folder = DEFAULT_INBOX / base_name
        if not folder.exists():
            return folder
        index = 2
        while True:
            candidate = DEFAULT_INBOX / f"{base_name} ({index})"
            if not candidate.exists():
                return candidate
            index += 1

    def process_current_task(self) -> None:
        if not self.current_task_folder:
            self.save_task()
        if self.current_task_folder:
            self.start_worker([self.current_task_folder], force=True)

    def clear_task(self) -> None:
        self.selected_pdf = None
        self.selected_supplements = []
        self.selected_images = {}
        self.current_task_folder = None
        self.pdf_label.setText("未选择")
        self.task_name_edit.clear()
        self.refresh_task_lists()

    def process_selected(self) -> None:
        selected = self.selected_records()
        if not selected:
            QMessageBox.information(self, "提示", "请先选择一篇或多篇文献。")
            return
        folders = [Path(record.folder_path) for record in selected]
        self.start_worker(folders, force=False)

    def force_selected(self) -> None:
        selected = self.selected_records()
        if not selected:
            QMessageBox.information(self, "提示", "请先选择要重新处理的文献。")
            return
        folders = [Path(record.folder_path) for record in selected]
        self.start_worker(folders, force=True)

    def process_all_new(self) -> None:
        self.scan()
        folders = [Path(record.folder_path) for record in self.records if record.status in {"new", "needs_retry"}]
        if not folders:
            QMessageBox.information(self, "提示", "没有需要处理的新文献或需重试文献。")
            return
        self.start_worker(folders, force=False)

    def scan_then_process_new(self) -> None:
        self.process_all_new()

    def refresh_selected_assets(self) -> None:
        selected = self.selected_records()
        if not selected:
            QMessageBox.information(self, "提示", "请先选择要刷新图片的文献。")
            return
        for record in selected:
            refresh_assets(Path(record.folder_path), DEFAULT_VAULT)
        self.scan()
        self.status_label.setText("图片资产已刷新")

    def start_worker(self, folders: list[Path], force: bool) -> None:
        self.status_label.setText(f"正在处理 {len(folders)} 篇，请不要关闭窗口...")
        self.worker = Worker(folders, force=force)
        self.worker.finished_records.connect(self.on_worker_done)
        self.worker.failed.connect(self.on_worker_failed)
        self.worker.start()

    def on_worker_done(self, _records: list[PaperRecord]) -> None:
        self.scan()
        self.status_label.setText("处理完成")

    def on_worker_failed(self, message: str) -> None:
        self.scan()
        QMessageBox.critical(self, "处理失败", message)

    def open_note(self) -> None:
        selected = self.selected_records()
        if not selected:
            QMessageBox.information(self, "提示", "请先选择一篇文献。")
            return
        note = selected[0].note_path
        if not note or not Path(note).exists():
            QMessageBox.information(self, "提示", "这篇还没有生成 Obsidian 笔记。")
            return
        os.startfile(note)

    def open_html(self) -> None:
        selected = self.selected_records()
        if not selected:
            QMessageBox.information(self, "提示", "请先选择一篇文献。")
            return
        html_path = selected[0].html_path
        if not html_path or not Path(html_path).exists():
            QMessageBox.information(self, "提示", "这篇还没有生成 HTML 文件。")
            return
        os.startfile(html_path)


def main() -> int:
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
