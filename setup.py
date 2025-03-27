from setuptools import setup, find_packages

setup(
    name="to-md",
    version="0.1.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "markitdown",  # Microsoft MarkItDown库
        "click",       # 命令行界面工具
        "tqdm",        # 进度条
        "colorama",    # 彩色终端输出
    ],
    entry_points={
        "console_scripts": [
            "to-md=to_md.cli:main",
        ],
    },
    python_requires=">=3.8",
    author="Your Name",
    author_email="your.email@example.com",
    description="批量文件转Markdown工具",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/to-md",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
) 