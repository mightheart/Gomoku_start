import pygame

pygame.init()
background_path = "e:/python/python/Gomoku_start-2/models/background1.jpg"
try:
    background_image = pygame.image.load(background_path)
    print("图片加载成功")
except Exception as e:
    print(f"图片加载失败: {e}")