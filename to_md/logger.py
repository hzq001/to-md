"""
日志管理模块
"""
import os
import logging
import json
from datetime import datetime
from typing import Dict, Any, List, Optional

# 设置彩色日志
import colorama
colorama.init()

class LogManager:
    """
    日志管理类，负责处理系统日志和转换结果记录
    """
    def __init__(self, config: Dict[str, Any]):
        """
        初始化日志管理器
        
        Args:
            config: 配置字典
        """
        self.config = config
        self.logger = logging.getLogger('to-md')
        self.results = []
        self.configure_logging()
        
    def configure_logging(self) -> None:
        """
        配置日志系统
        """
        # 清除现有的处理器
        for handler in self.logger.handlers[:]:
            self.logger.removeHandler(handler)
            
        # 设置日志级别
        level = logging.DEBUG if self.config.get('verbose', False) else logging.INFO
        self.logger.setLevel(level)
        
        # 创建控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)
        
        # 设置格式
        if self.config.get('verbose', False):
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        else:
            formatter = logging.Formatter('%(message)s')
            
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
        
        # 如果需要，添加文件处理器
        log_dir = os.path.join(self.config['target_dir'], 'logs')
        os.makedirs(log_dir, exist_ok=True)
        
        file_handler = logging.FileHandler(
            os.path.join(log_dir, f"to-md_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
        )
        file_handler.setLevel(logging.DEBUG)  # 文件日志总是使用DEBUG级别
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        ))
        self.logger.addHandler(file_handler)
        
    def log_event(self, level: str, message: str) -> None:
        """
        记录日志事件
        
        Args:
            level: 日志级别 ('debug', 'info', 'warning', 'error', 'critical')
            message: 日志消息
        """
        level_methods = {
            'debug': self.logger.debug,
            'info': self.logger.info,
            'warning': self.logger.warning,
            'error': self.logger.error,
            'critical': self.logger.critical
        }
        
        if level.lower() in level_methods:
            level_methods[level.lower()](message)
        else:
            self.logger.info(message)
            
    def log_conversion_result(self, file_info: Dict[str, Any], 
                             status: str, 
                             details: str = '',
                             duration: float = 0.0) -> None:
        """
        记录文件转换结果
        
        Args:
            file_info: 文件信息字典
            status: 转换状态 ('success', 'failure', 'skipped')
            details: 详细信息或错误消息
            duration: 转换耗时(秒)
        """
        result = {
            'file_info': file_info,
            'status': status,
            'message': details,
            'duration': duration,
            'timestamp': datetime.now().isoformat()
        }
        
        self.results.append(result)
        
        # 根据状态使用不同的日志级别
        if status == 'success':
            self.logger.info(f"✅ 成功: {file_info['path']} -> {file_info.get('output_path', '')} ({duration:.2f}s)")
        elif status == 'failure':
            self.logger.error(f"❌ 失败: {file_info['path']} - {details}")
        elif status == 'skipped':
            self.logger.warning(f"⏭ 跳过: {file_info['path']} - {details}")
            
    def generate_report(self) -> Dict[str, Any]:
        """
        生成转换报告
        
        Returns:
            报告字典
        """
        # 统计数据
        total = len(self.results)
        success_count = sum(1 for r in self.results if r['status'] == 'success')
        failure_count = sum(1 for r in self.results if r['status'] == 'failure')
        skipped_count = sum(1 for r in self.results if r['status'] == 'skipped')
        
        # 计算总耗时
        total_duration = sum(r['duration'] for r in self.results)
        
        report = {
            'summary': {
                'total': total,
                'success': success_count,
                'failure': failure_count,
                'skipped': skipped_count,
                'total_duration': total_duration
            },
            'results': self.results,
            'timestamp': datetime.now().isoformat()
        }
        
        # 将报告保存到文件
        report_dir = os.path.join(self.config['target_dir'], 'logs')
        os.makedirs(report_dir, exist_ok=True)
        
        report_path = os.path.join(
            report_dir, 
            f"to-md_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
            
        # 在控制台显示摘要
        self.logger.info("\n转换摘要:")
        self.logger.info(f"总文件数: {total}")
        self.logger.info(f"成功: {success_count}")
        self.logger.info(f"失败: {failure_count}")
        self.logger.info(f"跳过: {skipped_count}")
        self.logger.info(f"总耗时: {total_duration:.2f}秒")
        self.logger.info(f"报告已保存至: {report_path}")
        
        return report
            
    def save_checkpoint(self, completed_files: List[Dict[str, Any]], 
                       pending_files: List[Dict[str, Any]]) -> None:
        """
        保存检查点，用于断点续传
        
        Args:
            completed_files: 已完成的文件列表
            pending_files: 待处理的文件列表
        """
        checkpoint = {
            'timestamp': datetime.now().isoformat(),
            'completed': completed_files,
            'pending': pending_files
        }
        
        with open(self.config['checkpoint_file'], 'w', encoding='utf-8') as f:
            json.dump(checkpoint, f, ensure_ascii=False)
            
    def load_checkpoint(self) -> Optional[Dict[str, Any]]:
        """
        加载检查点
        
        Returns:
            检查点数据字典，如果不存在返回None
        """
        if os.path.exists(self.config['checkpoint_file']):
            try:
                with open(self.config['checkpoint_file'], 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                self.logger.warning(f"加载检查点文件失败: {e}")
                
        return None 