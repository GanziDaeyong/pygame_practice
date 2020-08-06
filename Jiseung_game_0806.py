#!/usr/bin/env python
# coding: utf-8

# In[ ]:


"""
해당 코드는 옥수별 님의 블로그 (https://m.blog.naver.com/samsjang/220706335386) 와 pygame 튜토리얼 페이지 (https://www.pygame.org/wiki/tutorials) 를 기반으로 작성되었다. 해당 게임에 등장하는 모든 이미지와 효과음은 저작권을 위반하지 않고, 적법한 경로로 가져왔기에 문제 소지가 없다.  

게임 제목: 바보 지승이의 비행기(記)
게임 장르: 2d 슈팅게임
게임 설명: 방향키를 통해 지승이를 위아래로 움직이며 LCTRL을 눌러 하트를 발사한다. 누멍이(강아지)를 하트로 맞춰야 하며, 4번 이상 누멍이를 놓칠 시 게임오버된다. 병아리는 맞출 수 없고 무조건 피해야 하며, 누멍이와 병아리 모두 지승이와 부딪히면 게임오버된다. 놓친 누멍이 수는 화면 좌상단에 표시된다.
최종 업데이트: 200719
"""


import pygame
import random
import time

WHITE = (255,255,255)
RED = (255,0,0) #RGB 로 들어간다
BLUE = (0,0,255)
BLACK = (0,0,0)
GREEN = (0, 255, 0)
pad_width = 1024
pad_height = 512
background_width = 1024
numung_width = 88
numung_height = 100
aircraft_width = 150
aircraft_height = 100
chick_width = 75
chick_height = 85

# 각 변수를 소스 연동부터 좌표 설정, 랜더링, 화면에 표시까지 다양한 작업을 거쳐야 하므로, global을 이용해 전역변수로 선언해주었다. 


def draw_score(count_miss, count_caught, life_left):
    global gamepad
    font = pygame.font.SysFont("malgungothic", 15 ) #인자 순서는 다음과 같음 SysFont(name, size, bold=False, italic=False)
    count_miss_score = font.render( " 누멍이 " + str(count_miss) + " 마리가 도망갔다!", True, RED) # 점수에 들어갈 내용을 작성한다. 인자 순서는 다음과 같음 render(text, antialias, color, background=None)
    count_caught_score = font.render(" 누멍이 " + str(count_caught) + " 마리를 포획했다!", True, BLUE)
    life_left_num = font.render(" 남은 반창고 수 : " + str(life_left), True, GREEN)
    gamepad.blit(count_miss_score,(0,0)) # 점수를 랜더링해준다.    
    gamepad.blit(count_caught_score,(0,22))
    gamepad.blit(life_left_num, (0, 44))
    
    
def game_over():
    global gamepad
    disp_msg("지숭이는 놓친 누멍이를 찾으러 집으로 돌아갔답니다!", BLUE)
    time.sleep(2)
    runGame()

def disp_msg(text,color,loc = 0):
    global gamepad
    
    large_text = pygame.font.SysFont("malgungothic", 20) # 폰트와 글씨 크기를 지정한다.freesansbold.ttf
    text_surf = large_text.render(text, True, color) # 텍스트를 surface 형으로. 인자순서는 위 참고
    text_rect = text_surf.get_rect() #.get_rect() 는 컨텐츠가 들어갈 칸을 만들어준다.
    text_rect.center = ((pad_width/2), (pad_height/2) + loc) # 화면의 중간에 글씨 칸을 만든다.
    gamepad.blit(text_surf, text_rect) #.blit는 대상을 렌더링해준다. heavy한 함수로, 한 프레임에 적절히 넣도록 한다. 너무 많이 blit을 우겨넣으면 프레임드랍/ 과부하 생긴다.
    pygame.display.update() # 랜더링 된 대상을 최종적으로 모니터에 띄워준다.
    time.sleep(1) # 메세지 표시 후 2초간 텀을 둔다.
    
def draw_object(obj, x, y):
    global gamepad
    gamepad.blit(obj,(x,y)) # 매번 gamepad.blit과 x축, y축을 써주어도 되지만, 편의성을 위해 한번에 draw_object(obj, x, y) 를 입력하도록 했다. .blit 보다 추가적인 기능은 없다.

def runGame():
    global gamepad, aircraft, clock, background1, background2 
    global numung, chicks, bullet, flip
    global shot_sound
    
    is_shot_numung = False # 적(누멍이)이 맞았을 때를 False로 초기화시켜준다.
    flip_count = 0 # 적을 맞춘 횟수를 초기화시켜준다. 
    count_miss = 0 # 적이 맞지 않고 지나간 횟수를 초기화시켜준다.
    count_caught = 0 # 적이 맞춘 횟수를 초기화시켜준다. - 점수표시용
    life_left = 3
    
    bullet_xy = [] # 총알의 좌표를 초기화시켜준다.
    
    x = pad_width * 0.01 # 아직 대상이 설정되진 않았다. 좌로부터 게임판의 0.01에 해당하는 위치이다.  
    y = pad_height * 0.8 # 아직 대상이 설정되진 않았다. 위로부터 게임판의 0.8배에 해당하는 위치.
    y_change = 0 # y축의 이동을 0으로 초기화시켜준다. 
    
    background1_x = 0 # 배경을 반복하기 위해 1과 2로 나누고, 배경 1 은 화면 왼쪽 끝부터 채워지게 한다.
    background2_x = background_width # 배경 2는 배경 폭의 끝, 즉 화면 오른쪽 끝부터 채워지게 함으로써 배경 1에 바로 이어지게 한다. 
    
    numung_x = pad_width # 적(누멍이)의 x 좌표를 게임판 우측 끝으로 설정한다.
    numung_y = random.randrange(0, pad_height) # 적의 y 좌표가 0부터 게임판 높이까지 랜덤하게 생성되도록 한다. 
    chick_x = pad_width # 병아리의 x 좌표를 게임판 우측 끝으로 설정한다. 
    chick_y = random.randrange(0, pad_height) # 병아리의 y 좌표가 0부터 게임판 높이까지 랜덤하게 생성되도록 한다.
    random.shuffle(chicks) # 밑에 등장한다. 병아리는 None이 될 수도 있고 등장할수도 있다. None과 등장하는 경우를 여러개 만들어 섞는 과정이다.
    chick = chicks[0] # chicks에는 None과 등장하는 경우가 뒤섞여있는데, 이 중 첫번째 요소를 선택한다. 쉽게 말하면 그냥 죄다 뒤섞은다음에 하나 선택하는 것. 그러니 꼭 첫번째가 아니어도 된다.
    
    crashed = False # 충돌하지 않은 경우 (게임오버되지 않은 경우)
    while not crashed: # 충돌이 아니면 계속 while문 돌아라.
        for event in pygame.event.get(): # pygame.event.get()를 통해 입력에 대한 반응을 설정한다.
            if event.type == pygame.QUIT: # 만약 event.type이 게임 종료라면 (우상단 x 버튼)
                crashed = True # 충돌은 참이다.여기서 충돌은 게임이 중단된다는 의미이다.
                
            if event.type == pygame.KEYDOWN: # .KEYDOWN 키가 눌려있을 때 반복적으로 수행한다.
                if event.key == pygame.K_UP: # 방향키 위를 누르면
                    y_change = -5 # y 좌표가 -7만큼 이동.(위로 이동)
                    # @중요@ pygame에서 x좌표는 좌에서 우로, y좌표는 상에서 하로 증가한다. 방향 주의.
                elif event.key == pygame.K_DOWN: # 방향키 아래를 누르면
                    y_change = 5 # y 좌표가 +7만큼 이동. (아래로 이동)
                elif event.key == pygame.K_LCTRL: # LCTRL을 누르면
                    pygame.mixer.Sound.play(shot_sound) # 총 소리를 재생한다.
                    bullet_x = x + aircraft_width # 총알의 x좌표는 비행기 폭 + 위에서 정의한 x좌표값.
                    bullet_y = y + aircraft_height/2 # 총알의 y좌표는 비행기 높이/2 (비행기 중간에서 나가니까) + 위에서 정의한 y 좌표값.
                    bullet_xy.append([bullet_x,bullet_y]) # 총알 좌표에 x좌표, y좌표를 각각 추가한다. 
            
            if event.type == pygame.KEYUP: # .KEYUP 키가 떨어졌을 때 수행한다.
                if event.key == pygame.K_UP or event.key == pygame.K_DOWN: # 방향키 떼더라도
                    y_change = 0 # 변화가 없게 한다. 
        
        #게임판 초기화
        gamepad.fill(WHITE) # 게임판을 흰색 배경으로 채운다.
        
        #배경 구현
        background1_x -= 2 # 배경이 우->좌 방향으로 2씩 움직이게 한다. (x축은 좌->우 가 기준이므로 -가 붙는다.)
        background2_x -= 2 
        
        if background1_x == -background_width: # 만약 배경1이 전부 지나가면 (-배경폭과 같아지면)
            background1_x = background_width # 원래 배경 위치로 리셋시킨다.
            
        if background2_x == -background_width: # 만약 배경2가 전부 지나가면
            background2_x = background_width # 원래 배경 위치로 리셋시킨다.
            
# 위에서 배경 1 뒤에 배경 2가 이어졌으므로 배경1 -> 배경2 -> 배경1 -> 배경2 로 반복되는 구조이다.
            
        draw_object(background1, background1_x, 0) # 배경 구현해준다. y축은 변동없으므로 0부터 시작.
        draw_object(background2, background2_x, 0)

        draw_score(count_miss, count_caught, life_left) # 적을 놓친 횟수 (점수) 를 구현해준다.
        draw_object(aircraft, x,y) # x좌표, y좌표에 비행기를 구현한다.
    
        if count_miss > 3 : # 만약 적을 3회 초과 놓쳤다면,
            game_over() # 게임오버된다.
        
        #비행기 위치설정
        y += y_change # 비행기 위치는 키 값에 따른 y_change의 누적으로 한다.
        
        if y < -80 : # y가 -80보다 작아지지 않도록 이동 범위를 고정한다. 
            y = -80 # 0으로 설정하면 비행기 상단이 화면 위쪽 끝에 닿게 된다. 나는 비행기 크기를 크게 하여 0으로 하면 이동 범위가 너무 작아져 화면 높이를 좀 크게 했다. 자꾸 강조하지만, pygame에서 y축은 위에서 아래로 증가한다. 즉, -80이면 화면 위쪽에서 오히려 80만큼 위로 이동한 꼴이 되는 것이다.  
            
        elif y > (pad_height+20) - aircraft_height: # y가 (게임판 높이 - 비행기 높이) 보다 커지지 않도록 이동 범위를 고정한다.  
            y = (pad_height+20) - aircraft_height # 위에서와 같은 이유로 + 20을 하여 이동 범위를 화면을 조금 벗어나도 되도록 설정하였다.
            
        #적(누멍이) 위치설정
        numung_x -= 7 # 적(누멍이)가 왼쪽으로 7프레임씩 이동하도록
        if numung_x <= 0: # 만약 적의 x좌표가 0보다 작아지면 화면 밖을 벗어난 것이므로
            count_miss += 1 # 놓친 적 수에 +1 한다.
            numung_x = pad_width # 그 적은 다시 오른쪽 끝으로 위치 초기화시켜준다.
            numung_y = random.randrange(40, pad_height + 40) # 적의 y 좌표는 40 부터 게임판 높이의 + 40까지로 한다. 적 크기가 있으므로 40을 각각 더해줘야 깔끔하게 화면에 나타나더라.
        
        #병아리 위치설정
        if chick[1] == None: # chick[0] 은 병아리 종류 식별자로 사용된다. (병아리 종류를 2개 이상으로 하는 경우) 병아리[1] 이 없으면
            chick_x -= 13 # 병아리가 없으면 -10의 속도로 진행한다. 단순히 시간 늦추기 용도이다.
        else:
            chick_x -= 10 # 병아리가 있으면 -7의 속도로 진행한다.
        
        if chick_x <= 0: # 병아리가 화면 끝에 도달하면
            chick_x = pad_width # 다시 오른쪽 끝으로 위치 초기화시켜준다.
            chick_y = random.randrange(0, pad_height) # y축은 0부터 게임판 높이까지 랜덤생성한다.
            random.shuffle(chicks) # 병아리들 리스트에 None과 등장하는 경우를 랜덤하게 섞는다.
            chick = chicks[0] # 리스트 첫 번째 요소를 병아리 변수로 받는다. 그냥 랜덤으로 뽑는 방법.
        
        #bullets position
        if len(bullet_xy) != 0 : # LCTRL을 눌러 총알 좌표가 생성되면
            for i, bxy in enumerate(bullet_xy): # 총알 좌표를 enumerate 하여
                bxy[0] += 15 # 총알의 x 좌표를 15씩 이동시킨다. 여기서 bxy는 직관적으로 코드를 구성하기위해 설정한 변수이다. 바로 bullet_xy[i][n]를 이용해서 코드를 짜도 무방하다.
                bullet_xy[i][0] = bxy[0] # i번째 총알의 x좌표 ([1]은 y좌표)를 bxy[0] 과 이어준다.
                if bxy[0] > numung_x: # 만약 총알 x 좌표가 적 x 좌표를 지나고,
                    if bxy[1] > numung_y and bxy[1] < numung_y + numung_height : # 총알 y 좌표가 적의 y 좌표에 해당하는 범위에 닿으면
                        bullet_xy.remove(bxy) # 해당 총알을 제거한다.
                        is_shot_numung = True # 그리고 적이 맞은 경우를 True로 바꿔준다.
                        count_caught += 1
                
                if bxy[0] >= pad_width: # 만약 총알의 x좌표가 게임판의 끝에 도달하면
                    try:
                        bullet_xy.remove(bxy) # 해당 총알을 제거한다.
                    except:
                        pass # 예외는 그냥 pass로 흘려준다.
                    
        # check aircraft crashed by Numung
        if x + aircraft_width > numung_x: # 비행기의 폭 + x 좌표가 적의 x 좌표에 닿으면
            if (y > numung_y and y < numung_y + numung_height) or (y + aircraft_height > numung_y and y + aircraft_height < numung_y + numung_height): # 비행기의 y 좌표가 적의 y 좌표에 해당하는 범위에 닿으면abs
                disp_msg("지숭이가 누멍이와 부딪혀 다쳤습니다 ㅠㅠ", RED) 
                life_left -= 1
                
                #crash() # 위에서 정의한 충돌 함수를 실행한다.
                numung_x = pad_width # 그 적은 다시 오른쪽 끝으로 위치 초기화시켜준다.
                numung_y = random.randrange(40, pad_height + 40)
                
        
        # check aircraft crashed by Chick
        if chick[1] != None: # 만약 병아리가 존재한다면
            if x + aircraft_width > chick_x: # 위와 같다. 비행기의 x좌표, y 좌표가 병아리에 닿으면
                if (y > chick_y and y < chick_y + chick_height) or (y + aircraft_height > chick_y and y + aircraft_height < chick_y + chick_height):
                    disp_msg("지숭이가 병아리와 부딪혀 다쳤습니다 ㅠㅠ", RED)
                    life_left -= 1
                    #crash() # 충돌엔딩.
                    chick_x = pad_width # 다시 오른쪽 끝으로 위치 초기화시켜준다.
                    chick_y = random.randrange(0, pad_height) # y축은 0부터 게임판 높이까지 랜덤생성한다.
                    random.shuffle(chicks) # 병아리들 리스트에 None과 등장하는 경우를 랜덤하게 섞는다.
                    chick = chicks[0] 
                           
        #draw_object(aircraft, x,y) # x좌표, y좌표에 비행기를 구현한다.
        
        if len(bullet_xy) != 0: # 만약 총알이 있으면 
            for bx, by in bullet_xy: # 총알의 x, y 좌표를 bx, by로 두고, 
                draw_object(bullet, bx, by) # 총알을 구현한다.
        
        if not is_shot_numung: # 만약 적이 맞지 않았다면
            draw_object(numung, numung_x, numung_y +40) # x, y 좌표로 적을 구현한다. 나의 경우 적 크기때문에 + 40을 해줘야 정확한 히트박스가 형성되더라.
        else:
            pygame.mixer.Sound.play(flip_sound) # 만약 적이 맞았다면
            draw_object(flip, numung_x, numung_y) # 적이 죽는 모션을 구현한다.
            #count_caught += 1
            flip_count += 1 # 적이 쓰러진 횟수 += 1
            if flip_count > 5: # 만약 적을 5회 이상 쓰러뜨리면,
                flip_count = 0 # 이를 초기화시켜준다. 그냥 게임을 light 하게 만들기 위해서이다.
                numung_x = pad_width # 적 x 좌표를 게임판 맨 끝으로 초기화시켜준다.
                numung_y = random.randrange(0, pad_height - numung_height) # 높이는 역시 랜덤으로.
                is_shot_numung = False # 적이 맞았는가? False.
                
        if chick[1] != None: # 병아리가 존재한다면
            draw_object(chick[1], chick_x, chick_y + 37) # 병아리를 구현해준다. 역시 크기와 히트박스 때문에 +37을 해주었다.
        
        if life_left < 0 :
            disp_msg("지숭이는 아파서 집으로 돌아갔습니다..", BLUE, loc = 30)
            runGame()
        
        pygame.display.update() # 랜더링(draw_object) 된 물체들을 전부 모니터에 띄워준다.
        clock.tick(60) # 초당 60번씩. 60프레임 개념.
    pygame.quit() # 게임 종료
    quit()

def initGame():
    global gamepad, aircraft, clock, background1, background2
    global numung, chicks, bullet, flip
    global shot_sound, flip_sound
    
    # 소리 소스 연동시켜준다.
    shot_sound = pygame.mixer.Sound(r"C:\Users\iwin1\Desktop\cs_portfolio\python_game\shot.wav")
    flip_sound = pygame.mixer.Sound(r"C:\Users\iwin1\Desktop\cs_portfolio\python_game\flip.wav")
    
    chicks = []
    
    pygame.init()
    gamepad = pygame.display.set_mode((pad_width, pad_height)) #게임판 폭, 높이로 gamepad를 선언해준다.
    # 이미지 소스를 연동시켜준다.
    pygame.display.set_caption("바보 지숭이의 비행기!") # 제목 만들기
    aircraft = pygame.image.load(r"C:\Users\iwin1\Desktop\cs_portfolio\python_game\최종_비행기.png")
    background1 = pygame.image.load(r"C:\Users\iwin1\Desktop\cs_portfolio\python_game\배경.png")
    background2 = background1.copy()
    numung = pygame.image.load(r"C:\Users\iwin1\Desktop\cs_portfolio\python_game\최종_누멍이달리기.png")
    chicks.append((0, pygame.image.load(r"C:\Users\iwin1\Desktop\cs_portfolio\python_game\최종_병아리.png")))
    flip = pygame.image.load(r"C:\Users\iwin1\Desktop\cs_portfolio\python_game\누멍이피격모션.png")
    
    for i in range (3) :
        chicks.append((i+2, None))
# 병아리를 3번마다 None으로 설정하여 75퍼센트의 확률을 구현한다. 
        
    bullet = pygame.image.load(r"C:\Users\iwin1\Desktop\cs_portfolio\python_game\bullet.png")
    clock = pygame.time.Clock()
    runGame()

if __name__ == "__main__":
    pygame.mixer.init() # 이건 일부 wav, mp3 파일에서 init()을 못시키는 오류가 발생하여 추가해주었다. 굳이 안해도 됨.
    initGame()


# In[ ]:





# In[ ]:




