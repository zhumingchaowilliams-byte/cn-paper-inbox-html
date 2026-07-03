---
name: cn-paper-inbox-html
description: Portable Chinese paper inbox workflow for environmental materials, water treatment, and pollution-control papers. Use when Codex needs to process folders containing only a main paper PDF and supplementary materials, generate Chinese deep-reading notes, export polished HTML, avoid YAML/frontmatter note properties, or package the workflow for students and collaborators.
---

# 中文文献投递箱 HTML

## Core Workflow

Use `scripts/process_paper_inbox.py` for deterministic processing. The minimum input is:

```text
<inbox>\<paper-folder>\
  正文.pdf
  补充材料.docx / supplementary.pdf / .txt / .md
```

Optional images are supported but not required:

```text
  图文摘要.jpg
  图1.jpg
  图2.jpg
```

Also support `supplements\` and `figures\` subfolders.

## Output Rules

- Write Chinese by default.
- Generate Markdown without YAML/frontmatter/note properties.
- Generate a same-title HTML file with readable CSS.
- Strip model preambles such as “好的，遵照您的指示”, “以下是”, and any text before the first `#` heading.
- Do not output code fences around the note.
- Do not infer image content; use only PDF text, figure captions, tables, and supplement text.
- Treat supplementary materials as core evidence for synthesis methods, characterization details, experimental conditions, and controls.

## Commands

Scan an inbox:

```bash
python scripts/process_paper_inbox.py --inbox <inbox> --vault <vault> --scan
```

Process one folder:

```bash
python scripts/process_paper_inbox.py --inbox <inbox> --vault <vault> --process <folder-name> --force
```

Process all new or failed folders:

```bash
python scripts/process_paper_inbox.py --inbox <inbox> --vault <vault> --process-all
```

Refresh manually supplied images:

```bash
python scripts/process_paper_inbox.py --inbox <inbox> --vault <vault> --refresh-assets <folder-name>
```

## Model Routing

- Prefer DeepSeek when `DEEPSEEK_API_KEY` is set.
- Fall back to Claude CLI when DeepSeek is not configured.
- Use the `--model deepseek` or `--model claude` flag only when the user explicitly wants a route.

## Default Local Paths

The bundled script defaults to portable local folders:

```text
inbox: <current directory>\paper
vault: <current directory>\vault
```

For real work, prefer passing `--inbox` and `--vault` explicitly.

## Expected Outputs

```text
<vault>\Knowledge\Paper Deep Readings\<title>.md
<vault>\Knowledge\Paper Deep Readings HTML\<title>.html
<vault>\AI Inputs\<doi-safe>.paper_text_packet.md
<vault>\AI Outputs\<doi-safe>.run_log.md
<paper-folder>\处理状态.json
<paper-folder>\处理结果.md
```

If DOI extraction fails, mark the folder `needs_review` and do not pretend the citation is complete.
