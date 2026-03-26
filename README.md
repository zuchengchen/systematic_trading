# Systematic Trading LaTeX Translation Project

本仓库用于整理 Robert Carver 所著 *Systematic Trading* 的可编辑 XeLaTeX 工程，并维护两个版本的排版结果：

- `main.tex`: 英文重排版
- `main_bilingual.tex`: 中英双语对照版

项目目标不是保存一份 OCR 文本，而是将原书重建为结构化、可维护、可继续编辑的 LaTeX 项目，便于后续校对、翻译和排版迭代。

## 目录结构

- `chapters/`: 英文版章节源码
- `chapters_bilingual/`: 双语版章节源码
- `figures/raw/`: 从原始 PDF 提取的图片资源
- `extracted/`: 从原始 PDF 提取的文本布局和图片清单等中间文件
- `scripts/extract_assets.sh`: 从原始 PDF 提取文本与图片资源
- `scripts/generate_remaining_tex.py`: 基于提取结果生成部分章节 LaTeX 文件
- `main.tex`: 英文版主入口
- `main_bilingual.tex`: 双语版主入口

## 环境要求

建议使用包含以下工具的 TeX 发行版：

- `latexmk`
- `xelatex`
- `xeCJK`
- `fontspec`

双语版编译时会优先使用以下中文字体之一：

- `Noto Serif CJK SC`
- `Source Han Serif SC`
- `FandolSong-Regular`

如果系统缺少前两者，模板会自动回退到 `FandolSong-Regular`。

此外，资源提取脚本依赖 Poppler 工具：

- `pdfinfo`
- `pdftotext`
- `pdfimages`

## 编译

生成英文版：

```bash
latexmk -xelatex main.tex
```

生成双语版：

```bash
latexmk -xelatex main_bilingual.tex
```

清理中间文件：

```bash
latexmk -c main.tex
latexmk -c main_bilingual.tex
```

生成的 `main.pdf` 和 `main_bilingual.pdf` 默认不纳入 Git 跟踪。

## 资源提取与再生成

如果需要从原始 PDF 重新提取文本和图片，请先将源文件放在仓库根目录，并保持以下文件名：

```text
Systematic Trading A unique new method for designing trading and investing systems-Robert.pdf
```

然后执行：

```bash
bash scripts/extract_assets.sh
python3 scripts/generate_remaining_tex.py
```

其中：

- `extract_assets.sh` 会生成 `extracted/` 下的文本布局、元数据和图片清单，并将图片导出到 `figures/raw/`
- `generate_remaining_tex.py` 会基于提取出的布局文本重建部分 `chapters/*.tex`

执行脚本前请注意，生成脚本会覆盖其负责输出的章节文件，因此修改前最好先确认差异。

## 协作说明

- 仓库已忽略 LaTeX 编译产物、Python 缓存和本地原始 PDF
- 日常编辑以 `chapters/` 和 `chapters_bilingual/` 为主
- 如果只调整翻译或排版，通常不需要重新运行提取脚本
- 建议在提交前至少重新编译一次目标版本，确认目录、页眉、图片和中英排版正常

## 版权说明

本项目包含基于原书内容的重排版与翻译整理材料。原书版权归原作者及其版权方所有。使用、分享或公开发布本仓库内容前，请自行确认是否具备相应授权与合规条件。
