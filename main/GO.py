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
        self.width_board = self.board_height = (self.dimension - 1) * self.len_edge_grid    # 棋盘宽、高
        self.len_border = Config.SIZE["border"]                                             # 边界宽度
        self.width_display = self.width_board + 2 * self.len_border                         # 游戏界面宽度
        self.height_display = self.board_height + 2 * self.len_border                       # 游戏界面高度
        self.left = self.len_border                                                         # 网格左上角左
        self.top = self.len_border                                                          # 网格左上角上
        
        self.coordinate_points = [(3,3),(3,9),(3,15),(9,3),(9,9),(9,15),(15,3),(15,9),(15,15)]  # 提示点坐标
        
        # 图片资源
        self.image_blackStone = assets.images["black_stone"]
        self.image_whiteStone = assets.images["white_stone"]
        self.image_icon = assets.images["icon"]

        # 初始化游戏
        pygame.display.set_caption("GO") # 将游戏窗口命名为GO
        pygame.display.set_icon(self.image_icon)
        self.screen = pygame.display.set_mode((self.width_display, self.height_display)) # 设置当前窗口
        
        self.draw_board_static() # 绘制棋盘网格和提示点到背景
        self.background = self.screen.copy() # 保存界面背景
        
        ## 初始化棋局

        # 棋局：当前全盘
        self.current_board = [['.' for _ in range(0, self.dimension + 2)] for _ in range(0, self.dimension + 2)]
        # 设置边界一周不可行棋区
        for x in range(self.dimension + 2):
            self.current_board[x][0] = '*'
            self.current_board[x][20] = '*'
        for y in range(self.dimension + 2):
            self.current_board[0][y] = '*'
            self.current_board[20][y] = '*'

        # 当前棋子颜色
        self.current_color = 'B'

        # 初始化落子顺序记录数据集
        
        # 棋子链
        self.move_sequence_list = ['0']
        self.cur_pos = 0
        # 全局记录
        self.full_board_log = ['0']

    ## 图形
    
    def load_background(self):
        '''加载背景'''
        self.screen.blit(self.background, (0, 0)) # 使用保存的背景覆盖重置界面
    
    def draw_board_static(self):
        '''绘制静态棋盘背景'''
        # 填充棋盘颜色
        self.screen.fill(Config.COLORS['board'])

        # 绘制提示点
        for coordinate in self.coordinate_points:
            pygame.draw.circle(self.screen, Config.COLORS['black'], (coordinate[0] * self.len_edge_grid + self.left, coordinate[1] * self.len_edge_grid + self.top), 5)

        # 绘制网格线
        for x in range(self.dimension):
            pygame.draw.line(self.screen, Config.COLORS['black'], (x * self.len_edge_grid + self.left, self.top), (x * self.len_edge_grid + self.left, self.top + (self.dimension - 1) * self.len_edge_grid), 1)
        for y in range(self.dimension):
            pygame.draw.line(self.screen, Config.COLORS['black'], (self.left, self.top + y * self.len_edge_grid), (self.left + (self.dimension - 1) * self.len_edge_grid, self.top + y * self.len_edge_grid), 1)
    
    def draw_stone(self):
        '''绘制棋子'''
        for x in range(1, self.dimension + 1):
            for y in range(1, self.dimension + 1):
                if self.current_board[x][y] == '.':
                    continue
                
                # 棋子位置，位于网格线交点
                center_x = (x - 1) * self.len_edge_grid + self.left
                center_y = (y - 1) * self.len_edge_grid + self.top
                stone_rect = pygame.rect.Rect(center_x - self.len_edge_grid // 2,center_y - self.len_edge_grid // 2,self.len_edge_grid,self.len_edge_grid)
                
                # 绘制单个棋子
                if self.current_board[x][y] == 'B': # 黑棋
                    self.screen.blit(self.image_blackStone,stone_rect)
                elif self.current_board[x][y] == 'W': # 白棋
                    self.screen.blit(self.image_whiteStone,stone_rect)

    ## 逻辑
    
    def reset_visit(self):
        '''初始化已访问位置,未访问为False,已访问为True'''
        self.visited_area = [[False for _ in range(0, self.dimension + 1)] for _ in range(0, self.dimension + 1)]
    
    def reset_onetime_visit(self):
        '''初始化单次搜索已访问位置,未访问为False,已访问为True'''
        self.oneTime_visited_area = [[False for _ in range(0, self.dimension + 1)] for _ in range(0, self.dimension + 1)]
    
    def mark_dead_group(self, x, y):
        '''搜索单个位置看是否可找到出路，另可解释为找到并标记无气的一团死子,活棋返回True,死棋返回False'''
        # 如果这个子已经被访问，当作活棋返回True
        if self.visited_area[x][y]:
            # print(1)
            return True
        
        ## print(2) # 测试成功，此方法正常被运行
        # 标记这颗子为全局中的已访问
        self.visited_area[x][y] = True
        #print(self.visited_area[x][y], x, y)
        
        # 标记这颗子为单次已访问
        self.oneTime_visited_area[x][y] = True

        # 判断这颗子有没有气
        if self.current_board[x-1][y] == '.' or self.current_board[x][y-1] == '.' or self.current_board[x+1][y] == '.' or self.current_board[x][y+1] == '.':
            # self.dead_groups[x][y] = [True, self.current_board[x][y]]
            return True
        
        # 判断这颗子周围的同色子是否全部被访问过
        if not ((self.current_board[x-1][y] == self.current_board[x][y] and self.oneTime_visited_area[x-1][y] == False) or (self.current_board[x+1][y] == self.current_board[x][y] and self.oneTime_visited_area[x+1][y] == False) or (self.current_board[x][y-1] == self.current_board[x][y] and self.oneTime_visited_area[x][y-1] == False) or (self.current_board[x][y+1] == self.current_board[x][y] and self.oneTime_visited_area[x][y+1] == False)):
            return False
        
        # 递归判断邻接同色子是否有通路
        if self.current_board[x-1][y] == self.current_board[x][y] and self.oneTime_visited_area[x-1][y] == False:
            if self.mark_dead_group(x-1,y):
                return True
        if self.current_board[x+1][y] == self.current_board[x][y] and self.oneTime_visited_area[x+1][y] == False:
            if self.mark_dead_group(x+1,y):
                return True
        if self.current_board[x][y+1] == self.current_board[x][y] and self.oneTime_visited_area[x][y+1] == False:
            if self.mark_dead_group(x,y+1):
                return True
        if self.current_board[x][y-1] == self.current_board[x][y] and self.oneTime_visited_area[x][y-1] == False:
            if self.mark_dead_group(x,y-1):
                return True
        return False
    
    def check_ko(self, current_board_copy):
        '''
        劫争判断,
        3种状态:
        global_homogeneity劫争中全同,
        none_global_homogeneity劫争中但不存在全同,
        not_in_ko_state不在劫争中
        '''
        
        ## print(1) # 调用正常
        if self.cur_pos > 2:
            # DEBUG
            ## print(1) # 调用正常
            print('self.cur_pos',self.cur_pos)
            print('type(self.full_board_log)',type(self.full_board_log))
            print('len(self.full_board_log)',len(self.full_board_log))
            #print(self.full_board_log)
            '''
            for z in range(1, len(self.full_board_log)):
                for x in range(1, self.dimension + 1):
                    for y in range(1, self.dimension + 1):
                        print(self.full_board_log[z][y][x],end='')
                    print()
                print()
            '''
            '''
            for x in range(1, self.dimension + 1):
                for y in range(1, self.dimension + 1):
                    print(self.current_board[y][x],end='')
                print()
            '''
            # 对副本进行提对方死子操作
            opposite_color = 'W' if self.current_color == 'B' else 'B'
            self.delete_dead_stones(opposite_color, current_board_copy)
            # DEBUG
            for x in range(1, self.dimension + 1):
                for y in range(1, self.dimension + 1):
                    print(current_board_copy[y][x],end='')
                print()
            
            # !! 此处功能不正常，无法正常比较，需要完成提子操作才能进行比较
            if self.full_board_log[self.cur_pos + 1 - 2] == current_board_copy:
                print(1)
                return 'global_homogeneity'
            else:
                print(2)
                return 'none_global_homogeneity'
        
        return 'not_in_ko_state'

    def reset_dead_groups(self):
        '''重置死棋'''
        # 0到max是因为存储从0开始，便于模拟1到max
        # False是被标记的死棋
        self.dead_groups = [[True for _ in range(0, self.dimension + 1)] for _ in range(0, self.dimension + 1)]
        
        # 死子团数
        self.dead_group_num = 0
        
        # 死棋颜色及其个数
        self.dead_group_color_num = 0
        self.dead_white = False
        self.dead_black = False

    def check_for_dead_groups(self):
        '''判断全盘是否存在没有气的棋块'''
        
        self.reset_dead_groups() # 重置死子标记
        # DEBUG
        '''
        for z in range(1, self.dimension + 1):
            for w in range(1, self.dimension + 1):
                print(self.dead_groups[z][w],end='')
            print()
        '''
        
        self.reset_visit() # 清除访问状态
        ## print(1) # 每点击一次输出一次，正常
        # 全盘搜索，对没有气的棋块进行标记
        for x in range(1, self.dimension + 1):
            for y in range(1, self.dimension + 1):
                ## print(1) # 每点击一次输出一次，正常
                
                # 空位不判定
                if self.current_board[x][y] == '.':
                    continue
                
                self.reset_onetime_visit() # 清除单次访问状态
                
                # 死棋判定
                if not self.mark_dead_group(x, y): # 活棋或不用搜索的棋 True, 死棋 False
                    ## print(2)
                    # 死棋块数增加1
                    self.dead_group_num += 1
                    
                    # 死棋颜色标记
                    if self.current_board[x][y] == 'B': # 黑棋
                        self.dead_black = True
                    else:
                        self.dead_white = True
                    
                    # 将已判定死棋区域转移至dead_groups
                    for z in range(1, self.dimension + 1):
                        for w in range(1, self.dimension + 1):
                            if self.oneTime_visited_area[z][w] == True:
                                self.dead_groups[z][w] = False
        
        # 统计死棋颜色种数
        self.dead_group_color_num += 1 if self.dead_black == True else 0
        self.dead_group_color_num += 1 if self.dead_white == True else 0
        
        # 一块死棋特判，确定死棋颜色
        if self.dead_group_color_num == 1:
            self.dead_group_color = 'W' if self.dead_white == True else 'B'
        
        return self.dead_group_num

    def can_play(self, x, y, current_color):
        '''判断能否落子'''
        # 判断量
        canPlay = False
        
        # 基础条件，在棋盘上and这个位置为空位
        if 1 <= x <= self.dimension and 1 <= y <= self.dimension and self.current_board[x][y] == '.':
            # DEBUG
            print(current_color)
            self.current_board[x][y] = current_color # 在原有棋局上加上这一颗子
            dead_group_num = self.check_for_dead_groups() # 检查全盘，获取死棋块数，进行死子标记
            # DEBUG
            print('dead_group_num',dead_group_num)
            if dead_group_num == 0: # 0块死棋，没有死棋，能正常落子
                canPlay = True
            elif dead_group_num == 1: # 1块死棋，禁入点，不能落子
                if current_color == self.dead_group_color:
                    canPlay = False
                else:
                    canPlay = True
            elif dead_group_num == 2: # 2块死棋，考虑劫争
                ko_value = self.check_ko(copy.deepcopy(self.current_board)) # 获取劫争状态
                if ko_value == 'global_homogeneity':
                    canPlay = False
                else:
                    canPlay = True
            elif dead_group_num >= 3: # 3块及以上死棋，不是劫争，可以落子
                canPlay = True
            self.current_board[x][y] = '.' # 还原这个位置为空位
            
        else:
            canPlay =  False
        
        return canPlay

    def delete_dead_stones(self, opposite_color, board):
        '''删除传入棋局的对方死子'''
        for x in range(1, self.dimension + 1):
            for y in range(1, self.dimension + 1):
                if self.dead_groups[x][y] == False and opposite_color == board[x][y]:
                    # DEBUG
                    print('delete', x, y)
                    
                    board[x][y] = '.'

    def pos_to_coordinate(self, pos):
        '''（鼠标点击）位置转化为坐标'''
        x, y = pos
        
        x -= self.left
        y -= self.top
        
        x += self.len_edge_grid // 2
        y += self.len_edge_grid // 2
        
        x //= self.len_edge_grid
        y //= self.len_edge_grid
        
        x += 1
        y += 1
        
        return x, y

    def drop_stone(self, pos):
        '''落子'''
        
        x, y = game.pos_to_coordinate(pos) # 处理棋子位置
        
        # 判断能否落子，先判断落子，判断落子时记录要删除的位子（死子），正式落子后删除相应位置的子
        if self.can_play(x, y, self.current_color):
            # 落子
            self.current_board[x][y] = self.current_color
            # DEBUG
            print('self.current_color',self.current_color)
            
            # 删去对方的标记的死子
            opposite_color = 'W' if self.current_color == 'B' else 'B'
            self.delete_dead_stones(opposite_color, self.current_board)
            
            self.cur_pos += 1 # 当前手数+1
            
            # 在全局记录上记录当前全盘情况
            self.full_board_log.append(copy.deepcopy(self.current_board))
            
            # DEBUG
            print(self.cur_pos)
            for x in range(1, self.dimension + 1):
                for y in range(1, self.dimension + 1):
                    print(self.full_board_log[self.cur_pos][y][x],end='')
                print()
            print()
            
            # 反转棋子颜色
            self.current_color = 'W' if self.current_color == 'B' else 'B'

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
            # 点击左键
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                game.drop_stone(event.pos)
        
        game.load_background()
        game.draw_stone()
        pygame.display.flip()
        clock.tick(165)