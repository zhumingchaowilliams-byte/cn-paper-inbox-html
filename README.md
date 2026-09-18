# CN Paper Inbox HTML

中文文献投递箱：把论文正文 PDF 和补充材料放进一个文件夹，让正在使用的 Codex/Claude 直接生成中文深读 Markdown 和可分享 HTML。

适合环境材料、水处理、污染控制等论文精读工作流。输出重点是实验方法、结果解释、机制链条和后续知识库复用。

## Features

- 只需要 `正文.pdf` 和补充材料即可处理。
- 支持补充材料：`.docx`、`.pdf`、`.txt`、`.md`。
- 可选图片：`图文摘要.jpg`、`图1.jpg`、`图2.jpg` 等；未提供图片时先用 `pdfplumber` 找 PDF 图像与 figure 区域坐标，再用 `pypdfium2` 裁剪真正的图面，抽不到时才渲染含 Fig./Figure/图号的页面兜底。
- 深读笔记必须把可用图像嵌入 `图文导读` 对应小节，形成原图加中文识读，不能只写文字版图文导读。
- 生成无 YAML/frontmatter 的 Markdown。
- 生成同题名 HTML，表格带斑马纹与深色表头，窄屏可横向滚动，支持打印分页控制，适合直接分享给学生或同事。
- 表格、粗体、斜体、行内代码、代码块、引用、列表均正确渲染，即使 Markdown 渲染库缺失也会自动切到内置渲染器并告警，不会把表格压成一行。
- 无需任何外部模型 API Key：谁在 Agent 里使用，就消耗谁当前会话的 token。
- 自动剔除模型客套开头，例如“好的，遵照您的指示”。
- 附带 Agent skill，可复制到 `.codex/skills` 或 `~/.workbuddy/skills` 后复用。

## Folder Format

最小输入：

```text
paper-inbox/
  any-paper-folder/
    正文.pdf
    补充材料.docx
```

可选图片：

```text
paper-inbox/
  any-paper-folder/
    正文.pdf
    补充材料.docx
    图文摘要.jpg
    图1.jpg
    图2.jpg
```

也支持：

```text
paper-inbox/
  any-paper-folder/
    正文.pdf
    supplements/
      补充材料.docx
    figures/
      图文摘要.jpg
      图1.jpg
```

## Install

```bash
pip install -r requirements.txt
```

不需要任何 API Key。若 HTML 中表格被压成一行纯文本，说明 `Markdown` 包不完整，执行 `pip install --force-reinstall Markdown` 修复。

## CLI Usage

Agent-first workflow, recommended:

```bash
python scripts/process_paper_inbox.py --inbox E:\paper --vault E:\MyVault --prepare my-paper-folder
```

Then ask the current Agent to read:

```text
<vault>/AI Inputs/<doi-safe>.agent_task.md
<vault>/AI Inputs/<doi-safe>.paper_text_packet.md
<vault>/Assets/Papers/<doi-safe>/pdf-extracted-images/
<vault>/Assets/Papers/<doi-safe>/pdf-auto-pages/
```

The Agent should inspect available visual assets, crop fallback page renders when practical, insert each figure under the matching `Fig. N` / `图N` heading with Obsidian embed syntax, and write the Chinese figure interpretation below the image.

The Agent writes its generated Markdown to a temporary file, then finalizes:

```bash
python scripts/process_paper_inbox.py --inbox E:\paper --vault E:\MyVault --finalize my-paper-folder --generated-md generated-note.md
```

On Windows, `--generated-md` must be a native path such as `C:\path\note.md`. Git Bash style `/c/path/note.md` is treated as a literal string and will fail.

Auxiliary commands:

```bash
python scripts/process_paper_inbox.py --inbox E:\paper --vault E:\MyVault --scan
python scripts/process_paper_inbox.py --inbox E:\paper --vault E:\MyVault --refresh-assets my-paper-folder
```

Outputs:

```text
<vault>/Knowledge/Paper Deep Readings/<title>.md
<vault>/Knowledge/Paper Deep Readings HTML/<title>.html
<vault>/AI Inputs/<doi-safe>.paper_text_packet.md
<vault>/AI Inputs/<doi-safe>.agent_task.md
<vault>/AI Outputs/<doi-safe>.run_log.md
<paper-folder>/处理状态.json
<paper-folder>/处理结果.md
```

## Formatting Rules

笔记由当前 Agent 撰写，脚本负责渲染。写笔记时遵守以下约定，避免格式塌陷。

- 表格必须写标准 Markdown 表头分隔行，即首行表头、第二行 `|---|---|`，且分隔行列数与表头一致。
- 表格单元格内不要换行，避免裸竖线字符，列数以 2 至 4 列为宜。
- 段落中不要用竖线做分隔符。
- 强调用 `**粗体**`，术语首次出现可用 `*斜体*`，不要整段加粗。
- 输出不含 YAML frontmatter，不加客套开头，不套代码围栏。

## Desktop App

Run:

```bash
python app/paper_inbox_app.py
```

Defaults:

```text
PAPER_INBOX_DIR=<current directory>\paper
PAPER_VAULT_DIR=<current directory>\vault
```

Override them before launching:

```powershell
$env:PAPER_INBOX_DIR="D:\paper"
$env:PAPER_VAULT_DIR="D:\ObsidianVault"
python app\paper_inbox_app.py
```

## Install As Skill

Copy this folder:

```text
skill/cn-paper-inbox-html
```

to one of the following, depending on the client.

WorkBuddy, user level and available in every project:

```text
C:\Users\<you>\.workbuddy\skills\cn-paper-inbox-html
```

Codex:

```text
C:\Users\<you>\.codex\skills\cn-paper-inbox-html
```

Then ask the Agent to use `cn-paper-inbox-html`.

## Notes

- This tool does not bypass paywalls or download papers illegally.
- Do not commit API keys, PDFs, or unpublished data.
- In agent-first mode, the current Agent can inspect auto-cropped PDF figure regions when no manual images are provided. Full-page renders are only a fallback for vector-only or hard-to-extract figures.
- If visual assets exist, a finished note should not have a text-only `图文导读`.
- Tables require a standard Markdown header separator row. Without it the renderer falls back to plain text.
