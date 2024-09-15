# 测试背景的copy
# 成功

import pygame
import sys

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
BOARD_COLOR = (221, 182, 116)

class Background_Test:
    def __init__(self, board_dimension = 19, cell_edge_len = 40) -> None:
        
        # 基本量
        self.board_dimension = board_dimension                                                  # 路数
        self.cell_edge_len = cell_edge_len                                                      # 格宽
        self.board_width = self.board_height = (self.board_dimension - 1) * self.cell_edge_len  # 棋盘宽、高
        self.border_len = cell_edge_len                                                         # 边界宽度
        self.display_width = self.board_width + 2 * self.border_len                             # 游戏界面宽度
        self.display_height = self.board_height + 2 * self.border_len + self.border_len         # 游戏界面高度
        
        # 前端初始化棋盘
        pygame.init()
        pygame.display.set_caption("GO") # 
        self.screen = pygame.display.set_mode((self.display_width, self.display_height))
        self.font = pygame.font.Font(None, 36)
        
        # 测试部分，测试Surface使用方法
        self.draw_board()
        self.background = self.screen.copy()
        
    
    # 用已保存的背景覆盖原有画面
    def load_background(self):
        # 使用保存的背景覆盖棋盘
        self.screen.blit(self.background, (0, 0))
        
    # 前端绘制棋盘
    def draw_board(self):

        self.screen.fill(BOARD_COLOR)

        # 绘制提示点
        pygame.draw.circle(self.screen, BLACK, (4 * self.cell_edge_len, 4 * self.cell_edge_len), 5)
        pygame.draw.circle(self.screen, BLACK, (16 * self.cell_edge_len, 4 * self.cell_edge_len), 5)
        pygame.draw.circle(self.screen, BLACK, (4 * self.cell_edge_len, 16 * self.cell_edge_len), 5)
        pygame.draw.circle(self.screen, BLACK, (16 * self.cell_edge_len, 16 * self.cell_edge_len), 5)
        pygame.draw.circle(self.screen, BLACK, (4 * self.cell_edge_len, 10 * self.cell_edge_len), 5)
        pygame.draw.circle(self.screen, BLACK, (10 * self.cell_edge_len, 4 * self.cell_edge_len), 5)
        pygame.draw.circle(self.screen, BLACK, (10 * self.cell_edge_len, 10 * self.cell_edge_len), 5)
        pygame.draw.circle(self.screen, BLACK, (10 * self.cell_edge_len, 16 * self.cell_edge_len), 5)
        pygame.draw.circle(self.screen, BLACK, (16 * self.cell_edge_len, 10 * self.cell_edge_len), 5)

        # 绘制网格线
        for x in range(1, self.board_dimension + 1):
            pygame.draw.line(self.screen, BLACK, (x * self.cell_edge_len, self.cell_edge_len), (x * self.cell_edge_len, 19 * self.cell_edge_len), 1)
        for y in range(1, self.board_dimension + 1):
            pygame.draw.line(self.screen, BLACK, (self.cell_edge_len, y * self.cell_edge_len), (19 * self.cell_edge_len, y * self.cell_edge_len), 1)
    
if __name__ == "__main__":
    test = Background_Test(board_dimension=19, cell_edge_len=40)
    pygame.init()
    pygame.display.set_caption("test")
    test.screen = pygame.display.set_mode((test.display_width, test.display_height))
    
    while True:

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        
        test.load_background()
        pygame.display.flip()