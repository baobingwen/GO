import os
import sys
import pygame
import numpy as np

#os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1' # 隐藏pygame控制台窗口

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
BOARD_COLOR = (221, 182, 116)

TILE_SIZE = 40 # 棋子大小

class Chess_Piece:
    def __init__(self, color, x, y, visible):
        self.color = color
        self.x = x
        self.y = y
        self.visible = visible

    def set_visible(self):
        self.visible = True

    def set_invisible(self):
        self.visible = False

class GO:
    # 初始化
    def __init__(self,board_size=19, tile_size=40):
        
        # 前端初始化棋盘
        self.board_size = board_size

        self.grid_size = self.board_size ** 2

        self.tile_size=tile_size

        self.width = self.height = self.board_size * self.tile_size

        self.border_size = 40

        self.display_width = self.width + self.border_size
        self.display_height = self.height + self.border_size

        pygame.init()
        pygame.display.set_caption("GO")
        self.screen = pygame.display.set_mode((self.display_width, self.display_height))
        self.font = pygame.font.Font(None, 36)
        
        # 绘制棋盘网格和提示点到背景
        self.draw_board()  

        # 保存棋盘的背景
        self.background = pygame.Surface((self.display_width, self.display_height))
        self.background.fill(BOARD_COLOR)
        
        
        # 后端初始化棋盘

        # 20*20的棋盘
        self.board = [['.' for _ in range(0, self.board_size + 2)] for _ in range(0, self.board_size + 2)]
        # 边界一周为既黑又白不可行棋区
        for x in range(self.board_size + 2):
            self.board[x][0] = '*'
            self.board[x][20] = '*'
        for y in range(self.board_size + 2):
            self.board[0][y] = '*'
            self.board[20][y] = '*'

        # 当前棋子颜色
        self.player = 'B'

        # 后端初始化落子顺序记录数据集
        self.move_order_records = ['0']
        self.cur_pos = 0

    # 初始化已访问位置
    def reset_visit(self):
        self.board_is_visited = [[False for _ in range(0, self.board_size + 1)] for _ in range(0, self.board_size + 1)]
    
    # 清空棋盘
    def clear_tiles(self):
        # 使用保存的背景 Surface 覆盖棋盘，清除所有棋子
        self.screen.blit(self.background, (0, 0))
    
    # 前端绘制棋盘
    def draw_board(self):

        self.screen.fill(BOARD_COLOR)

        # 绘制提示点
        pygame.draw.circle(self.screen, BLACK, (4 * self.tile_size, 4 * self.tile_size), 5)
        pygame.draw.circle(self.screen, BLACK, (16 * self.tile_size, 4 * self.tile_size), 5)
        pygame.draw.circle(self.screen, BLACK, (4 * self.tile_size, 16 * self.tile_size), 5)
        pygame.draw.circle(self.screen, BLACK, (16 * self.tile_size, 16 * self.tile_size), 5)
        pygame.draw.circle(self.screen, BLACK, (4 * self.tile_size, 10 * self.tile_size), 5)
        pygame.draw.circle(self.screen, BLACK, (10 * self.tile_size, 4 * self.tile_size), 5)
        pygame.draw.circle(self.screen, BLACK, (10 * self.tile_size, 10 * self.tile_size), 5)
        pygame.draw.circle(self.screen, BLACK, (10 * self.tile_size, 16 * self.tile_size), 5)
        pygame.draw.circle(self.screen, BLACK, (16 * self.tile_size, 10 * self.tile_size), 5)

        # 绘制网格线
        for x in range(1, self.board_size + 1):
            pygame.draw.line(self.screen, BLACK, (x * self.tile_size, self.tile_size), (x * self.tile_size, 19 * self.tile_size), 1)
        for y in range(1, self.board_size + 1):
            pygame.draw.line(self.screen, BLACK, (self.tile_size, y * self.tile_size), (19 * self.tile_size, y * self.tile_size), 1)
    
    # 前端绘制棋子
    def draw_tile(self):
        for x in range(1, self.board_size + 1):
            for y in range(1, self.board_size + 1):
                if self.board[x][y] != '.':
                    
                    # 计算棋子的中心位置，确保它位于网格线的交点上
                    center_x = (x) * self.tile_size
                    center_y = (y) * self.tile_size
                    
                    # 放置单个棋子
                    color = BLACK if self.board[x][y] == 'B' else WHITE
                    
                    

                    pygame.draw.circle(self.screen, color, (int(center_x), int(center_y)), self.tile_size // 2 - 3)

    
    
    # 搜索单个位置看是否可找到出路，另可解释为找到并标记无气的一团死子
    def this_chess_can_exist(self,x,y):
        # 标记这颗子为已访问
        self.board_is_visited[x][y] = True
        #print(self.board_is_visited[x][y], x, y)

        # 判断这颗子有没有气
        if self.board[x-1][y] == '.' or self.board[x][y-1] == '.' or self.board[x+1][y] == '.' or self.board[x][y+1] == '.':
            return True
        
        # 判断这颗子周围的同色子是否全部被访问过
        if not ((self.board[x-1][y] == self.board[x][y] and self.board_is_visited[x-1][y] == False) or (self.board[x+1][y] == self.board[x][y] and self.board_is_visited[x+1][y] == False) or (self.board[x][y-1] == self.board[x][y] and self.board_is_visited[x][y-1] == False) or (self.board[x][y+1] == self.board[x][y] and self.board_is_visited[x][y+1] == False)):
            return False
        
        # 递归判断邻接同色子是否有通路
        if self.board[x-1][y] == self.board[x][y] and self.board_is_visited[x-1][y] == False:
            if self.this_chess_can_exist(x-1,y):
                return True
        if self.board[x+1][y] == self.board[x][y] and self.board_is_visited[x+1][y] == False:
            if self.this_chess_can_exist(x+1,y):
                return True
        if self.board[x][y+1] == self.board[x][y] and self.board_is_visited[x][y+1] == False:
            if self.this_chess_can_exist(x,y+1):
                return True
        if self.board[x][y-1] == self.board[x][y] and self.board_is_visited[x][y-1] == False:
            if self.this_chess_can_exist(x,y-1):
                return True
        return False

    # 搜索全局删除死子（需要重构落子体系？
    def judge_capture(self):
        for x in range(1, self.board_size + 1):
            for y in range(1, self.board_size + 1):
                self.reset_visit()
                if not self.board_is_visited[x][y] and (self.board[x][y] == 'B' or self.board[x][y] == 'W'):
                    if not self.this_chess_can_exist(x, y):
                        print('delete_start')
                        for z in range(1, self.board_size + 1):
                            for w in range(1, self.board_size + 1):
                                if self.board_is_visited[z][w]:
                                    self.board[z][w] = '.'
                        return True
        return False


    # 预落子，判断能否落子
    def pre_play_check(self,x,y):
        self.board[x][y] = self.player
        self.reset_visit()
        self.board_is_visited[x][y] = True
        
        if self.this_chess_can_exist(x,y):
            self.board[x][y] = '.'
            return True
        else:
            if self.judge_capture():
                return True
        
        self.board[x][y] = '.'
        return False
    
    # 判断劫争中的落子
    #def ko_check(self,x,y):

    # 判断能否落子
    def can_play(self, x, y):
        if 1 <= x <= self.board_size and 1 <= y <= self.board_size and self.board[x][y] == '.':
            #if not self.ko_check(x,y):
                #return False
            if not self.pre_play_check(x,y):
                return False
            return True
        else:
            return False

    # 后端落子
    def drop_tile(self, pos):
        # 处理棋子位置
        x, y = pos
        
        x += self.tile_size // 2
        y += self.tile_size // 2
        
        x //= self.tile_size
        y //= self.tile_size
        
        # 落子？吃棋？劫争？
        if self.can_play(x, y):# 基础条件
            self.board[x][y] = self.player

            self.judge_capture()

            new_piece = Chess_Piece(self.player, x, y, True)
            
            self.cur_pos += 1
            
            if self.cur_pos >= len(self.move_order_records):
                self.move_order_records.append(new_piece)
            else:
                self.move_order_records[self.cur_pos] = new_piece

            self.player = 'W' if self.player == 'B' else 'B'

    # 后端处理前进、后退(基本开发完成)

    def move_backward(self):
        if self.cur_pos - 1 >= 0:
            
            
            self.board[self.move_order_records[self.cur_pos].x][self.move_order_records[self.cur_pos].y] = '.'
            print(self.cur_pos, self.move_order_records[self.cur_pos].x, self.move_order_records[self.cur_pos].y)
            self.cur_pos -= 1

    def move_forward(self):
        if self.cur_pos + 1 < len(self.move_order_records):
            self.cur_pos += 1
            self.board[self.move_order_records[self.cur_pos].x][self.move_order_records[self.cur_pos].y] = self.move_order_records[self.cur_pos].color
            print(self.cur_pos, self.move_order_records[self.cur_pos].x, self.move_order_records[self.cur_pos].y)




if __name__ == "__main__":
    # 前端初始化棋盘

   

    game = GO(board_size=19)
    pygame.init()
    game.screen = pygame.display.set_mode((game.display_width, game.display_height))
    pygame.display.set_caption("GO")
    game.font = pygame.font.Font(None, 36)

    game.draw_board()

    
    
    game_state = "running"

    while True:

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # 点击左键
                print(game.player)
                game.drop_tile(event.pos)
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    game.move_backward()
                if event.key == pygame.K_RIGHT:
                    game.move_forward()
                if event.key == pygame.K_r:  # 假设使用 'R' 键重置棋盘
                    game.clear_tiles()
        
        game.clear_tiles()
        game.draw_board()
        game.draw_tile()
        pygame.display.flip()