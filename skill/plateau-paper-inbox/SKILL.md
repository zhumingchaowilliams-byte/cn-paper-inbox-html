---
name: plateau-paper-inbox
display_name: 珠峰文献投递箱
display_name_en: Everest Paper Inbox
description: 珠峰文献投递箱，把论文正文 PDF 与补充材料批量转成结构化的中文深读 Markdown 与可分享 HTML，面向环境材料、水处理与污染控制方向。当需要处理只含正文 PDF 和补充材料的文献文件夹、在图缺失时用 pdfplumber 坐标配合 pypdfium2 自动裁剪 PDF 图区、用当前 Agent 自身 token 生成中文深读笔记、导出排版规范的 HTML、输出不含 YAML frontmatter 的笔记，或把这套流程打包给研究生与协作者使用时调用。触发词：文献投递箱、论文深读、中文精读笔记、PDF 转 HTML、图文导读、批量处理文献、paper inbox。
description_zh: 把论文正文 PDF 与补充材料批量转成中文深读笔记与可分享 HTML，自动抽取并裁出 PDF 图区，生成含技术路线图、逐图实验卡片与方法细读的结构化笔记，无需任何外部模型 API Key。
description_en: Turn paper PDFs and supplementary materials into structured Chinese deep-reading notes and shareable HTML. Figures are extracted and cropped from the PDF automatically, and each note carries a workflow diagram, per-figure evidence tables and a detailed methods section, with no external model API key required.
category: research
version: 1.0.0
author: 朱明超
agent_created: true
---

# 珠峰文献投递箱

把一个文献文件夹转成中文深读笔记与可分享 HTML。正文 PDF 加补充材料即可，无需预先准备图片，也无需要求任何外部模型 API Key。

## 核心理念

当前 Agent 自己读文本包、自己写中文笔记，消耗的是本次会话的 token。脚本只负责确定性的文件准备与收尾，不承担写作，也不调用外部推理服务。

## 最小输入

```text
<inbox>\<paper-folder>\
  正文.pdf
  补充材料.docx / supplementary.pdf / .txt / .md
```

可选手工命名图片：

```text
  图文摘要.jpg
  图1.jpg
  图2.jpg
```

也支持 `supplements\` 与 `figures\` 子目录。未提供图片时，脚本先用 `pdfplumber` 定位 PDF 图像对象与题注引导的图区，再用 `pypdfium2` 裁剪到 `<vault>\Assets\Papers\<doi-safe>\pdf-extracted-images\`。若未识别到可用图区，则回退为渲染含 Fig./Figure/图号的页面到 `pdf-auto-pages\`。

## 工作流程

```bash
python scripts/process_paper_inbox.py --inbox <inbox> --vault <vault> --prepare <folder-name>
```

随后读取 `<vault>\AI Inputs\<doi-safe>.agent_task.md` 与生成的文本包，若存在则查看抽取出的图或回退渲染的图页。由当前 Agent 自己写中文笔记为 Markdown，直接以 `# 标题` 开头，存成临时 `.md`，再收尾：

```bash
python scripts/process_paper_inbox.py --inbox <inbox> --vault <vault> --finalize <folder-name> --generated-md <generated-note.md>
```

`--generated-md` 在 Windows 下必须传原生路径（`C:\...`），不能用 Git Bash 的 `/c/...` 形式，否则会被当作字面量。

辅助命令：

```bash
python scripts/process_paper_inbox.py --inbox <inbox> --vault <vault> --scan
python scripts/process_paper_inbox.py --inbox <inbox> --vault <vault> --refresh-assets <folder-name>
```

## 图表规范

图不是装饰，是深读的必备内容。PDF 类文献必须完成图区抽取与嵌入。

- 写最终 Markdown 前，先查看手工图片、`pdf-extracted-images` 或回退的 `pdf-auto-pages`。
- 在 `图文导读` 中，把每张可用图紧接在其 `Fig. N` / `图N` 标题下方，用 Obsidian 嵌入语法，例如 `![[Assets/Papers/<doi-safe>/图1.png]]`。
- 图片解读写在图片下方，只能依据可见图像加题注与正文，不臆造画面细节。
- 若脚本只产出整页渲染，尽量裁出图区；实在无法裁剪时嵌入整页并标注为回退图页。
- 有视觉素材时，`图文导读` 不得只写文字。

## 排版规范

脚本会把 Markdown 渲染为 HTML。表格、粗体、斜体、行内代码、代码块、引用、列表都会被正确解析，表格带斑马纹与深色表头，窄屏可横向滚动，宽表格不会被压扁。` ```svg ` 代码围栏内的 SVG 会原样内嵌进页面，不会被转义。

写笔记时遵守以下约定，避免格式塌陷。

- 表格必须写标准的 Markdown 表头分隔行，即首行表头、第二行 `|---|---|`，否则不会被识别为表格。分隔行列数要与表头一致。
- 表格单元格内不要换行，长内容用短句分段表达，或拆成多行表格。
- 单元格内避免出现裸的竖线字符，需要时用顿号或分号替代。
- 表格列数以 2 至 4 列为宜，超过 5 列在窄屏上可读性会明显下降。
- 段落中不要用竖线做分隔符，改用标点或换行。
- 强调用 `**粗体**`，术语首次出现可用 `*斜体*`，但不要整段加粗。段落整段加粗会触发深色强调块样式，只留给真正需要突出的那一两句。
- 全文速览的 SVG 必须整体包在 ` ```svg ` 与 ` ``` ` 之间，围栏外不要写任何标签或图注文字。
- 输出不含 YAML frontmatter 与笔记属性。
- 不要在笔记前后添加“好的，遵照您的指示”“以下是”之类的客套开头，也不要给笔记套代码围栏。
- 把补充材料当作方法学、表征细节、实验条件与对照组的核心证据。

## 笔记结构

笔记按固定章节顺序撰写，不得增删或调换顺序。

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

各章节内容要求如下。

**文章简介** 是摘要与关键结论合一的单元，不要拆成两节。先用一句话给出全文最核心的判断，自然带出研究涉及的关键概念、方法名与研究对象，再空行分二至四段写核心发现，每段只说一件事，按重要性递减排列。决定性的一两个数字或结论用 `**粗体**` 或行内代码标出，其余保持正常字重。不要把整段写成粗体，渲染后整段变深色块，主次全失。

**全文速览** 用一张自制流程/技术路线图呈现论文自身的结构脉络，替代表格。第一段必须是引言所指的问题，即这篇文章要回答的科学问题，标注为问题所在。图用 ` ```svg ` 代码围栏内嵌，不要写成图片文件引用，也不要存成表格。

图的设计要求：`viewBox` 以 `0 0 680 ` 起头，横向展开；按论文结构分三至六个阶段，从左到右推进；每个阶段一个实心圆角色块，配色区分，阶段内子项用小卡片列出；相关阶段可用虚线框归并；阶段之间用一个大箭头连接，箭头是主要视觉引导。中文标注字号不低于 13px，图内不写冗余说明文字。可以标注关键数字，例如样本量、河流条数、关键阈值，但不要复述结论。

**图文导读** 逐图展开，每张图一个三级标题 `### 图 N 图题`。标题下先嵌入图片，紧接图片写中文识读，再紧接该图对应的关键实验卡片。卡片必须与这张图直接相关，写成本图的数据支撑表，列固定为三列，分别是观察角度、结论、数据支撑。章节标题下直接进入第一张图，不写导语、串讲或背景交代。

**机制链条** 按环节分述作者提出的因果链条，每环节一段，用 `**环节名。**` 起头。只写论文支持或明确推断的环节，不做超出原文的延伸。

**方法细读** 详写实验与分析步骤，可以到操作层面。按流程顺序分段，每段用 `**小标题。**` 起头，写明具体参数、阈值、软件版本与依赖关系。这一节允许且鼓励比其他节更详细。

**分析与思考** 写这篇论文对本方向工作的启示、可迁移的方法、值得切入的空白以及作者明确讨论过的条件限制。不写文献综述层面的证据支撑关系，不出现“可以作为综述的支撑”“可以纳入某一节”这类表述。落点在具体判断与可执行想法上。

**分析与思考里不谈数据缺失。** 不写论文未提供什么、正文引用了哪张补充图、哪个材料不在本地、数据按需提供、脚本托管情况、需要回头核对数字这类内容。作者本人在正文中明确讨论过的研究条件限制（例如单季节采样）可以写，但只讲这一条件对结论适用范围的影响，不涉及资料获取。

**文章信息** 放在正文之后，用两列表格给出期刊卷期、类型、DOI、通讯作者、第一作者、数据可用性、分析脚本与资助信息。不写收稿与接收时间。

不写人工核查清单。笔记到文章信息即结束。

不要输出图片资产的清单章节，脚本已自动处理图区，无需在笔记里另列。

## 输出物

```text
<vault>\Knowledge\Paper Deep Readings\<title>.md
<vault>\Knowledge\Paper Deep Readings HTML\<title>.html
<vault>\AI Inputs\<doi-safe>.paper_text_packet.md
<vault>\AI Inputs\<doi-safe>.agent_task.md
<vault>\AI Outputs\<doi-safe>.run_log.md
<paper-folder>\处理状态.json
<paper-folder>\处理结果.md
```

若 DOI 抽取失败，文件夹标记为 `needs_review`，不得假装引用信息完整。

## 默认路径

```text
inbox: <current directory>\paper
vault: <current directory>\vault
```

实际使用时建议显式传入 `--inbox` 与 `--vault`。

## 依赖

```bash
pip install -r requirements.txt
```

含 pypdf、pdfplumber、python-docx、Pillow、Markdown、pypdfium2。PySide6 仅桌面版界面需要，命令行流程不必安装。

若 HTML 中表格被压成一行纯文本，说明 `Markdown` 包不完整，执行 `pip install --force-reinstall Markdown` 修复。脚本检测到库异常时会向 stderr 输出警告，并自动切换到内置渲染器。

## 边界

不绕过付费墙，不下载文献。不要把 API Key、PDF 或未发表数据提交到仓库。
