import sys
import pygame
from config import Config

class Assets:
    def __init__(self):
        self.images = {}
    
    def load_all(self):
        """显式调用加载资源，确保 pygame 已初始化"""
        self.load_images()

    def load_images(self):
        """加载所有图片"""
        for name, path in Config.IMAGE_PATHS.items():
            try:
                self.images[name] = pygame.image.load(str(path))
            except FileNotFoundError:
                print(f"错误：图片 {path} 未找到！")
                sys.exit(1)

# 全局资源实例（但需显式调用 load_all()）
assets = Assets()