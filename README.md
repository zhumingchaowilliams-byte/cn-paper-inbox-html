# CN Paper Inbox HTML

中文文献投递箱：把论文正文 PDF 和补充材料放进一个文件夹，让正在使用的 Codex/Claude 直接生成中文深读 Markdown 和可分享 HTML。

适合环境材料、水处理、污染控制等论文精读工作流。输出重点是实验方法、结果解释、机制链条和后续知识库复用。

## Features

- 只需要 `正文.pdf` 和补充材料即可处理。
- 支持补充材料：`.docx`、`.pdf`、`.txt`、`.md`。
- 可选图片：`图文摘要.jpg`、`图1.jpg`、`图2.jpg` 等；未提供图片时先用 `pdfplumber` 找 PDF 图像/figure 区域坐标，再用 `pypdfium2` 裁剪真正的图面，抽不到时才渲染含 Fig./Figure/图号的页面兜底。
- 深读笔记必须把可用图像嵌入 `图文导读` 对应小节，形成“原图 + 中文识读”；不能只写文字版图文导读。
- 生成无 YAML/frontmatter 的 Markdown。
- 生成同题名 HTML 文件，适合直接分享给学生或同事。
- 自动剔除模型客套开头，例如“好的，遵照您的指示”。
- 默认不需要 DeepSeek API：谁在 Codex/Claude 里使用，就消耗谁当前 Agent 的 token。
- 仍保留可选的 DeepSeek/Claude CLI 批处理模式。
- 附带 Codex skill，可复制到 `.codex/skills` 后复用。

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

Optional:

- Set `DEEPSEEK_API_KEY` only if you want unattended DeepSeek batch processing.
- Install and log in to Claude CLI only if you want unattended Claude CLI fallback.

Windows user environment variable example:

```powershell
[Environment]::SetEnvironmentVariable("DEEPSEEK_API_KEY", "<your-deepseek-api-key>", "User")
```

## CLI Usage

Agent-first workflow, recommended for Codex or Claude:

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

Legacy unattended workflow, optional:

```bash
python scripts/process_paper_inbox.py --inbox E:\paper --vault E:\MyVault --scan
python scripts/process_paper_inbox.py --inbox E:\paper --vault E:\MyVault --process my-paper-folder
python scripts/process_paper_inbox.py --inbox E:\paper --vault E:\MyVault --process-all
```

Outputs:

```text
<vault>/Knowledge/Paper Deep Readings/<title>.md
<vault>/Knowledge/Paper Deep Readings HTML/<title>.html
<vault>/AI Inputs/<doi-safe>.paper_text_packet.md
<vault>/AI Inputs/<doi-safe>.agent_task.md
<vault>/AI Outputs/<doi-safe>.run_log.md
```

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

## Install As Codex Skill

Copy this folder:

```text
skill/cn-paper-inbox-html
```

to:

```text
C:\Users\<you>\.codex\skills\cn-paper-inbox-html
```

Then ask Codex to use `cn-paper-inbox-html`.

## Notes

- This tool does not bypass paywalls or download papers illegally.
- Do not commit API keys, PDFs, or unpublished data.
- In agent-first mode, the current Codex/Claude can inspect auto-cropped PDF figure regions when no manual images are provided. Full-page renders are only a fallback for vector-only or hard-to-extract figures.
- If visual assets exist, a finished note should not have a text-only `图文导读`.
