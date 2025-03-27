"""
文件扫描器测试模块
"""
import os
import tempfile
import shutil
import pytest
from to_md.file_scanner import FileScanner
from to_md.config import ConfigManager


class TestFileScanner:
    """
    文件扫描器测试类
    """
    
    @pytest.fixture
    def temp_dir(self):
        """
        创建临时目录结构用于测试
        """
        # 创建临时源目录
        source_dir = tempfile.mkdtemp()
        
        try:
            # 创建子目录
            subdir1 = os.path.join(source_dir, "subdir1")
            subdir2 = os.path.join(source_dir, "subdir2")
            os.makedirs(subdir1)
            os.makedirs(subdir2)
            
            # 创建测试文件
            with open(os.path.join(source_dir, "test1.txt"), "w") as f:
                f.write("test file 1")
                
            with open(os.path.join(source_dir, "test2.pdf"), "w") as f:
                f.write("test file 2")
                
            with open(os.path.join(subdir1, "test3.docx"), "w") as f:
                f.write("test file 3")
                
            with open(os.path.join(subdir2, "test4.pptx"), "w") as f:
                f.write("test file 4")
                
            yield source_dir
            
        finally:
            # 清理临时目录
            shutil.rmtree(source_dir)
            
    def test_scan_directory(self, temp_dir):
        """
        测试目录扫描功能
        """
        config = {
            'source_dir': temp_dir,
            'target_dir': os.path.join(temp_dir, 'md_output'),
            'recursive': True,
            'file_types': []
        }
        
        scanner = FileScanner(config)
        files = scanner.scan_directory()
        
        # 应该找到4个文件
        assert len(files) == 4
        
        # 验证文件路径
        file_paths = [f['path'] for f in files]
        assert os.path.join(temp_dir, "test1.txt") in file_paths
        assert os.path.join(temp_dir, "test2.pdf") in file_paths
        assert os.path.join(temp_dir, "subdir1", "test3.docx") in file_paths
        assert os.path.join(temp_dir, "subdir2", "test4.pptx") in file_paths
        
    def test_filter_files(self, temp_dir):
        """
        测试文件过滤功能
        """
        config = {
            'source_dir': temp_dir,
            'target_dir': os.path.join(temp_dir, 'md_output'),
            'recursive': True,
            'file_types': ['pdf', 'docx']
        }
        
        scanner = FileScanner(config)
        files = scanner.scan_directory()
        
        # 应该只找到2个文件 (pdf和docx)
        assert len(files) == 2
        
        # 验证文件类型
        file_types = [f['type'] for f in files]
        assert 'pdf' in file_types
        assert 'docx' in file_types
        assert 'txt' not in file_types
        assert 'pptx' not in file_types
        
    def test_non_recursive(self, temp_dir):
        """
        测试非递归扫描
        """
        config = {
            'source_dir': temp_dir,
            'target_dir': os.path.join(temp_dir, 'md_output'),
            'recursive': False,
            'file_types': []
        }
        
        scanner = FileScanner(config)
        files = scanner.scan_directory()
        
        # 应该只找到2个文件（顶层目录中的文件）
        assert len(files) == 2
        
        # 验证文件路径（只有顶层目录的文件）
        file_paths = [f['path'] for f in files]
        assert os.path.join(temp_dir, "test1.txt") in file_paths
        assert os.path.join(temp_dir, "test2.pdf") in file_paths
        assert not any(p.endswith("test3.docx") for p in file_paths)
        assert not any(p.endswith("test4.pptx") for p in file_paths) 