"""
异常处理模块
"""

class ToMdError(Exception):
    """基础异常类"""
    pass

class ConfigurationError(ToMdError):
    """配置错误"""
    pass

class FileAccessError(ToMdError):
    """文件访问错误"""
    pass

class ConversionError(ToMdError):
    """转换过程错误"""
    pass 