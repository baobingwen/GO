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

    def draw_button(self, screen, current_color):
        pygame.draw.rect(screen, self.color, self.rect)
        color = BLACK if current_color == 'B' else WHITE
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
        self.current_color = 'B'

        # 后端初始化落子顺序记录数据集
        
        # 棋子链
        self.move_sequence_list = ['0']
        self.cur_pos = 0
        # 全局记录
        self.full_board_log = ['0']

    ## 前端
    
    # 重置背景
    def load_background(self):
        # 使用保存的背景覆盖重置棋盘
        self.screen.blit(self.background, (0, 0))
    
    # 前端绘制棋盘
    def draw_board(self):

        # 填充棋盘颜色
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
    
    
    # 初始化已访问位置，未访问为False，已访问为True
    def reset_visit(self):
        self.visited_area = [[False for _ in range(0, self.board_dimension + 1)] for _ in range(0, self.board_dimension + 1)]
    
    # 初始化单次搜索已访问位置，未访问为False，已访问为True
    def reset_onetime_visit(self):
        self.oneTime_visited_area = [[False for _ in range(0, self.board_dimension + 1)] for _ in range(0, self.board_dimension + 1)]
    
    # 搜索单个位置看是否可找到出路，另可解释为找到并标记无气的一团死子，活棋返回True，死棋返回False
    def mark_dead_group(self, x, y):
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
    '''
    # 搜索全局删除死子（需要重构落子体系？
    def judge_capture(self):
        for x in range(1, self.board_dimension + 1):
            for y in range(1, self.board_dimension + 1):
                # 清除访问状态
                self.reset_visit()
                # 
                if not self.visited_area[x][y] and (self.current_board[x][y] == 'B' or self.current_board[x][y] == 'W'):
                    if not self.mark_dead_group(x, y) and not self.current_board[x][y] == self.current_color:
                        print('delete_start')
                        for z in range(1, self.board_dimension + 1):
                            for w in range(1, self.board_dimension + 1):
                                if self.visited_area[z][w]:
                                    self.current_board[z][w] = '.'
                        return True
        return False

    
    # 预落子，判断能否落子
    def pre_play_check(self,x,y):
        self.current_board[x][y] = self.current_color
        self.reset_visit()
        self.visited_area[x][y] = True
        
        if self.mark_dead_group(x,y):
            self.current_board[x][y] = '.'
            return True
        else:
            if self.judge_capture():
                return True
        
        self.current_board[x][y] = '.'
        return False
    '''
    # 劫争判断，3种状态：global_homogeneity劫争中全同，none_global_homogeneity劫争中但不存在全同，not_in_ko_state不在劫争中
    def check_ko(self):
        if self.cur_pos > 2:
            if self.full_board_log[self.cur_pos - 2] == self.current_board:
                return 'global_homogeneity'
            else:
                return 'none_global_homogeneity'
        else:
            return 'not_in_ko_state'

    # 重置死棋
    def reset_dead_groups(self):
        # 0到max是因为存储从0开始，便于模拟1到max
        # False是被标记的死棋
        self.dead_groups = [[True for _ in range(0, self.board_dimension + 1)] for _ in range(0, self.board_dimension + 1)]
        
        # 死子团数
        self.dead_group_num = 0
        
        # 死棋颜色及其个数
        self.dead_group_color_num = 0
        self.dead_white = False
        self.dead_black = False

    # 判断全盘是否存在没有气的棋块
    def check_for_dead_groups(self):
        # 重置死子标记
        self.reset_dead_groups()
        
        '''
        for z in range(1, self.board_dimension + 1):
            for w in range(1, self.board_dimension + 1):
                print(self.dead_groups[z][w],end='')
            print()
        '''
        # 清除访问状态
        self.reset_visit()
        ## print(1) # 每点击一次输出一次，正常
        # 全盘搜索，对没有气的棋块进行标记
        for x in range(1, self.board_dimension + 1):
            for y in range(1, self.board_dimension + 1):
                ## print(1) # 每点击一次输出一次，正常
                
                # 空位不判定
                if self.current_board[x][y] == '.':
                    continue
                
                # 清除单次访问状态
                self.reset_onetime_visit()
                
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
                    for z in range(1, self.board_dimension + 1):
                        for w in range(1, self.board_dimension + 1):
                            if self.oneTime_visited_area[z][w] == True:
                                self.dead_groups[z][w] = False
        
        # 统计死棋颜色种数
        self.dead_group_color_num += 1 if self.dead_black == True else 0
        self.dead_group_color_num += 1 if self.dead_white == True else 0
        
        # 一块死棋特判，确定死棋颜色
        if self.dead_group_color_num == 1:
            self.dead_group_color = 'W' if self.dead_white == True else 'B'
        
        return self.dead_group_num

    # 判断能否落子
    def can_play(self, x, y, current_color):
        # 判断量
        canPlay = False
        
        # 基础条件，在棋盘上and这个位置为空位
        if 1 <= x <= self.board_dimension and 1 <= y <= self.board_dimension and self.current_board[x][y] == '.':
            print(current_color)
            self.current_board[x][y] = current_color # 在原有棋局上加上这一颗子
            dead_group_num = self.check_for_dead_groups() # 检查全盘，获取死棋块数
            print('dead_group_num',dead_group_num)
            if dead_group_num == 0: # 0块死棋，没有死棋，能正常落子
                canPlay = True
            elif dead_group_num == 1: # 1块死棋，禁入点，不能落子
                if current_color == self.dead_group_color:
                    canPlay = False
                else:
                    canPlay = True
            elif dead_group_num == 2: # 2块死棋，考虑劫争
                ko_value = self.check_ko() # 获取劫争状态
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

    # 删除对方死子
    def delete_dead_stones(self, opposite_color):
        for x in range(1, self.board_dimension + 1):
            for y in range(1, self.board_dimension + 1):
                if self.dead_groups[x][y] == False and opposite_color == self.current_board[x][y]:
                    print('delete', x, y)
                    
                    self.current_board[x][y] = '.'
    
    # （鼠标点击）位置转化为坐标
    def pos_to_coordinate(self, pos):
        x, y = pos
        
        x += self.cell_edge_len // 2
        y += self.cell_edge_len // 2
        
        x //= self.cell_edge_len
        y //= self.cell_edge_len
        
        return x, y
        

    # 后端落子
    def drop_tile(self, coordinate):
        # 处理棋子位置
        x, y = coordinate
        
        # 判断能否落子，先判断落子，判断落子时记录要删除的位子（死子），正式落子后删除相应位置的子
        if self.can_play(x, y, self.current_color):

            '''
            # 根据模式判定当前棋子的颜色
            if Only_black:
                #print(1)
                self.current_color = 'B'
            elif Only_white:
                #print(2)
                self.current_color = 'W'
            else:
                #print(3)
                # 反转棋子颜色
                self.current_color = 'W' if self.current_color == 'B' else 'B'
            '''
            # 落子
            self.current_board[x][y] = self.current_color
            print('self.current_color',self.current_color)
            # 删去对方的标记的死子
            opposite_color = 'W' if self.current_color == 'B' else 'B'
            self.delete_dead_stones(opposite_color)

            # 在棋子链上记录当前棋子
            new_piece = Chess_Piece(self.current_color, x, y, True) # 创建新棋子
            
            self.cur_pos += 1 # 当前手数+1
            
            if self.cur_pos >= len(self.move_sequence_list):
                self.move_sequence_list.append(new_piece)
            else:
                self.move_sequence_list[self.cur_pos] = new_piece
            
            # 在全局记录上记录当前全盘情况
            self.full_board_log.append(self.current_board)
            
            # 反转棋子颜色
            self.current_color = 'W' if self.current_color == 'B' else 'B'

            
    '''
    # 后端处理前进、后退(基本开发完成)

    def move_backward(self):
        if self.cur_pos - 1 >= 0:
            
            
            self.current_board[self.move_sequence_list[self.cur_pos].x][self.move_sequence_list[self.cur_pos].y] = '.'
            #print(self.cur_pos, self.move_sequence_list[self.cur_pos].x, self.move_sequence_list[self.cur_pos].y)
            self.cur_pos -= 1

    def move_forward(self):
        if self.cur_pos + 1 < len(self.move_sequence_list):
            self.cur_pos += 1
            self.current_board[self.move_sequence_list[self.cur_pos].x][self.move_sequence_list[self.cur_pos].y] = self.move_sequence_list[self.cur_pos].color
            #print(self.cur_pos, self.move_sequence_list[self.cur_pos].x, self.move_sequence_list[self.cur_pos].y)
    '''



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
    cur_Piece_Color.draw_button(game.screen, game.current_color)

    while True:

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # 点击左键
                
                game.drop_tile(game.pos_to_coordinate(event.pos))
                only_Black_Piece_Button.set_only_black(event.pos)
                only_White_Piece_Button.set_only_white(event.pos)
                normal_Mode_Button.set_normal(event.pos)
            '''
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    game.move_backward()
                if event.key == pygame.K_RIGHT:
                    game.move_forward()
            '''    
        
        game.load_background()
        only_Black_Piece_Button.draw_button(game.screen)
        only_White_Piece_Button.draw_button(game.screen)
        normal_Mode_Button.draw_button(game.screen)
        cur_Piece_Color.draw_button(game.screen, game.current_color)
        game.draw_tile()
        pygame.display.flip()