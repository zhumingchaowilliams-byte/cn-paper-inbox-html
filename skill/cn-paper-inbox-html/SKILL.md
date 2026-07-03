---
name: cn-paper-inbox-html
description: Portable Chinese paper inbox workflow for environmental materials, water treatment, and pollution-control papers. Use when Codex needs to process folders containing only a main paper PDF and supplementary materials, auto-extract embedded PDF images or fallback figure pages when images are missing, generate Chinese deep-reading notes with the current agent's own token budget, export polished HTML, avoid YAML/frontmatter note properties, or package the workflow for students and collaborators.
---

# 中文文献投递箱 HTML

## Core Workflow

Use `scripts/process_paper_inbox.py` for deterministic file preparation and finalization. The current Codex/Claude agent should generate the Chinese note itself; do not require a DeepSeek API key for normal interactive use.

The minimum input is:

```text
<inbox>\<paper-folder>\
  正文.pdf
  补充材料.docx / supplementary.pdf / .txt / .md
```

Optional manually named images are supported but not required:

```text
  图文摘要.jpg
  图1.jpg
  图2.jpg
```

Also support `supplements\` and `figures\` subfolders. If no manual images are provided, run `--prepare`; the script first extracts real embedded PDF image objects into `<vault>\Assets\Papers\<doi-safe>\pdf-extracted-images\`. If no usable embedded images are found, it falls back to rendering PDF pages containing Fig./Figure/图号 labels into `<vault>\Assets\Papers\<doi-safe>\pdf-auto-pages\`.

## Output Rules

- Write Chinese by default.
- Generate Markdown without YAML/frontmatter/note properties.
- Generate a same-title HTML file with readable CSS.
- Strip model preambles such as “好的，遵照您的指示”, “以下是”, and any text before the first `#` heading.
- Do not output code fences around the note.
- If auto-extracted PDF figure pages exist, inspect them directly when the runtime supports image viewing; otherwise use only PDF text, figure captions, tables, and supplement text.
- Treat supplementary materials as core evidence for synthesis methods, characterization details, experimental conditions, and controls.

## Commands

Recommended agent-first flow:

```bash
python scripts/process_paper_inbox.py --inbox <inbox> --vault <vault> --prepare <folder-name>
```

Then read `<vault>\AI Inputs\<doi-safe>.agent_task.md`, the generated text packet, and, if present, inspect extracted PDF images or fallback rendered PDF figure pages. Write the Chinese note yourself as Markdown, starting directly with `# 标题`. Save it to a temporary `.md` file, then finalize:

```bash
python scripts/process_paper_inbox.py --inbox <inbox> --vault <vault> --finalize <folder-name> --generated-md <generated-note.md>
```

Utility commands:

```bash
python scripts/process_paper_inbox.py --inbox <inbox> --vault <vault> --scan
python scripts/process_paper_inbox.py --inbox <inbox> --vault <vault> --process-all
python scripts/process_paper_inbox.py --inbox <inbox> --vault <vault> --refresh-assets <folder-name>
```

## Model Routing

- Normal interactive use: do not call DeepSeek or Claude CLI; the current Codex/Claude agent reads the prepared packet and generates the Markdown.
- Optional unattended batch mode: `--process` and `--process-all` can use `DEEPSEEK_API_KEY` or Claude CLI, but this is not required for skill use.

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
<vault>\AI Inputs\<doi-safe>.agent_task.md
<vault>\AI Outputs\<doi-safe>.run_log.md
<paper-folder>\处理状态.json
<paper-folder>\处理结果.md
```

If DOI extraction fails, mark the folder `needs_review` and do not pretend the citation is complete.
