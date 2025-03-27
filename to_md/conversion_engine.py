"""
转换引擎模块
"""
import os
import time
import tempfile
from typing import Dict, Any, Optional, List, Tuple
import json
import importlib
import sys

# 检查markitdown库是否可用
try:
    from markitdown import MarkItDown
    MARKITDOWN_AVAILABLE = True
except ImportError:
    MARKITDOWN_AVAILABLE = False
    print("错误: markitdown库未安装，请使用 'pip install markitdown[all]~=0.1.0a1' 进行安装")


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
            raise ImportError("markitdown库未安装，请使用 'pip install markitdown[all]~=0.1.0a1' 进行安装")
            
        try:
            # 检查是否启用插件
            enable_plugins = self.config.get('use_plugins', False)
            
            # 初始化MarkItDown实例
            markitdown_kwargs = {'enable_plugins': enable_plugins}
            
            # 如果配置了Azure文档智能端点，设置它
            if self.config.get('docintel_endpoint'):
                markitdown_kwargs['docintel_endpoint'] = self.config['docintel_endpoint']
                
            # 配置LLM客户端（如果有）
            if self.config.get('llm_client') and self.config.get('llm_model'):
                markitdown_kwargs['llm_client'] = self.config['llm_client']
                markitdown_kwargs['llm_model'] = self.config['llm_model']
                
            # 初始化MarkItDown
            self.markitdown = MarkItDown(**markitdown_kwargs)
                
        except Exception as e:
            raise RuntimeError(f"初始化MarkItDown失败: {e}")
            
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
            
        # 执行实际转换
        try:
            # 确保输出目录存在
            os.makedirs(os.path.dirname(file_info['output_path']), exist_ok=True)
            
            # 调用MarkItDown库进行转换
            result = self.markitdown.convert(
                file_info['path']
            )
            
            # 如果转换成功，保存结果到输出文件
            if result and hasattr(result, 'text_content'):
                with open(file_info['output_path'], 'w', encoding='utf-8') as f:
                    f.write(result.text_content)
                    
                return {
                    'file_info': file_info,
                    'status': 'success',
                    'message': '文件已成功转换',
                    'duration': time.time() - start_time,
                    'output_path': file_info['output_path'],
                    'content': result.text_content
                }
            else:
                return {
                    'file_info': file_info,
                    'status': 'failure',
                    'message': '转换失败，未获取到内容',
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
            
    def get_supported_formats(self) -> List[str]:
        """
        获取支持的文件格式列表
        
        Returns:
            支持的文件格式列表
        """
        # 调用MarkItDown获取支持的格式
        try:
            # 在最新版API中，可能需要查看支持的转换器
            # 这里我们假设有一个get_supported_formats方法
            # 如果实际API不同，需要根据实际情况调整
            if hasattr(self.markitdown, 'get_supported_formats'):
                return self.markitdown.get_supported_formats()
            else:
                # 如果没有此方法，返回常见格式
                return ["pdf", "doc", "docx", "ppt", "pptx", "xls", "xlsx", 
                        "txt", "html", "htm", "jpg", "jpeg", "png", "mp3", 
                        "mp4", "epub", "zip"]
        except Exception as e:
            print(f"获取支持的格式失败: {e}")
            return []
    
    def configure_llm(self, llm_client: Any, llm_model: str) -> bool:
        """
        配置LLM客户端，用于增强图像和音频处理
        
        Args:
            llm_client: LLM客户端实例（如OpenAI客户端）
            llm_model: 要使用的LLM模型名称
            
        Returns:
            是否成功配置
        """
        if not self.markitdown:
            raise RuntimeError("MarkItDown未初始化，无法配置LLM")
            
        try:
            # 更新配置
            self.config['llm_client'] = llm_client
            self.config['llm_model'] = llm_model
            
            # 重新初始化MarkItDown
            self.initialize_markitdown()
            return True
        except Exception as e:
            raise RuntimeError(f"配置LLM失败: {e}")
            
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