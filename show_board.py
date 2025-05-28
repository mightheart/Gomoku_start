#调用pygame库
import pygame
import numpy as np

class board:
    def __init__(self,board_size):
        self.board_size=board_size
        self.updown_space=int((670-(self.board_size-1)*44)/2)
        self.midlen=int((self.board_size-1)/2)
    def draw_board(self,screen,line_color,over_pos):
        for i in range(self.updown_space,671-self.updown_space,44):
            #先画竖线
            if i==self.updown_space or i==670-self.updown_space:#边缘线稍微粗一些
                pygame.draw.line(screen,line_color,[i,self.updown_space],[i,670-self.updown_space],4)
            else:
                pygame.draw.line(screen,line_color,[i,self.updown_space],[i,670-self.updown_space],2)
            #再画横线
            if i==self.updown_space or i==670-self.updown_space:#边缘线稍微粗一些
                pygame.draw.line(screen,line_color,[self.updown_space,i],[670-self.updown_space,i],4)
            else:
                pygame.draw.line(screen,line_color,[self.updown_space,i],[670-self.updown_space,i],2)

        #在棋盘中心画个小圆表示正中心位置
        pygame.draw.circle(screen, line_color,[self.updown_space+44*self.midlen,self.updown_space+44*self.midlen], 8,0)

        for val in over_pos:#显示所有落下的棋子
            pygame.draw.circle(screen, val[1],val[0], 20,0)

    def check_win(self, over_pos,white_color):  # 判断五子连心
        mp = np.zeros([self.board_size, self.board_size], dtype=int)
        for val in over_pos:
            x = int((val[0][0] - self.updown_space) / 44)
            y = int((val[0][1] - self.updown_space) / 44)
            if val[1] == white_color:
                mp[x][y] = 2  # 表示白子
            else:
                mp[x][y] = 1  # 表示黑子

        for i in range(self.board_size):
            pos1 = []
            pos2 = []
            for j in range(self.board_size):
                if mp[i][j] == 1:
                    pos1.append([i, j])
                else:
                    pos1 = []
                if mp[i][j] == 2:
                    pos2.append([i, j])
                else:
                    pos2 = []
                if len(pos1) >= 5:  # 五子连心
                    return [1, pos1]
                if len(pos2) >= 5:
                    return [2, pos2]

        for j in range(self.board_size):
            pos1 = []
            pos2 = []
            for i in range(self.board_size):
                if mp[i][j] == 1:
                    pos1.append([i, j])
                else:
                    pos1 = []
                if mp[i][j] == 2:
                    pos2.append([i, j])
                else:
                    pos2 = []
                if len(pos1) >= 5:
                    return [1, pos1]
                if len(pos2) >= 5:
                    return [2, pos2]
        for i in range(self.board_size):
            for j in range(self.board_size):
                pos1 = []
                pos2 = []
                for k in range(self.board_size):
                    if i + k >= self.board_size or j + k >= self.board_size:
                        break
                    if mp[i + k][j + k] == 1:
                        pos1.append([i + k, j + k])
                    else:
                        pos1 = []
                    if mp[i + k][j + k] == 2:
                        pos2.append([i + k, j + k])
                    else:
                        pos2 = []
                    if len(pos1) >= 5:
                        return [1, pos1]
                    if len(pos2) >= 5:
                        return [2, pos2]
        for i in range(self.board_size):
            for j in range(self.board_size):
                pos1 = []
                pos2 = []
                for k in range(self.board_size):
                    if i + k >= self.board_size or j - k < 0:
                        break
                    if mp[i + k][j - k] == 1:
                        pos1.append([i + k, j - k])
                    else:
                        pos1 = []
                    if mp[i + k][j - k] == 2:
                        pos2.append([i + k, j - k])
                    else:
                        pos2 = []
                    if len(pos1) >= 5:
                        return [1, pos1]
                    if len(pos2) >= 5:
                        return [2, pos2]
        return [0, []]

    def find_pos(self,x, y):  # 找到显示的可以落子的位置
        for i in range(self.updown_space, 671 - self.updown_space, 44):
            for j in range(self.updown_space, 671 - self.updown_space, 44):
                L1 = i - 22
                L2 = i + 22
                R1 = j - 22
                R2 = j + 22
                if x >= L1 and x <= L2 and y >= R1 and y <= R2:
                    return i, j

        return x, y

    def check_over_pos(self,x, y, over_pos):  # 检查当前的位置是否已经落子
        for val in over_pos:
            if val[0][0] == x and val[0][1] == y:
                return False
        return True  # 表示没有落子