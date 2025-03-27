"""
转换引擎模块
"""
import os
import time
import tempfile
from typing import Dict, Any, Optional, List, Tuple
import json
import importlib

# 检查markitdown库是否可用
try:
    import markitdown
    MARKITDOWN_AVAILABLE = True
except ImportError:
    MARKITDOWN_AVAILABLE = False
    print("警告: markitdown库未安装，将使用模拟转换")


class ConversionEngine:
    """
    转换引擎类，负责调用MarkItDown API进行文件转换
    """
    def __init__(self, config: Dict[str, Any]):
        """
        初始化转换引擎
        
        Args:
            config: 配置字典
        """
        self.config = config
        self.markitdown = None
        self.plugins = []
        self.initialize_markitdown()
        
    def initialize_markitdown(self) -> None:
        """
        初始化MarkItDown库
        """
        if not MARKITDOWN_AVAILABLE:
            print("警告: markitdown库未安装，将使用模拟转换")
            return
            
        try:
            # 初始化MarkItDown实例
            self.markitdown = markitdown.MarkItDown()
            
            # 如果配置了Azure文档智能端点，设置它
            if self.config.get('docintel_endpoint'):
                self.markitdown.configure({
                    'azure_document_intelligence_endpoint': self.config['docintel_endpoint']
                })
                
            # 如果启用了插件，加载并配置
            if self.config.get('use_plugins', False):
                self._load_plugins()
                
        except Exception as e:
            print(f"初始化MarkItDown失败: {e}")
            self.markitdown = None
            
    def _load_plugins(self) -> None:
        """
        加载MarkItDown插件
        """
        # 这里应该根据实际的MarkItDown插件加载机制实现
        # 由于当前没有具体的插件信息，这里只是一个示例实现
        pass
            
    def convert_file(self, file_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        转换单个文件
        
        Args:
            file_info: 文件信息字典
            
        Returns:
            转换结果字典
        """
        # 记录开始时间
        start_time = time.time()
        
        # 如果是模拟运行，不执行实际转换
        if self.config.get('dry_run', False):
            # 等待一小段时间以模拟处理
            time.sleep(0.5)
            return {
                'file_info': file_info,
                'status': 'success',
                'message': '[模拟] 文件已成功转换',
                'duration': time.time() - start_time,
                'output_path': file_info['output_path']
            }
            
        # 如果MarkItDown未初始化，使用模拟转换
        if not self.markitdown:
            return self._mock_convert_file(file_info)
            
        # 执行实际转换
        try:
            # 确保输出目录存在
            os.makedirs(os.path.dirname(file_info['output_path']), exist_ok=True)
            
            # 调用MarkItDown库进行转换
            result = self.markitdown.convert(
                file_info['path'],
                output_path=file_info['output_path']
            )
            
            # 处理转换结果
            if result and os.path.exists(file_info['output_path']):
                return {
                    'file_info': file_info,
                    'status': 'success',
                    'message': '文件已成功转换',
                    'duration': time.time() - start_time,
                    'output_path': file_info['output_path']
                }
            else:
                return {
                    'file_info': file_info,
                    'status': 'failure',
                    'message': '转换失败，未生成输出文件',
                    'duration': time.time() - start_time,
                    'output_path': None
                }
                
        except Exception as e:
            # 记录错误并返回失败状态
            return {
                'file_info': file_info,
                'status': 'failure',
                'message': f'转换过程中出错: {str(e)}',
                'duration': time.time() - start_time,
                'output_path': None
            }
            
    def _mock_convert_file(self, file_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        模拟文件转换，用于测试或MarkItDown不可用时
        
        Args:
            file_info: 文件信息字典
            
        Returns:
            转换结果字典
        """
        # 记录开始时间
        start_time = time.time()
        
        try:
            # 创建输出目录
            os.makedirs(os.path.dirname(file_info['output_path']), exist_ok=True)
            
            # 创建一个简单的Markdown内容
            md_content = f"""# {os.path.basename(file_info['path'])}

## 文件信息

- 原始文件: {file_info['path']}
- 文件类型: {file_info.get('type', '未知')}
- 文件大小: {file_info.get('size', 0)} 字节
- MIME类型: {file_info.get('mime_type', '未知')}

## 内容

这是一个模拟转换的Markdown文件。在实际使用中，这里会包含从原始文件提取的内容。

*注意: 这是由to-md工具模拟转换生成的文件，未使用实际的MarkItDown库。*
"""
            
            # 写入输出文件
            with open(file_info['output_path'], 'w', encoding='utf-8') as f:
                f.write(md_content)
                
            # 添加一些随机延迟以模拟处理时间
            time.sleep(0.5 + (file_info.get('size', 0) % 1000) / 1000)
            
            return {
                'file_info': file_info,
                'status': 'success',
                'message': '[模拟] 文件已成功转换',
                'duration': time.time() - start_time,
                'output_path': file_info['output_path']
            }
            
        except Exception as e:
            # 记录错误并返回失败状态
            return {
                'file_info': file_info,
                'status': 'failure',
                'message': f'[模拟] 转换过程中出错: {str(e)}',
                'duration': time.time() - start_time,
                'output_path': None
            }
            
    def get_supported_formats(self) -> List[str]:
        """
        获取支持的文件格式列表
        
        Returns:
            支持的文件格式列表
        """
        if not self.markitdown:
            # 如果MarkItDown不可用，返回常见格式
            return ["pdf", "doc", "docx", "ppt", "pptx", "xls", "xlsx", 
                    "txt", "html", "htm", "jpg", "jpeg", "png", "mp3", 
                    "mp4", "epub", "zip"]
        
        # 调用MarkItDown获取支持的格式
        try:
            return self.markitdown.get_supported_formats()
        except Exception as e:
            print(f"获取支持的格式失败: {e}")
            return []
            
    def save_result(self, result: Dict[str, Any], output_path: str = None) -> bool:
        """
        保存转换结果
        
        Args:
            result: 转换结果字典
            output_path: 输出路径，如果为None则使用file_info中的output_path
            
        Returns:
            是否成功保存
        """
        if result['status'] != 'success':
            return False
            
        if not output_path:
            output_path = result['file_info']['output_path']
            
        # 如果已经成功保存，不需要再保存
        if os.path.exists(output_path):
            return True
            
        # 如果有转换结果但还没保存，进行保存
        try:
            # 确保输出目录存在
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # 不同情况下的保存逻辑
            # 如果结果包含内容，写入文件
            if 'content' in result:
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(result['content'])
                return True
                
            # 如果结果包含临时文件，复制文件
            elif 'temp_file' in result and os.path.exists(result['temp_file']):
                import shutil
                shutil.copy2(result['temp_file'], output_path)
                return True
                
            return False
            
        except Exception as e:
            print(f"保存结果失败: {e}")
            return False 