"""
配置管理模块
"""
import os
from typing import Dict, List, Any, Optional

from to_md.exceptions import ConfigurationError


class ConfigManager:
    """
    配置管理类，负责处理用户配置和默认设置
    """

    def __init__(self, cli_args: Dict[str, Any]):
        """
        初始化配置管理器
        
        Args:
            cli_args: 命令行参数字典
        """
        self.cli_args = cli_args
        self.config = self.load_default_config()
        self.config = self.merge_user_config(cli_args)
        self.validate_config()

    def load_default_config(self) -> Dict[str, Any]:
        """
        加载默认配置
        
        Returns:
            默认配置字典
        """
        return {
            'source_dir': '',
            'target_dir': '',
            'recursive': True,
            'file_types': [],  # 空列表表示支持所有类型
            'use_plugins': False,
            'threads': 4,
            'verbose': False,
            'docintel_endpoint': '',
            'checkpoint_file': '.to_md_checkpoint.json',
            'llm_client': None,  # LLM客户端实例
            'llm_model': '',     # LLM模型名称
            'overwrite': False,  # 是否覆盖已存在的文件
        }

    def merge_user_config(self, user_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        合并用户配置
        
        Args:
            user_config: 用户提供的配置
            
        Returns:
            合并后的配置字典
        """
        config = self.config.copy()
        
        # 更新配置值
        for key, value in user_config.items():
            if key in config and value is not None:
                config[key] = value
        
        # 处理特殊情况
        if 'source_dir' in user_config:
            config['source_dir'] = os.path.abspath(user_config['source_dir'])
        
        if 'target_dir' in user_config:
            # 如果未指定目标目录，默认使用源目录下的"md_output"目录
            if not user_config['target_dir']:
                config['target_dir'] = os.path.join(config['source_dir'], 'md_output')
            else:
                config['target_dir'] = os.path.abspath(user_config['target_dir'])
        
        # 处理文件类型
        if 'file_types' in user_config and isinstance(user_config['file_types'], str):
            if user_config['file_types']:
                config['file_types'] = [ft.strip().lower() for ft in user_config['file_types'].split(',')]
        
        return config

    def validate_config(self) -> None:
        """
        验证配置的有效性
        
        Raises:
            ConfigurationError: 配置无效时抛出
        """
        # 验证源目录存在
        if not self.config['source_dir']:
            raise ConfigurationError("必须指定源目录")
        
        if not os.path.exists(self.config['source_dir']):
            raise ConfigurationError(f"源目录不存在: {self.config['source_dir']}")
        
        if not os.path.isdir(self.config['source_dir']):
            raise ConfigurationError(f"指定的源路径不是目录: {self.config['source_dir']}")
        
        # 验证线程数
        if self.config['threads'] < 1:
            self.config['threads'] = 1
        
        # 验证LLM配置
        if self.config['llm_client'] is not None and not self.config['llm_model']:
            raise ConfigurationError("如果提供了LLM客户端，则必须指定LLM模型名称")
        
        # 验证其他配置项
        # ...

    def get_config(self) -> Dict[str, Any]:
        """
        获取当前配置
        
        Returns:
            当前配置字典
        """
        return self.config
    
    def update_config(self, key: str, value: Any) -> None:
        """
        更新配置值
        
        Args:
            key: 配置键
            value: 配置值
        """
        if key in self.config:
            self.config[key] = value
        else:
            raise ConfigurationError(f"未知的配置键: {key}")


class ConfigurationError(Exception):
    """配置错误异常类"""
    pass 