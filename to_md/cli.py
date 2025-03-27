"""
命令行接口模块
"""
import os
import sys
import time
import click
from typing import Dict, List, Any

from to_md.config import ConfigManager, ConfigurationError
from to_md.logger import LogManager
from to_md.file_scanner import FileScanner
from to_md.conversion_engine import ConversionEngine
from to_md.task_scheduler import TaskScheduler


@click.command()
@click.argument('source_dir', type=click.Path(exists=True, file_okay=False, dir_okay=True))
@click.argument('target_dir', type=click.Path(), required=False)
@click.option('-r', '--recursive', is_flag=True, default=True, 
              help='递归处理子目录（默认启用）')
@click.option('-f', '--file-types', type=str, default='',
              help='指定要处理的文件类型列表（如pdf,docx,pptx）')
@click.option('-p', '--use-plugins', is_flag=True, default=False,
              help='启用MarkItDown插件')
@click.option('-t', '--threads', type=int, default=4,
              help='并行处理的线程数（默认: 4）')
@click.option('-v', '--verbose', is_flag=True, default=False,
              help='显示详细日志')
@click.option('--docintel-endpoint', type=str, default='',
              help='Azure文档智能服务端点')
@click.option('--dry-run', is_flag=True, default=False,
              help='模拟运行，不实际转换文件')
@click.option('--overwrite', is_flag=True, default=False,
              help='覆盖已存在的目标文件')
def main(source_dir: str, target_dir: str, **options):
    """
    to-md: 批量文件转Markdown工具
    
    参数:
    \b
    SOURCE_DIR  源目录路径
    TARGET_DIR  目标目录路径（可选，默认为源目录下的md_output目录）
    """
    # 开始计时
    start_time = time.time()
    
    try:
        # 合并参数
        cli_args = {
            'source_dir': source_dir,
            'target_dir': target_dir,
            **options
        }
        
        # 初始化配置
        config_manager = ConfigManager(cli_args)
        config = config_manager.get_config()
        
        # 初始化日志管理器
        log_manager = LogManager(config)
        
        # 初始化文件扫描器
        file_scanner = FileScanner(config)
        
        # 创建输出目录结构
        file_scanner.create_output_directories()
        
        # 初始化转换引擎
        conversion_engine = ConversionEngine(config)
        
        # 扫描文件
        log_manager.log_event('info', f"正在扫描目录: {config['source_dir']}")
        files = file_scanner.scan_directory()
        
        # 在日志中显示文件数量
        total_files = len(files)
        log_manager.log_event('info', f"找到 {total_files} 个文件需要处理")
        
        if total_files == 0:
            log_manager.log_event('warning', "没有找到符合条件的文件，程序将退出")
            return
            
        # 模拟运行时显示提示
        if config['dry_run']:
            log_manager.log_event('info', "注意: 这是模拟运行，不会实际转换文件")
            
        # 初始化任务调度器
        task_scheduler = TaskScheduler(config, conversion_engine, log_manager)
        
        # 创建任务队列
        task_scheduler.create_task_queue(files)
        
        # 处理队列
        task_scheduler.process_queue()
        
        # 生成报告
        report = log_manager.generate_report()
        
        # 显示总耗时
        elapsed_time = time.time() - start_time
        log_manager.log_event('info', f"总耗时: {elapsed_time:.2f} 秒")
        
    except ConfigurationError as e:
        # 配置错误
        click.echo(f"配置错误: {str(e)}", err=True)
        sys.exit(1)
    except KeyboardInterrupt:
        # 用户中断
        click.echo("\n程序被用户中断", err=True)
        sys.exit(130)
    except Exception as e:
        # 未预期的错误
        click.echo(f"错误: {str(e)}", err=True)
        if 'verbose' in options and options['verbose']:
            import traceback
            click.echo(traceback.format_exc(), err=True)
        sys.exit(1)
        
if __name__ == '__main__':
    main() 