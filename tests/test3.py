import pygame
import sys

# 初始化 Pygame
pygame.init()

# 设置窗口
screen = pygame.display.set_mode((640, 480))
pygame.display.set_caption('Button Example')

# 定义按钮
class Button:
    def __init__(self, x, y, width, height, color, text):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
        self.text = text
        self.font = pygame.font.SysFont(None, 36)

    def draw(self, screen):
        # 绘制按钮的矩形
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))
        # 绘制按钮的文本
        text_surf = self.font.render(self.text, True, (255, 255, 255))
        text_rect = text_surf.get_rect(center=(self.x + self.width / 2, self.y + self.height / 2))
        screen.blit(text_surf, text_rect)

    def is_clicked(self, event):
        # 检查鼠标点击是否在按钮上
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.x < event.pos[0] < self.x + self.width and self.y < event.pos[1] < self.y + self.height:
                return True
        return False

# 创建一个按钮实例
button = Button(100, 100, 200, 50, (0, 255, 0), 'Click Me')

# 游戏主循环
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if button.is_clicked(event):
            print("Button clicked!")

    # 填充背景色
    screen.fill((0, 0, 0))
    # 绘制按钮
    button.draw(screen)
    # 更新显示
    pygame.display.flip()

# 退出 Pygame
pygame.quit()
sys.exit()