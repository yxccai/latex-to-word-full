# LaTeX to Word Full

**[English](README.md) | 中文**

> 将 LaTeX 或 Markdown 学术项目转换为真正可编辑、可维护、可验证的 Word 文档：支持原生公式、动态交叉引用、论文三线表、图表排版和逐页格式检查。

[![Agent Skill](https://img.shields.io/badge/Agent%20Skill-ready-6d5dfc?style=for-the-badge)](SKILL.md)
[![输入格式](https://img.shields.io/badge/输入-LaTeX%20%7C%20Markdown-008080?style=flat-square)](SKILL.md)
[![输出格式](https://img.shields.io/badge/输出-可编辑%20DOCX-2b579a?style=flat-square)](SKILL.md)
[![质量检查](https://img.shields.io/badge/QA-渲染%20%2B%20结构检查-16a34a?style=flat-square)](references/visual-qa-checklist.md)

## 为什么需要它？

很多“LaTeX 转 Word”只保留了文字，却丢失了真正的文档功能：公式变成图片、图表编号变成静态文本、交叉引用失效、三线表出现竖线、分页产生大块空白。

这个 skill 面向更完整的转换目标：生成一个可以继续编辑、重新编号、更新引用、检查结构并通过逐页视觉复核的 Word 文件。

## 工作流程

| 1 · 预检 | 2 · 语义建模 | 3 · 生成 | 4 · 验证 |
| --- | --- | --- | --- |
| 检查源文件、标签、图片、引用和资源路径 | 保留标题、段落、公式、图、表和参考文献关系 | 生成可编辑 DOCX、Word 字段、样式和表格 | 导出页面截图，检查布局并验证 OOXML |

## 核心能力

| 内容 | 处理结果 |
| --- | --- |
| 公式 | 优先转换为 Word 原生公式/OMML，不静默转成图片 |
| 标题 | 只使用一种编号来源，避免出现 `4.3. 4.3` |
| 图片 | 保留图片、标题、标签、尺寸和合理分页 |
| 表格 | 生成真正的 Word 表格，支持论文三线表和语义对齐 |
| 交叉引用 | 使用 Word `SEQ`、书签和 `REF` 字段，而不是冻结编号 |
| 文献引用 | 将引用键映射到同一套参考文献编号 |
| 分页 | 检查隐藏的 `keepNext`、`pageBreakBefore` 和图表后异常空白 |
| 质量控制 | 同时进行 DOCX 结构验证和逐页渲染检查 |

## 快速使用

### 作为 Codex/agent skill 使用

```bash
git clone https://github.com/yxccai/latex-to-word-full.git
```

将仓库根目录作为 skill 目录，然后向兼容的 agent 提出：

```text
使用 $latex-to-word-full 将我的 LaTeX 项目转换为功能完整、可编辑的 Word 文档。
请保留公式、图片、表格、文献、交叉引用和分页，并逐页渲染检查最终格式。
```

主要说明位于 [`SKILL.md`](SKILL.md)，其中规定了源文件预检、转换路线选择、模板处理、Word 字段、三线表和最终 QA 流程。

### 单独运行预检和 DOCX 验证脚本

```bash
python scripts/inspect_latex_project.py path/to/main.tex \
  --json-out build/source-inventory.json

python scripts/validate_docx.py build/manuscript.docx --three-line
```

`inspect_latex_project.py` 会检查标题、标签、引用、图片、公式、表格、参考文献键和缺失资源。

`validate_docx.py` 会检查 DOCX 压缩包、图片关系、书签、`REF`/`SEQ` 字段、三线表边框、重复表头和常见结构问题。

## 重点功能

### 动态编号和交叉引用

转换后的图表标题和正文引用采用 Word 字段：

```text
图/表标题编号  →  SEQ Figure / SEQ Table  →  书签
正文交叉引用  →  REF 书签
文献引用      →  REF 参考文献书签
```

因此在 Word 中编辑或调整内容后，可以重新更新编号，而不是继续使用过期的静态数字。如果 Word 尚未自动更新字段，可在最终文件中按 `Ctrl+A`，再按 `F9`。

### 论文三线表

三线表模式会自动设置：

- 顶部粗横线；
- 表头下方较细横线；
- 底部粗横线；
- 不显示竖线和内部网格线；
- 表头和分类列居中；
- 文本左对齐，数字、百分比、分数和 `N/A` 右对齐；
- 跨页时重复表头，并尽量避免短表格被拆开。

加粗不会改变单元格的语义对齐方式，因此加粗数字不会突然偏到另一侧。

### 逐页格式检查

DOCX 能够保存并不代表转换完成。最终流程会渲染 PDF/PNG 并检查：

- 标题或图表编号是否重复；
- 公式、图片、标题和表格边框是否被裁切；
- 图表后是否出现无法解释的大块空白；
- 标题是否孤零零地留在页底；
- 短表格和参考文献条目是否被不合理拆页；
- 字段、图片资源、字体和符号是否正确显示。

详细检查项见[逐页视觉 QA 清单](references/visual-qa-checklist.md)。

## 仓库结构

```text
.
├── README.md                             # English README
├── README.zh-CN.md                       # 中文 README
├── SKILL.md                              # agent 主说明
├── agents/openai.yaml                    # UI 元数据和默认提示词
├── references/
│   ├── source-and-architecture.md        # 源文件解析和转换路线
│   ├── ooxml-fields-and-layout.md        # 字段、书签、表格和分页
│   └── visual-qa-checklist.md            # 渲染与逐页检查
└── scripts/
    ├── inspect_latex_project.py          # 源项目预检
    └── validate_docx.py                  # DOCX 结构验证
```

## 支持的项目类型

- 含有 `\input`、`\include`、`\graphicspath`、图片、表格、公式和 `.bib` 文件的 LaTeX 论文；
- 含有标题、图片、行内/块级公式、管线表格、引用和脚注的 Markdown/Quarto 文档；
- 由语义转换器处理正文，再由自定义 OOXML 逻辑处理 Word 字段、模板样式和特殊表格的混合流程；
- 基于已有 Word 模板转换，或在没有模板时生成统一的论文风格默认样式。

## 诚实的限制

通用转换器无法自动理解所有私有宏和个人排版习惯。因此本 skill 遵循三条原则：

1. 生成前检查导言区、宏定义和资源文件；
2. 对不支持的宏、缺失文件和渲染器限制给出明确报告；
3. 不静默地把可编辑公式、表格或交叉引用替换成截图或冻结文本。

如果需要完全复刻某个人工调好的页边距、字体、行距、编号定义或表格规范，提供一个 Word 模板会显著提高一致性。没有模板时，仍然可以生成规范的论文风格 Word，但应明确记录采用的默认假设。

## 进一步阅读

- [SKILL.md](SKILL.md)：完整的 agent 工作流和转换约束；
- [source-and-architecture.md](references/source-and-architecture.md)：源文件预检、语义模型和路线选择；
- [ooxml-fields-and-layout.md](references/ooxml-fields-and-layout.md)：Word 字段、书签、三线表和分页控制；
- [visual-qa-checklist.md](references/visual-qa-checklist.md)：渲染、截图检查和常见问题修复。
