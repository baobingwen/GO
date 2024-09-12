import pygame
import sys

# 初始化pygame
pygame.init()

# 设置棋盘大小和窗口大小
BOARD_SIZE = 19
WINDOW_SIZE = 600
TILE_SIZE = WINDOW_SIZE // BOARD_SIZE

# 设置颜色
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)

# 创建窗口
screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE))
pygame.display.set_caption("Go Game")

# 初始化棋盘
board = [['.' for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]
current_player = 'B'

def draw_board():
    screen.fill(pygame.Color(50,50,50))
    for x in range(BOARD_SIZE):
        for y in range(BOARD_SIZE):
            pygame.draw.rect(screen, GRAY, (x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE), 1)
            if board[x][y] != '.':
                color = BLACK if board[x][y] == 'B' else WHITE
                # 计算棋子的中心位置，确保它位于网格线的交点上
                center_x = (x) * TILE_SIZE
                center_y = (y) * TILE_SIZE
                pygame.draw.circle(screen, color, (int(center_x), int(center_y)), TILE_SIZE // 2 - 3)

def main():
    global current_player
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Left click
                x, y = event.pos
                x //= TILE_SIZE
                y //= TILE_SIZE
                if 0 <= x < BOARD_SIZE and 0 <= y < BOARD_SIZE and board[x][y] == '.':
                    board[x][y] = current_player
                    current_player = 'W' if current_player == 'B' else 'B'

        draw_board()
        pygame.display.flip()

if __name__ == "__main__":
    main()