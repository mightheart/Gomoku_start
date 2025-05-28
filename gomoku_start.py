#调用pygame库
import pygame
import sys
#调用常用关键字常量
from pygame.locals import QUIT,KEYDOWN,MOUSEBUTTONDOWN
from show_board import board

# 新增游戏状态常量
GAME_STATES = ['start', 'choose_board', 'playing']
current_state = 'start'
selected_size = 11  # 默认尺寸



def draw_start_screen():
    screen.fill([238, 154, 73])
    # 绘制标题
    font = pygame.font.Font(None, 100)
    title = font.render("GOMOKU", True, [0, 0, 0])
    screen.blit(title, (180, 200))

    # 绘制开始按钮
    pygame.draw.rect(screen, [144, 238, 144], [240, 350, 180, 60])
    font = pygame.font.Font(None, 50)
    start_txt = font.render("START", True, [0, 0, 0])
    screen.blit(start_txt, (275, 365))

    # 绘制退出按钮
    pygame.draw.rect(screen, [255, 99, 71], [240, 450, 180, 60])
    quit_txt = font.render("EXIT", True, [0, 0, 0])
    screen.blit(quit_txt, (275, 465))


def draw_board_choice():
    screen.fill([238, 154, 73])
    font = pygame.font.Font(None, 80)
    title = font.render("Choose Size", True, [0, 0, 0])
    screen.blit(title, (180, 150))

    # 绘制三个尺寸按钮
    btn_props = [
        (15, "15x15", [255, 215, 0]),
        (13, "13x13", [135, 206, 235]),
        (11, "11x11", [147, 112, 219])
    ]

    y = 280
    for size, text, color in btn_props:
        pygame.draw.rect(screen, color, [220, y, 240, 60])
        txt = font.render(text, True, [0, 0, 0])
        screen.blit(txt, (250, y + 10))
        y += 100



#初始化pygame
pygame.init()
#获取对显示系统的访问，并创建一个窗口screen
#窗口大小为670x670
screen = pygame.display.set_mode((670,670))
pygame.display.set_caption("Gomoku")
screen_color=[238,154,73]#设置画布颜色,[238,154,73]对应为棕黄色
line_color = [0,0,0]#设置线条颜色，[0,0,0]对应黑色



over_pos=[]#表示已经落子的位置
white_color=[255,255,255]#白棋颜色
black_color=[0,0,0]#黑棋颜色

while True:#不断训练刷新画布

    # 处理事件
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()

        # 处理鼠标点击
        if event.type == MOUSEBUTTONDOWN and event.button == 1:
            x, y = event.pos

            # 开始界面逻辑
            if current_state == 'start':
                # 点击开始按钮
                if 240 <= x <= 440 and 350 <= y <= 410:
                    current_state = 'choose_board'
                # 点击退出按钮
                elif 240 <= x <= 440 and 450 <= y <= 510:
                    pygame.quit()
                    sys.exit()

            # 选择棋盘界面逻辑
            elif current_state == 'choose_board':
                if 220 <= x <= 460:
                    if 280 <= y <= 340:  # 15x15
                        selected_size = 15
                        current_state = 'playing'
                    elif 380 <= y <= 440:  # 13x13
                        selected_size = 13
                        current_state = 'playing'
                    elif 480 <= y <= 540:  # 11x11
                        selected_size = 11
                        current_state = 'playing'

    # 根据状态绘制界面
    if current_state == 'start':
        draw_start_screen()
    elif current_state == 'choose_board':
        draw_board_choice()
    elif current_state == 'playing':

        myboard = board(selected_size)
        updown_space = myboard.updown_space
        screen.fill(screen_color)#清屏
        #画棋盘
        myboard.draw_board(screen,line_color,over_pos)
        #判断是否存在五子连心
        res=myboard.check_win(over_pos,white_color)
        if res[0]!=0:
            for pos in res[1]:
                pygame.draw.rect(screen,[238,48,167],[pos[0]*44+updown_space-22,pos[1]*44+updown_space-22,44,44],2,1)
            pygame.display.update()#刷新显示
            continue#游戏结束，停止下面的操作
        #获取鼠标坐标信息
        x,y = pygame.mouse.get_pos()

        x,y=myboard.find_pos(x,y)
        if x >= updown_space and x <= 670 - updown_space and y >= updown_space and y <= 670 - updown_space:
            if myboard.check_over_pos(x,y,over_pos):#判断是否可以落子，再显示
                pygame.draw.rect(screen,[0 ,229 ,238 ],[x-22,y-22,44,44],2,1)

                for event in pygame.event.get():
                    if event.type == MOUSEBUTTONDOWN and event.button == 1:
                        if myboard.check_over_pos(x,y,over_pos):#判断是否可以落子，再落子
                            if len(over_pos)%2==0:#黑子
                                over_pos.append([[x,y],black_color])
                            else:
                                over_pos.append([[x,y],white_color])


    pygame.display.update()#刷新显示

