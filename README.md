# 珠峰文献投递箱

把论文正文 PDF 和补充材料放进一个文件夹，让正在使用的 Agent 直接生成中文深读笔记和可分享 HTML。

适合环境材料、水处理、污染控制等论文精读工作流。输出重点是实验方法、结果解释、机制链条和后续知识库复用。

## Features

- 只需要 `正文.pdf` 和补充材料即可处理。
- 支持补充材料：`.docx`、`.pdf`、`.txt`、`.md`。
- 可选图片：`图文摘要.jpg`、`图1.jpg`、`图2.jpg` 等；未提供图片时先用 `pdfplumber` 找 PDF 图像与 figure 区域坐标，再用 `pypdfium2` 裁剪真正的图面，抽不到时才渲染含 Fig./Figure/图号的页面兜底。
- 深读笔记把可用图像嵌入 `图文导读` 对应小节，形成原图加中文识读，不写文字版图文导读。
- `全文速览` 以一张自制技术路线图呈现论文结构，按阶段分区、子卡片列要点，替代纯文字表格。
- `文章简介` 是摘要与关键结论合一的单元，决定性数字以粗体或行内代码突出。
- 逐图配有实验卡片，列明观察角度、结论与数据支撑，卡片与该图直接对应。
- 生成无 YAML/frontmatter 的 Markdown。
- 生成同题名 HTML，表格带斑马纹与深色表头，窄屏可横向滚动，` ```svg ` 围栏内的 SVG 原样内嵌，支持打印分页控制，适合直接分享给学生或同事。
- 表格、粗体、斜体、行内代码、代码块、引用、列表均正确渲染，即使 Markdown 渲染库缺失也会自动切到内置渲染器并告警，不会把表格压成一行。
- 无需任何外部模型 API Key：谁在 Agent 里使用，就消耗谁当前会话的 token。
- 自动剔除模型客套开头，例如“好的，遵照您的指示”。
- 附带 Agent skill，可复制到 `.codex/skills` 或 `~/.workbuddy/skills` 后复用，也已按 WorkBuddy 开放平台规范打包，可上架技能市场。

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

## Note Structure

笔记按固定章节顺序撰写，不得增删或调换。

```text
# 中文题目

## 文章简介
## 全文速览
## 图文导读
## 机制链条
## 方法细读
## 分析与思考
## 文章信息
```

- `文章简介` 合并摘要与关键结论。先用一句话给出全文最核心的判断，空行后分二至四段写核心发现，按重要性递减排列。决定性数字或结论用粗体或行内代码标出，其余保持正常字重，不整段加粗。
- `全文速览` 用一张自制技术路线图呈现论文结构，不用表格。第一段是引言所指的科学问题，标注为问题所在。图以 ` ```svg ` 围栏内嵌，`viewBox` 以 `0 0 680 ` 起头，按阶段分区、每阶段配子卡片、阶段间用大箭头连接。
- `图文导读` 逐图展开，每张图一个三级标题，标题下先嵌入图片，写中文识读，再紧跟该图的三列实验卡片。章节标题下直接进入第一张图，不写导语。
- `机制链条` 按环节分述作者提出的因果链条，每环节一段。
- `方法细读` 详写实验与分析步骤，可到操作层面，写明参数、阈值、软件版本。这一节允许比其他节更详细。
- `分析与思考` 写启示、可迁移的方法、值得切入的空白，以及作者明确讨论过的条件限制。
- `文章信息` 用两列表格给出期刊卷期、类型、DOI、通讯作者、第一作者、数据可用性与资助，不写收稿与接收时间。笔记到此结束。

## Formatting Rules

笔记由当前 Agent 撰写，脚本负责渲染。写笔记时遵守以下约定，避免格式塌陷。

- 表格必须写标准 Markdown 表头分隔行，即首行表头、第二行 `|---|---|`，且分隔行列数与表头一致。
- 表格单元格内不要换行，避免裸竖线字符，列数以 2 至 4 列为宜。
- 段落中不要用竖线做分隔符。
- 强调用 `**粗体**`，术语首次出现可用 `*斜体*`，不要整段加粗。段落整段加粗会触发深色强调块样式，只留给真正需要突出的那一两句。
- 全文速览的 SVG 必须整体包在 ` ```svg ` 与 ` ``` ` 之间。
- 输出不含 YAML frontmatter，不加客套开头，不套代码围栏。
- 不写人工核查清单，也不提论文缺什么、补充材料是否在本地、数据是否按需提供这类内容。

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
skill/plateau-paper-inbox
```

to one of the following, depending on the client.

WorkBuddy, user level and available in every project:

```text
C:\Users\<you>\.workbuddy\skills\plateau-paper-inbox
```

Codex:

```text
C:\Users\<you>\.codex\skills\plateau-paper-inbox
```

Then ask the Agent to use 珠峰文献投递箱.

## Publish To SkillHub

Package layout expected by the WorkBuddy open platform:

```text
skills/plateau-paper-inbox/
├── SKILL.md
├── requirements.txt
├── agents/openai.yaml
└── scripts/process_paper_inbox.py
```

Submit at https://open.workbuddy.cn/ and follow the skill documentation at https://open.workbuddy.cn/docs/skill.

## Notes

- This tool does not bypass paywalls or download papers illegally.
- Do not commit API keys, PDFs, or unpublished data.
- In agent-first mode, the current Agent can inspect auto-cropped PDF figure regions when no manual images are provided. Full-page renders are only a fallback for vector-only or hard-to-extract figures.
- If visual assets exist, a finished note should not have a text-only `图文导读`.
- Tables require a standard Markdown header separator row. Without it the renderer falls back to plain text.
