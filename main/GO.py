import os
import sys
import pygame
import numpy as np

#os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1' # 隐藏pygame控制台窗口

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
BOARD_COLOR = (221, 182, 116)

cell_edge_len = 40 # 棋子大小

Only_black = False
Only_white = False

class Only_Black_Piece_Button:
    def __init__(self):
        self.rect = pygame.Rect(cell_edge_len, cell_edge_len * 20, 80, 20)
        self.color = GRAY
        self.text = 'only black'

    def draw_button(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)
        if self.text:
            font = pygame.font.Font(None, 24)
            text_surf = font.render(self.text, True, BLACK)
            text_rect = text_surf.get_rect(center=self.rect.center)
            screen.blit(text_surf, text_rect)

    def set_only_black(self, event_pos):
        if self.rect.collidepoint(event_pos):
            global Only_black, Only_white
            Only_black = True
            Only_white = False

class Only_White_Piece_Button:
    def __init__(self):
        self.rect = pygame.Rect(cell_edge_len * 3, cell_edge_len * 20, 80, 20)
        self.color = GRAY
        self.text = 'only white'

    def draw_button(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)
        if self.text:
            font = pygame.font.Font(None, 24)
            text_surf = font.render(self.text, True, BLACK)
            text_rect = text_surf.get_rect(center=self.rect.center)
            screen.blit(text_surf, text_rect)

    def set_only_white(self, event_pos):
        if self.rect.collidepoint(event_pos):
            global Only_black, Only_white
            Only_black = False
            Only_white = True

class Normal_Mode_Button:
    def __init__(self):
        self.rect = pygame.Rect(cell_edge_len * 5, cell_edge_len * 20, 80, 20)
        self.color = GRAY
        self.text = 'normal'

    def draw_button(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)
        if self.text:
            font = pygame.font.Font(None, 24)
            text_surf = font.render(self.text, True, BLACK)
            text_rect = text_surf.get_rect(center=self.rect.center)
            screen.blit(text_surf, text_rect)

    def set_normal(self, event_pos):
        if self.rect.collidepoint(event_pos):
            global Only_black, Only_white
            Only_black = False
            Only_white = False

class Cur_Piece_Color:
    def __init__(self):
        self.rect = pygame.Rect(cell_edge_len * 7, cell_edge_len * 20, 80, 20)
        self.color = GRAY
        self.text = ''

    def draw_button(self, screen, player):
        pygame.draw.rect(screen, self.color, self.rect)
        color = BLACK if player == 'B' else WHITE
        pygame.draw.circle(screen, color, (self.rect.centerx, self.rect.centery), cell_edge_len // 2 - 3)

        if self.text:
            font = pygame.font.Font(None, 24)
            text_surf = font.render(self.text, True, BLACK)
            text_rect = text_surf.get_rect(center=self.rect.center)
            screen.blit(text_surf, text_rect)

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
    def __init__(self, board_dimension = 19, cell_edge_len = 40):
        
        # 基本量
        self.board_dimension = board_dimension                                                  # 路数
        self.cell_edge_len = cell_edge_len                                                      # 格宽
        self.board_width = self.board_height = (self.board_dimension - 1) * self.cell_edge_len  # 棋盘宽、高
        self.border_len = cell_edge_len                                                         # 边界宽度
        self.display_width = self.board_width + 2 * self.border_len                             # 游戏界面宽度
        self.display_height = self.board_height + 2 * self.border_len + self.border_len         # 游戏界面高度

        # 前端初始化棋盘
        pygame.init()
        pygame.display.set_caption("GO") # 将游戏窗口命名为GO
        self.screen = pygame.display.set_mode((self.display_width, self.display_height)) # 设置当前窗口
        self.font = pygame.font.Font(None, 36)
        
        # 绘制棋盘网格和提示点到背景
        self.draw_board()  

        # 保存游戏的背景
        self.background = self.screen.copy()
        
        
        # 后端初始化棋局

        # 棋局：当前全盘
        self.current_board = [['.' for _ in range(0, self.board_dimension + 2)] for _ in range(0, self.board_dimension + 2)]
        # 设置边界一周不可行棋区
        for x in range(self.board_dimension + 2):
            self.current_board[x][0] = '*'
            self.current_board[x][20] = '*'
        for y in range(self.board_dimension + 2):
            self.current_board[0][y] = '*'
            self.current_board[20][y] = '*'

        # 当前棋子颜色
        self.player = 'W'

        # 后端初始化落子顺序记录数据集
        self.move_order_records = ['0']
        self.cur_pos = 0

    
    
    # 重置背景
    def load_background(self):
        # 使用保存的背景覆盖重置棋盘
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
    
    # 前端绘制棋子
    def draw_tile(self):
        for x in range(1, self.board_dimension + 1):
            for y in range(1, self.board_dimension + 1):
                if self.current_board[x][y] != '.':
                    
                    # 计算棋子的中心位置，确保它位于网格线的交点上
                    center_x = (x) * self.cell_edge_len
                    center_y = (y) * self.cell_edge_len
                    
                    # 放置单个棋子
                    color = BLACK if self.current_board[x][y] == 'B' else WHITE
                    
                    

                    pygame.draw.circle(self.screen, color, (int(center_x), int(center_y)), self.cell_edge_len // 2 - 3)

    ## 后端
    
    
    # 初始化已访问位置
    def reset_visit(self):
        self.board_is_visited = [[False for _ in range(0, self.board_dimension + 1)] for _ in range(0, self.board_dimension + 1)]
    
    # 搜索单个位置看是否可找到出路，另可解释为找到并标记无气的一团死子
    def this_chess_can_exist(self,x,y):
        # 标记这颗子为已访问
        self.board_is_visited[x][y] = True
        #print(self.board_is_visited[x][y], x, y)

        # 判断这颗子有没有气
        if self.current_board[x-1][y] == '.' or self.current_board[x][y-1] == '.' or self.current_board[x+1][y] == '.' or self.current_board[x][y+1] == '.':
            return True
        
        # 判断这颗子周围的同色子是否全部被访问过
        if not ((self.current_board[x-1][y] == self.current_board[x][y] and self.board_is_visited[x-1][y] == False) or (self.current_board[x+1][y] == self.current_board[x][y] and self.board_is_visited[x+1][y] == False) or (self.current_board[x][y-1] == self.current_board[x][y] and self.board_is_visited[x][y-1] == False) or (self.current_board[x][y+1] == self.current_board[x][y] and self.board_is_visited[x][y+1] == False)):
            return False
        
        # 递归判断邻接同色子是否有通路
        if self.current_board[x-1][y] == self.current_board[x][y] and self.board_is_visited[x-1][y] == False:
            if self.this_chess_can_exist(x-1,y):
                return True
        if self.current_board[x+1][y] == self.current_board[x][y] and self.board_is_visited[x+1][y] == False:
            if self.this_chess_can_exist(x+1,y):
                return True
        if self.current_board[x][y+1] == self.current_board[x][y] and self.board_is_visited[x][y+1] == False:
            if self.this_chess_can_exist(x,y+1):
                return True
        if self.current_board[x][y-1] == self.current_board[x][y] and self.board_is_visited[x][y-1] == False:
            if self.this_chess_can_exist(x,y-1):
                return True
        return False

    # 搜索全局删除死子（需要重构落子体系？
    def judge_capture(self):
        for x in range(1, self.board_dimension + 1):
            for y in range(1, self.board_dimension + 1):
                # 清除访问状态
                self.reset_visit()
                # 
                if not self.board_is_visited[x][y] and (self.current_board[x][y] == 'B' or self.current_board[x][y] == 'W'):
                    if not self.this_chess_can_exist(x, y) and not self.current_board[x][y] == self.player:
                        print('delete_start')
                        for z in range(1, self.board_dimension + 1):
                            for w in range(1, self.board_dimension + 1):
                                if self.board_is_visited[z][w]:
                                    self.current_board[z][w] = '.'
                        return True
        return False


    # 预落子，判断能否落子
    def pre_play_check(self,x,y):
        self.current_board[x][y] = self.player
        self.reset_visit()
        self.board_is_visited[x][y] = True
        
        if self.this_chess_can_exist(x,y):
            self.current_board[x][y] = '.'
            return True
        else:
            if self.judge_capture():
                return True
        
        self.current_board[x][y] = '.'
        return False
    
    # 判断劫争中的落子
    #def ko_check(self,x,y):

    # 判断能否落子
    def can_play(self, x, y):
        if 1 <= x <= self.board_dimension and 1 <= y <= self.board_dimension and self.current_board[x][y] == '.':
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
        
        x += self.cell_edge_len // 2
        y += self.cell_edge_len // 2
        
        x //= self.cell_edge_len
        y //= self.cell_edge_len
        
        # 落子？吃棋？劫争？
        if self.can_play(x, y):# 基础条件

            if Only_black:
                #print(1)
                self.player = 'B'
            elif Only_white:
                #print(2)
                self.player = 'W'
            else:
                #print(3)
                # 反转棋子颜色
                self.player = 'W' if self.player == 'B' else 'B'

            self.current_board[x][y] = self.player

            self.judge_capture()

            new_piece = Chess_Piece(self.player, x, y, True)
            
            self.cur_pos += 1
            
            if self.cur_pos >= len(self.move_order_records):
                self.move_order_records.append(new_piece)
            else:
                self.move_order_records[self.cur_pos] = new_piece

            

    # 后端处理前进、后退(基本开发完成)

    def move_backward(self):
        if self.cur_pos - 1 >= 0:
            
            
            self.current_board[self.move_order_records[self.cur_pos].x][self.move_order_records[self.cur_pos].y] = '.'
            #print(self.cur_pos, self.move_order_records[self.cur_pos].x, self.move_order_records[self.cur_pos].y)
            self.cur_pos -= 1

    def move_forward(self):
        if self.cur_pos + 1 < len(self.move_order_records):
            self.cur_pos += 1
            self.current_board[self.move_order_records[self.cur_pos].x][self.move_order_records[self.cur_pos].y] = self.move_order_records[self.cur_pos].color
            #print(self.cur_pos, self.move_order_records[self.cur_pos].x, self.move_order_records[self.cur_pos].y)




if __name__ == "__main__":
    # 前端初始化棋盘

   

    game = GO(board_dimension = 19)
    pygame.init()
    pygame.display.set_caption("GO")
    game.screen = pygame.display.set_mode((game.display_width, game.display_height))
    
    game.font = pygame.font.Font(None, 36)

    game.draw_board()

    
    only_Black_Piece_Button = Only_Black_Piece_Button()
    only_Black_Piece_Button.draw_button(game.screen)

    only_White_Piece_Button = Only_White_Piece_Button()
    only_White_Piece_Button.draw_button(game.screen)
    
    normal_Mode_Button = Normal_Mode_Button()
    normal_Mode_Button.draw_button(game.screen)

    cur_Piece_Color = Cur_Piece_Color()
    cur_Piece_Color.draw_button(game.screen, game.player)

    while True:

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # 点击左键
                print(game.player)
                game.drop_tile(event.pos)
                only_Black_Piece_Button.set_only_black(event.pos)
                only_White_Piece_Button.set_only_white(event.pos)
                normal_Mode_Button.set_normal(event.pos)
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    game.move_backward()
                if event.key == pygame.K_RIGHT:
                    game.move_forward()
                
        
        game.load_background()
        only_Black_Piece_Button.draw_button(game.screen)
        only_White_Piece_Button.draw_button(game.screen)
        normal_Mode_Button.draw_button(game.screen)
        cur_Piece_Color.draw_button(game.screen, game.player)
        game.draw_tile()
        pygame.display.flip()