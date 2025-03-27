# 使用Conda安装to-md工具及其依赖

## 1. Conda环境准备

### 1.1 安装Conda

如果尚未安装Conda，请先从[Anaconda官网](https://www.anaconda.com/products/distribution)或[Miniconda官网](https://docs.conda.io/en/latest/miniconda.html)下载并安装Conda。

### 1.2 创建专用环境

建议为to-md工具创建独立的Conda环境，以避免与其他项目的依赖冲突：

```bash
# 创建名为to-md的环境，指定Python版本为3.8
conda create -n to-md python=3.8
```

### 1.3 激活环境

```bash
# 在Linux/macOS中
conda activate to-md

# 在Windows中
conda activate to-md
```

## 2. 安装依赖

### 2.1 安装必要依赖

使用conda和pip结合的方式安装依赖：

```bash
# 安装主要依赖（conda可以安装的部分）
conda install -c conda-forge colorama tqdm pytest

# 安装click库
conda install -c conda-forge click
```

### 2.2 安装markitdown库

markitdown库目前可能不在conda仓库中，需要使用pip安装：

```bash
pip install markitdown
```

如果markitdown库安装失败，to-md工具将使用模拟转换模式，仍然可以运行，但功能会受限。

## 3. 安装to-md工具

### 3.1 从PyPI安装

激活conda环境后，使用pip安装to-md：

```bash
pip install to-md
```

### 3.2 从源码安装

或者从源码安装（开发模式）：

```bash
# 克隆仓库
git clone https://github.com/yourusername/to-md.git
cd to-md

# 安装到当前conda环境
pip install -e .
```

## 4. 验证安装

安装完成后，验证to-md工具是否可用：

```bash
# 查看帮助信息
to-md --help
```

应该显示to-md工具的帮助信息，包括可用选项和参数说明。

## 5. 配置环境变量（可选）

如果想在任何目录都能使用to-md命令，确保conda环境的bin目录在PATH环境变量中：

```bash
# 将conda环境的bin目录添加到PATH（Linux/macOS）
echo 'export PATH="$HOME/anaconda3/envs/to-md/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc

# 对于Windows，conda通常会自动处理PATH
```

## 6. 开发环境配置

如果需要进行to-md工具的开发或扩展，安装额外的开发依赖：

```bash
# 安装开发工具
conda install -c conda-forge pytest pytest-cov black isort mypy
```

## 7. 常见问题与解决方案

### 7.1 conda与pip混合使用的注意事项

- 优先使用conda安装依赖，只在conda没有提供包时使用pip
- 先安装conda包，再安装pip包，避免依赖冲突
- 如果遇到依赖冲突，可以尝试创建新的conda环境重新安装

### 7.2 markitdown库不可用

如果markitdown库不可用，to-md会自动降级为模拟模式。如需使用完整功能，请检查markitdown库的安装状态：

```bash
# 检查markitdown是否已安装
pip list | grep markitdown
```

### 7.3 conda环境管理

- 查看所有环境：`conda env list`
- 删除环境：`conda env remove -n to-md`
- 克隆环境：`conda create --name to-md-new --clone to-md`

## 8. 使用conda-pack进行环境迁移（可选）

如果需要将配置好的环境迁移到其他机器（无互联网环境），可以使用conda-pack：

```bash
# 安装conda-pack
conda install -c conda-forge conda-pack

# 打包环境
conda pack -n to-md -o to-md-env.tar.gz

# 在目标机器上解压并激活
mkdir -p to-md-env
tar -xzf to-md-env.tar.gz -C to-md-env
source to-md-env/bin/activate  # Linux/macOS
``` 