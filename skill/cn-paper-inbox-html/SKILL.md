---
name: cn-paper-inbox-html
description: Portable Chinese paper inbox workflow for environmental materials, water treatment, and pollution-control papers. Use when Codex needs to process folders containing only a main paper PDF and supplementary materials, auto-crop PDF figure regions with pdfplumber coordinates and pypdfium2 when images are missing, generate Chinese deep-reading notes with the current agent's own token budget, export polished HTML, avoid YAML/frontmatter note properties, or package the workflow for students and collaborators.
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

Also support `supplements\` and `figures\` subfolders. If no manual images are provided, run `--prepare`; the script first uses `pdfplumber` to find PDF image objects and caption-guided figure regions, then uses `pypdfium2` to crop those regions into `<vault>\Assets\Papers\<doi-safe>\pdf-extracted-images\`. If no usable figure region is found, it falls back to rendering PDF pages containing Fig./Figure/图号 labels into `<vault>\Assets\Papers\<doi-safe>\pdf-auto-pages\`.

## Figure Recognition And Insertion

- Treat figure extraction as required for PDF-based deep readings, not as optional decoration.
- Before writing the final Markdown, inspect the manual images, `pdf-extracted-images`, or fallback `pdf-auto-pages` when the runtime supports image viewing.
- In `图文导读`, insert each available figure immediately below its `Fig. N` / `图N` heading using Obsidian embed syntax, for example `![[Assets/Papers/<doi-safe>/图1.png]]` or the generated extracted-image path.
- If the script only produced full-page renders, crop the figure region manually/programmatically when practical; otherwise embed the page render and label it as a fallback figure page.
- Write the Chinese interpretation under the image. Base visual statements only on the visible image plus the caption/text packet; do not invent visual details.

## Output Rules

- Write Chinese by default.
- Generate Markdown without YAML/frontmatter/note properties.
- Generate a same-title HTML file with readable CSS.
- Strip model preambles such as “好的，遵照您的指示”, “以下是”, and any text before the first `#` heading.
- Do not output code fences around the note.
- If auto-extracted PDF figure pages exist, inspect them directly when the runtime supports image viewing; otherwise use only PDF text, figure captions, tables, and supplement text.
- Do not leave `图文导读` text-only when visual assets exist; the note should read as “original figure + Chinese interpretation”.
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
