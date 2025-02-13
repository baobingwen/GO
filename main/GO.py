import os
import copy
import sys
import pygame
import numpy as np
from config import Config
from assets import assets

#os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1' # 隐藏pygame控制台窗口

class GO:
    def __init__(self) -> None:
        
        # 棋盘基本量
        self.dimension = Config.SIZE["dimension_init"]                                      # 19路
        self.len_edge_grid = Config.SIZE["edge_grid"]                                       # 格宽
        self.width_board = self.height_board = (self.dimension - 1) * self.len_edge_grid    # 棋盘宽、高
        self.len_border = Config.SIZE["border"]                                             # 边界宽度
        self.left_board = self.len_border                                                   # 网格左上角左
        self.top_board = self.len_border                                                    # 网格左上角上
        
        self.coordinate_points = [(3,3),(3,9),(3,15),(9,3),(9,9),(9,15),(15,3),(15,9),(15,15)]  # 提示点坐标
        
        self.left_button_square = self.left_board + self.width_board // 2
        self.top_button_square = self.top_board + self.height_board
        self.width_button_square = self.len_border
        self.height_button_square = self.len_border
        self.rect_button_square = pygame.rect.Rect(self.left_button_square,self.top_button_square,self.width_button_square,self.height_button_square)
        
        self.width_display = self.left_board + self.width_board + self.len_border                 # 游戏界面宽度
        self.height_display = self.top_board + self.height_board + self.len_border                # 游戏界面高度
        
        # 图片资源
        self.image_blackStone = assets.images["black_stone"]
        self.image_whiteStone = assets.images["white_stone"]
        self.image_icon = assets.images["icon"]

        # 初始化pygame
        pygame.display.set_caption("GO") # 将游戏窗口命名为GO
        pygame.display.set_icon(self.image_icon)
        self.screen = pygame.display.set_mode((self.width_display, self.height_display)) # 设置当前窗口
        
        self.draw_board_static() # 绘制棋盘网格和提示点到背景
        self.background = self.screen.copy() # 保存界面背景
        
        ## 初始化棋局

        # 棋局：当前全盘
        self.current_board = [['.' for _ in range(0, self.dimension + 2)] for _ in range(0, self.dimension + 2)]
        # 设置棋局边界一周的障碍区
        for x in range(self.dimension + 2):
            self.current_board[x][0] = '*'
            self.current_board[x][20] = '*'
        for y in range(self.dimension + 2):
            self.current_board[0][y] = '*'
            self.current_board[20][y] = '*'

        self.current_color = 'B' # 当前棋子颜色

        # 初始化落子顺序记录数据集
        self.move_sequence_list = ['0'] # 行棋链
        self.cur_move = 0 # 当前下了几步棋
        self.full_board_log = ['0'] # 全局记录,先占零位,从1开始记录

    ## 图形
    
    def load_background(self) -> None:
        '''加载背景'''
        self.screen.blit(self.background, (0, 0)) # 使用保存的背景覆盖重置界面
    
    def draw_board_static(self) -> None:
        '''绘制静态棋盘背景'''
        # 填充棋盘颜色
        self.screen.fill(Config.COLORS['board'])

        # 绘制提示点
        for coordinate in self.coordinate_points:
            pygame.draw.circle(self.screen, Config.COLORS['black'], (coordinate[0] * self.len_edge_grid + self.left_board, coordinate[1] * self.len_edge_grid + self.top_board), 5)

        # 绘制网格线
        for x in range(self.dimension):
            pygame.draw.line(self.screen, Config.COLORS['black'], (self.left_board + x * self.len_edge_grid, self.top_board), (self.left_board + x * self.len_edge_grid, self.top_board + (self.dimension - 1) * self.len_edge_grid), 1)
        for y in range(self.dimension):
            pygame.draw.line(self.screen, Config.COLORS['black'], (self.left_board, self.top_board + y * self.len_edge_grid), (self.left_board + (self.dimension - 1) * self.len_edge_grid, self.top_board + y * self.len_edge_grid), 1)
    
    def draw_piece(self) -> None:
        '''绘制棋子'''
        for x in range(1, self.dimension + 1):
            for y in range(1, self.dimension + 1):
                if self.current_board[x][y] == '.':
                    continue
                
                # 棋子位置，位于网格线交点
                center_x = (x - 1) * self.len_edge_grid + self.left_board
                center_y = (y - 1) * self.len_edge_grid + self.top_board
                stone_rect = pygame.rect.Rect(center_x - self.len_edge_grid // 2,center_y - self.len_edge_grid // 2,self.len_edge_grid,self.len_edge_grid)
                
                # 绘制单个棋子
                if self.current_board[x][y] == 'B': # 黑棋
                    self.screen.blit(self.image_blackStone,stone_rect)
                elif self.current_board[x][y] == 'W': # 白棋
                    self.screen.blit(self.image_whiteStone,stone_rect)
    
    def draw_button(self) -> None:
        '''绘制按钮'''
        pass
    def draw(self) -> None:
        '''绘制界面'''
        self.load_background()
        self.draw_piece()
        self.draw_button()

    ## 逻辑
    
    def reset_visit(self):
        '''初始化单次遍历已访问位置,未访问为False,已访问为True'''
        self.area_visited = [[False for _ in range(0, self.dimension + 1)] for _ in range(0, self.dimension + 1)]
    
    def reset_onetime_visit(self):
        '''初始化单次深搜已访问位置,未访问为False,已访问为True'''
        self.oneTime_visited_area = [[False for _ in range(0, self.dimension + 1)] for _ in range(0, self.dimension + 1)]
    
    def mark_dead_group(self, x, y) -> bool:
        '''
        对单个位置进行深搜,判断这个位置的棋子是否是死棋;
        在深搜过程中可以标记无气的一团死子;
        活棋返回True,
        不是活棋返回False
        '''
        
        if self.area_visited[x][y]: # 访问本次遍历已访问位置标记，如果这个子已经被访问，不做处理，当作活棋返回True
            return True
        self.area_visited[x][y] = True # 标记这颗子为遍历中的已访问
        
        self.oneTime_visited_area[x][y] = True # 标记这颗子为本次深搜已访问

        # 判断这个位置的棋子有没有气。有气即上下左右方向存在空位。有气则活棋。活棋则返回True。
        for i,j in [(-1,0),(0,-1),(1,0),(0,1)]:
            if self.current_board[x+i][y+j] == '.':
                return True
        
        # 判断这个位置的棋子上下左右的同色棋子是否全部被访问过。如果在本次深搜内全部被访问过，返回False。
        if sum((self.current_board[x][y] == self.current_board[x+i][y+j] and self.oneTime_visited_area[x+i][y+j] == False) for i,j in [(-1,0),(0,-1),(1,0),(0,1)]) == 0:
            return False
        
        # 递归判断邻接同色子是否有通路
        for i,j in [(-1,0),(0,-1),(1,0),(0,1)]:
            if self.current_board[x+i][y+j] == self.current_board[x][y] and self.oneTime_visited_area[x+i][y+j] == False:
                if self.mark_dead_group(x+i,y+j):
                    return True
        return False # 如果上下左右同色棋子都没有活棋，返回False
    
    def check_ko(self, current_board_copy) -> bool:
        '''
        劫争判断,
        2种状态:
        True: global_homogeneity,全局同型;
        False: none_global_homogeneity,非全同;
        '''
        
        if self.cur_move <= 2: # 手数少于2不可能劫争
            return False
        
        # DEBUG
        print(f'self.cur_move: {self.cur_move}')
        print(f'len(self.full_board_log): {len(self.full_board_log)}')
        
        # 对副本进行提行棋者对方的死子的操作
        opposite_color = 'W' if self.current_color == 'B' else 'B'
        self.delete_dead_stones(opposite_color, current_board_copy)
        # DEBUG
        print('current_board_copy deleted dead pieces:')
        for x in range(1, self.dimension + 1):
            for y in range(1, self.dimension + 1):
                print(current_board_copy[y][x],end='')
            print()
        
        # 需要完成提子操作后，将提完子的棋局和之前的棋局进行比较。如果相同，则判断出现全局同型，返回True；如果不同，则判断不是全同，返回False。
        if self.full_board_log[self.cur_move + 1 - 2] == current_board_copy:
            print('global_homogeneity')
            return True
        else:
            print('none_global_homogeneity')
            return False

    def reset_dead_groups(self):
        '''重置死棋'''
        # 0到max是因为存储从0开始，便于模拟1到max
        # True是被标记的死棋
        self.dead_groups = [[False for _ in range(0, self.dimension + 1)] for _ in range(0, self.dimension + 1)]
        
        # 死子团数
        self.dead_group_num = 0
        
        # 死棋颜色及其个数
        self.dead_group_color_num = 0
        self.dead_white = False
        self.dead_black = False

    def check_for_dead_groups(self):
        '''判断全盘是否存在没有气的棋块'''
        
        self.reset_dead_groups() # 重置死子标记
        self.reset_visit() # 清除遍历访问状态
        
        # 全盘搜索，对没有气的棋块进行标记
        for x in range(1, self.dimension + 1):
            for y in range(1, self.dimension + 1):
                # 空位不判定
                if self.current_board[x][y] == '.':
                    continue
                
                self.reset_onetime_visit() # 清除单次深搜访问状态
                
                # 死棋判定，不是死棋不用操作
                if self.mark_dead_group(x, y): # 活棋或不用搜索的棋 True, 死棋 False
                    continue
                # 是死棋
                self.dead_group_num += 1 # 死棋块数增加1
                
                if self.current_board[x][y] == 'B': # 黑棋
                    self.dead_black = True # 死棋颜色标记
                else: # 白棋
                    self.dead_white = True
                
                # 将已判定死棋区域转移至dead_groups
                # 在针对本格的死棋块深搜mark_dead_group()中，搜索过的区域都是死棋。
                for z in range(1, self.dimension + 1):
                    for w in range(1, self.dimension + 1):
                        if self.oneTime_visited_area[z][w] == True:
                            self.dead_groups[z][w] = True
        
        # 统计死棋颜色种数
        self.dead_group_color_num += 1 if self.dead_black else 0
        self.dead_group_color_num += 1 if self.dead_white else 0
        
        # 一块死棋特判，确定死棋颜色
        if self.dead_group_color_num == 1:
            self.dead_group_color = 'W' if self.dead_white else 'B'
        
        return self.dead_group_num

    def handle_piece_place(self, x, y, current_piece) -> bool:
        '''处理落子，返回能否落子'''
        canPlay = False # 判断能否落子的返回量
        
        # 基础条件:在棋盘上 并且 这个位置没有棋子
        if not (1 <= x <= self.dimension and 1 <= y <= self.dimension and self.current_board[x][y] == '.'):
            return False
        
        self.current_board[x][y] = current_piece # 尝试落子，在原有棋局上该落子位置上加上这一颗棋子(后面会还原)
        dead_group_num = self.check_for_dead_groups() # 检查全盘，获取死棋块数，进行死子标记
        
        # 根据死棋情况处理能否落子
        if dead_group_num == 0: # 0块死棋，没有死棋，能正常落子
            canPlay = True
        elif dead_group_num == 1: # 1块死棋
            if current_piece == self.dead_group_color: # 死棋颜色和落子颜色一样，说明本次落子处是禁入点，不能落子
                canPlay = False
            else: # 死棋颜色与落子颜色相异，说明死的是非落子方的棋子，可以落子
                canPlay = True
        elif dead_group_num == 2: # 2块死棋，考虑劫争，全同不可落子
            canPlay = not self.check_ko(copy.deepcopy(self.current_board)) # 获取劫争状态，全局同型True，非全局同型False
        elif dead_group_num >= 3: # 3块及以上死棋，不是劫争，可以落子
            canPlay = True
        
        self.current_board[x][y] = '.' # 还原当前棋局落子位置为空位
        
        return canPlay

    def delete_dead_stones(self, opposite_color, board):
        '''
        传入要删除的棋子颜色 和 要删除的棋局。
        删除传入棋局的行棋对方的死子。
        '''
        for x in range(1, self.dimension + 1):
            for y in range(1, self.dimension + 1):
                if self.dead_groups[x][y] == True and board[x][y] == opposite_color:
                    # DEBUG
                    print(f'delete ({x},{y})')
                    
                    board[x][y] = '.' # 在dead_groups中被标记为死棋，并且是对方棋子，提子

    def pos_to_coordinate(self, pos):
        '''（鼠标点击）位置转化为坐标'''
        x, y = pos
        
        x -= self.left_board
        y -= self.top_board
        
        x += self.len_edge_grid // 2
        y += self.len_edge_grid // 2
        
        x //= self.len_edge_grid
        y //= self.len_edge_grid
        
        x += 1
        y += 1
        
        return x, y

    def drop_piece(self, pos):
        '''落子'''
        
        x, y = game.pos_to_coordinate(pos) # 处理鼠标点击位置，获取棋子抽象坐标，即current_board里的坐标
        
        # 处理落子，判断能否落子。先判断落子，判断落子时记录要删除的棋子位置（死子位置），正式落子后删除相应位置的棋子
        if not self.handle_piece_place(x, y, self.current_color):
            return # 不能落子，直接返回不做处理
        # 可以落子
        self.current_board[x][y] = self.current_color # 正式落子
        # DEBUG
        print('self.current_color',self.current_color)
        
        # 删除行棋者对手的死子
        opposite_color = 'W' if self.current_color == 'B' else 'B'
        self.delete_dead_stones(opposite_color, self.current_board)
        
        self.cur_move += 1 # 当前手数+1
        self.full_board_log.append(copy.deepcopy(self.current_board)) # 在全局记录上加上当前全盘情况的记录
        
        # DEBUG
        print('self.cur_move',self.cur_move)
        '''for x in range(1, self.dimension + 1):
            for y in range(1, self.dimension + 1):
                print(self.full_board_log[self.cur_move][y][x],end='')
            print()
        print()'''
        
        # 准备下一步行棋，反转棋子颜色
        self.current_color = 'W' if self.current_color == 'B' else 'B'
    
    def handle_event(self,event):
        '''事件处理'''
        # 点击左键
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            game.drop_piece(event.pos)

if __name__ == "__main__":
    pygame.init()
    assets.load_all()

    game = GO()

    clock = pygame.time.Clock() # 游戏帧率
    while True:
        # 游戏发生事件
        for event in pygame.event.get():
            # 退出游戏
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            # 处理事件
            game.handle_event(event)
        
        game.draw()
        pygame.display.flip()
        clock.tick(165)