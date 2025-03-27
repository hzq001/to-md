"""
文件遍历模块
"""
import os
import pathlib
from typing import Dict, List, Any, Optional, Set
import mimetypes


class FileScanner:
    """
    文件扫描器，负责遍历目录结构并收集文件信息
    """
    def __init__(self, config: Dict[str, Any]):
        """
        初始化文件扫描器
        
        Args:
            config: 配置字典
        """
        self.config = config
        # 确保MIME类型映射表已初始化
        mimetypes.init()
        
    def scan_directory(self, directory: str = None) -> List[Dict[str, Any]]:
        """
        扫描目录收集文件信息
        
        Args:
            directory: 要扫描的目录，如果为None则使用配置中的源目录
            
        Returns:
            文件信息列表
        """
        if directory is None:
            directory = self.config['source_dir']
            
        results = []
        self._scan_directory_recursive(directory, results)
        
        # 如果设置了文件类型过滤，应用过滤器
        if self.config['file_types']:
            results = self.filter_files(results, self.config['file_types'])
            
        return results
        
    def _scan_directory_recursive(self, directory: str, results: List[Dict[str, Any]]) -> None:
        """
        递归遍历目录收集文件信息
        
        Args:
            directory: 当前扫描的目录
            results: 结果列表，用于添加找到的文件
        """
        try:
            for entry in os.scandir(directory):
                if entry.is_file():
                    file_info = self.collect_file_metadata(entry.path)
                    if file_info:
                        results.append(file_info)
                        
                elif entry.is_dir() and self.config['recursive']:
                    # 跳过目标目录，防止重复处理
                    if os.path.abspath(entry.path) != os.path.abspath(self.config['target_dir']):
                        self._scan_directory_recursive(entry.path, results)
        except PermissionError as e:
            # 记录权限错误但继续处理
            print(f"无权访问目录: {directory} - {e}")
        except Exception as e:
            # 记录其他错误但继续处理
            print(f"扫描目录时出错: {directory} - {e}")
            
    def filter_files(self, files: List[Dict[str, Any]], file_types: List[str]) -> List[Dict[str, Any]]:
        """
        根据文件类型过滤文件列表
        
        Args:
            files: 文件信息列表
            file_types: 要保留的文件类型列表
            
        Returns:
            过滤后的文件信息列表
        """
        if not file_types:
            return files
            
        return [file for file in files 
                if file.get('type', '').lower() in file_types or
                   pathlib.Path(file['path']).suffix.lower().lstrip('.') in file_types]
                   
    def collect_file_metadata(self, file_path: str) -> Optional[Dict[str, Any]]:
        """
        收集文件元数据
        
        Args:
            file_path: 文件路径
            
        Returns:
            文件信息字典，如果不应处理该文件则返回None
        """
        try:
            file_stat = os.stat(file_path)
            file_size = file_stat.st_size
            
            # 获取文件类型
            file_type = pathlib.Path(file_path).suffix.lower().lstrip('.')
            mime_type, _ = mimetypes.guess_type(file_path)
            
            # 计算相对路径（相对于源目录）
            rel_path = os.path.relpath(file_path, self.config['source_dir'])
            
            # 确定输出文件路径
            output_path = os.path.join(
                self.config['target_dir'],
                os.path.splitext(rel_path)[0] + '.md'
            )
            
            return {
                'path': file_path,
                'type': file_type,
                'mime_type': mime_type,
                'size': file_size,
                'rel_path': rel_path,
                'output_path': output_path
            }
            
        except (PermissionError, FileNotFoundError, OSError) as e:
            # 记录错误但继续处理其他文件
            print(f"处理文件元数据时出错: {file_path} - {e}")
            return None
            
    def create_output_directories(self) -> None:
        """
        创建输出目录结构
        """
        # 首先创建主输出目录
        os.makedirs(self.config['target_dir'], exist_ok=True)
        
        # 扫描文件并为每个文件的输出创建必要的目录
        files = self.scan_directory()
        directories = set()
        
        for file_info in files:
            output_dir = os.path.dirname(file_info['output_path'])
            directories.add(output_dir)
            
        # 创建所有需要的目录
        for directory in directories:
            os.makedirs(directory, exist_ok=True) 