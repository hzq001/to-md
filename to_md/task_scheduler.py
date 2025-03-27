"""
任务调度模块
"""
import os
import time
import concurrent.futures
from typing import Dict, List, Any, Callable, Optional
from tqdm import tqdm
import json

from to_md.conversion_engine import ConversionEngine
from to_md.logger import LogManager


class TaskScheduler:
    """
    任务调度器，负责管理并行任务的创建和执行
    """
    
    def __init__(self, config: Dict[str, Any], 
                conversion_engine: ConversionEngine,
                log_manager: LogManager):
        """
        初始化任务调度器
        
        Args:
            config: 配置字典
            conversion_engine: 转换引擎实例
            log_manager: 日志管理器实例
        """
        self.config = config
        self.conversion_engine = conversion_engine
        self.log_manager = log_manager
        self.completed_files = []
        self.pending_files = []
        self.failed_files = []
        
    def create_task_queue(self, file_list: List[Dict[str, Any]]) -> None:
        """
        创建任务队列
        
        Args:
            file_list: 待处理的文件列表
        """
        self.pending_files = file_list.copy()
        
        # 检查是否有检查点可以恢复
        checkpoint = self.log_manager.load_checkpoint()
        if checkpoint:
            # 从检查点恢复已完成和待处理的文件
            self._restore_from_checkpoint(checkpoint)
        
        # 按文件大小排序，优先处理小文件
        self.pending_files.sort(key=lambda x: x.get('size', 0))
        
    def _restore_from_checkpoint(self, checkpoint: Dict[str, Any]) -> None:
        """
        从检查点恢复状态
        
        Args:
            checkpoint: 检查点数据
        """
        # 获取已完成的文件路径集合
        completed_paths = {f['path'] for f in checkpoint.get('completed', [])}
        
        # 更新已完成和待处理的文件列表
        self.completed_files = [f for f in self.pending_files if f['path'] in completed_paths]
        self.pending_files = [f for f in self.pending_files if f['path'] not in completed_paths]
        
        # 记录恢复情况
        self.log_manager.log_event('info', 
            f"从检查点恢复: 已完成 {len(self.completed_files)} 个文件, 剩余 {len(self.pending_files)} 个文件待处理")
        
    def process_queue(self) -> Dict[str, Any]:
        """
        处理任务队列
        
        Returns:
            处理结果摘要
        """
        # 如果没有待处理的文件，直接返回
        if not self.pending_files:
            self.log_manager.log_event('info', "没有文件需要处理")
            return {"success": 0, "failure": 0, "skipped": 0, "total": 0}
            
        # 记录开始处理
        self.log_manager.log_event('info', 
            f"开始处理 {len(self.pending_files)} 个文件，使用 {self.config['threads']} 个线程")
            
        # 设置进度条
        pbar = tqdm(total=len(self.pending_files), 
                   desc="转换进度", 
                   unit="个文件")
                   
        # 更新已完成的数量
        pbar.update(len(self.completed_files))
        
        # 创建线程池
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.config['threads']) as executor:
            # 提交所有任务
            future_to_file = {
                executor.submit(self._process_file, file_info): file_info 
                for file_info in self.pending_files
            }
            
            # 处理结果
            try:
                for i, future in enumerate(concurrent.futures.as_completed(future_to_file)):
                    file_info = future_to_file[future]
                    
                    try:
                        result = future.result()
                        
                        # 记录结果
                        self.log_manager.log_conversion_result(
                            file_info,
                            result['status'],
                            result.get('message', ''),
                            result.get('duration', 0.0)
                        )
                        
                        # 更新文件状态
                        if result['status'] == 'success':
                            self.completed_files.append(file_info)
                        elif result['status'] == 'failure':
                            self.failed_files.append(file_info)
                            
                        # 更新进度条
                        pbar.update(1)
                        
                        # 定期保存检查点（每处理10个文件或处理了全部文件的5%）
                        if i % 10 == 0 or i % max(1, len(self.pending_files) // 20) == 0:
                            self._save_checkpoint()
                            
                    except Exception as e:
                        # 记录任务执行异常
                        self.log_manager.log_conversion_result(
                            file_info,
                            'failure',
                            f'任务执行异常: {str(e)}'
                        )
                        self.failed_files.append(file_info)
                        pbar.update(1)
            
            except KeyboardInterrupt:
                # 处理用户中断
                self.log_manager.log_event('warning', "用户中断处理")
                # 保存检查点
                self._save_checkpoint()
                # 取消所有未完成的任务
                for future in future_to_file:
                    if not future.done():
                        future.cancel()
            
            finally:
                pbar.close()
                
        # 最后一次保存检查点
        self._save_checkpoint()
        
        # 返回处理结果摘要
        return {
            "success": len(self.completed_files),
            "failure": len(self.failed_files),
            "skipped": 0,
            "total": len(self.pending_files)
        }
        
    def _process_file(self, file_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理单个文件
        
        Args:
            file_info: 文件信息字典
            
        Returns:
            处理结果字典
        """
        # 检查输出文件是否已存在
        if os.path.exists(file_info['output_path']) and not self.config.get('overwrite', False):
            return {
                'file_info': file_info,
                'status': 'skipped',
                'message': '输出文件已存在',
                'duration': 0,
                'output_path': file_info['output_path']
            }
            
        # 实际转换文件
        try:
            return self.conversion_engine.convert_file(file_info)
        except Exception as e:
            # 捕获并记录所有异常
            return {
                'file_info': file_info,
                'status': 'failure',
                'message': f'处理文件时出错: {str(e)}',
                'duration': 0,
                'output_path': None
            }
            
    def _save_checkpoint(self) -> None:
        """
        保存检查点
        """
        self.log_manager.save_checkpoint(self.completed_files, self.pending_files)
        
    def track_progress(self) -> Dict[str, Any]:
        """
        跟踪处理进度
        
        Returns:
            当前进度信息
        """
        total = len(self.pending_files) + len(self.completed_files) + len(self.failed_files)
        return {
            'total': total,
            'completed': len(self.completed_files),
            'pending': len(self.pending_files),
            'failed': len(self.failed_files),
            'progress': len(self.completed_files) / total if total > 0 else 0
        } 