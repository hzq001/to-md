# to-md: 文件转Markdown工具

一个基于[Microsoft MarkItDown](https://github.com/microsoft/markitdown)的批量文件转换工具，能够将各种格式的文件（如PDF、Word、PowerPoint等）批量转换为Markdown格式。

## 功能特点

- 批量目录处理：自动遍历目录及所有子目录
- 文件格式识别：自动识别支持的文件类型
- 文件格式转换：将识别的文件转换为Markdown格式
- 保留目录结构：转换后的MD文件保持原有的目录结构
- 并行处理：多线程并行处理，提高转换效率
- 断点续传：支持从中断处继续转换

## 安装

```bash
# 从PyPI安装
pip install to-md

# 或者从源码安装
git clone https://github.com/yourusername/to-md.git
cd to-md
pip install -e .
```

## 使用方法

基本用法：

```bash
# 转换单个目录下的所有文件
to-md /path/to/source /path/to/output

# 指定文件类型
to-md -f pdf,docx,pptx /path/to/source /path/to/output

# 启用详细日志
to-md -v /path/to/source /path/to/output

# 设置并行线程数
to-md -t 8 /path/to/source /path/to/output

# 查看帮助
to-md --help
```

## 支持的文件类型

支持MarkItDown库支持的所有文件类型，包括但不限于：

- PDF文件
- Microsoft Office文档（Word、PowerPoint、Excel）
- 图片文件（含OCR和EXIF元数据）
- 音频文件（含语音转文字）
- HTML文件
- 文本文件（CSV、JSON、XML）
- ZIP压缩文件
- EPUB电子书

## 开发

### 环境设置

```bash
# 克隆仓库
git clone https://github.com/yourusername/to-md.git
cd to-md

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate  # Windows

# 安装开发依赖
pip install -e ".[dev]"
```

### 运行测试

```bash
pytest
```

## 许可证

MIT 