import pygame
import sys
import os
import random
import math

# === 1. 配置与初始化函数 ===
def main():
    pygame.init()
    # 初始化混音器（必须在音乐播放前）
    pygame.mixer.init()
    LOGIC_W, LOGIC_H = 3200, 1800
    win_w, win_h = 1600, 900

    screen = pygame.display.set_mode((win_w, win_h), pygame.RESIZABLE)
    canvas = pygame.Surface((LOGIC_W, LOGIC_H))
    title="变异狂潮-十周年纪念版demo"
    pygame.display.set_caption(title)
    icon_img = pygame.image.load("codemao/r-logo.png").convert_alpha() 
    pygame.display.set_icon(icon_img)
    show1 = False
    alpha = 0
    developer_mode = True  # 开发者模式开关


    def load(file,x=None,y=None):#加载图片并根据参数调整大小
        '''
        :param file:图片路径
        :param x:物品长度
        :param y:物品宽度
        '''
        if os.path.exists(file):
            try:
                img = pygame.image.load(file).convert_alpha()
                width = img.get_width()   # 获取宽度
                height = img.get_height() # 获取高度
                ratio = height / width  # 计算宽高比
                if x is None:
                    img = pygame.transform.scale(img, (int(y/ratio), y ))
                elif y is None:
                    img = pygame.transform.scale(img, (x, int(x*ratio)))
                elif x is not None and y is not None:
                    img = pygame.transform.scale(img, (x, y))
                return img
            except:
                print(f"Error loading image: {file}")
    def center(img,x,y):#定义图片居中绘制
        rect = img.get_rect()
        rect.center = (x, y)
        return rect
    def draw_health_bar(surface, x, y, current_hp, max_hp,delay):
        bar_width = 230    # 血条总长度（像素）
        bar_height = 28    # 血条高度
        ratio = max(0, min(current_hp / max_hp, 1))
        ratio2 = max(0, min(delay / max_hp, 1))
        pygame.draw.rect(surface, (30, 30, 30), (x, y, bar_width, bar_height))
        pygame.draw.rect(surface, (255, 255, 255), (x, y, int(bar_width * ratio2), bar_height))
        color = (42, 174, 42) if ratio > 0.5 else (218, 165, 32) if ratio > 0.2 else (178, 34, 34)
        pygame.draw.rect(surface, color, (x, y, int(bar_width * ratio), bar_height))
        pygame.draw.rect(surface, (100, 100, 100), (x, y, bar_width, bar_height), 2)
        # 创建一个带 Alpha 的临时 Surface 来画半透明高光
        highlight_surf = pygame.Surface((int(bar_width * ratio), bar_height // 2), pygame.SRCALPHA)
        highlight_surf.fill((255, 255, 255, 40)) # 最后一个值 40 是透明度，非常淡
        surface.blit(highlight_surf, (x, y))

    def load_ls(file,x=None,y=None):#加载图片并根据参数调整大小
        '''
        :param file:图片路径
        :param x:物品长度
        :param y:物品宽度
        '''
        ls=[]
        for i in file:
            if os.path.exists(i):
                try:
                    img = pygame.image.load(i).convert_alpha()
                    width = img.get_width()   # 获取宽度
                    height = img.get_height() # 获取高度
                    ratio = height / width  # 计算宽高比
                    if x is None:
                        img = pygame.transform.scale(img, (int(y/ratio), y ))
                    elif y is None:
                        img = pygame.transform.scale(img, (x, int(x*ratio)))
                    elif x is not None and y is not None:
                        img = pygame.transform.scale(img, (x, y))
                    ls.append(img)
                    return ls
                except:
                    print(f"Error loading image: {i}")


    def get_font(size):
        return pygame.font.SysFont(["wqy-microhei", "notosanscjksc", "simhei", "sans-serif"], size)

    title_font = get_font(100)
    ui_font = get_font(40)
    clock = pygame.time.Clock()

    # --- 2. 资源加载与处理 ---

    hit_cooldown = 300 # 被撞后无敌时间（毫秒）

    # 背景音乐加载
    bgm_path = "codemao/music/bgm.mp3"
    bgm_path2 = "codemao/music/bgm2.mp3"
    #title_img图片加载
    title_img = pygame.image.load("codemao/UI/Byzomb.png").convert_alpha()
    title_img = pygame.transform.scale(title_img, (1716, 500))
    #加载围栏
    move_x =5750
    move_y =(96/230)*move_x  #可移动距离大小
    # 开始按钮图片加载
    # 按钮尺寸（根据你的图片实际大小调整）
    BTN_W, BTN_H = 912.5, 322.5

    # 加载开始按钮
    btn_normal = load(file="codemao/UI/buttun1.png",x=BTN_W,y=BTN_H)
    btn_hover = load(file="codemao/UI/buttun2.png",x=BTN_W,y=BTN_H)

    #加载帮助按钮
    btn_help_normal = load(file="codemao/UI/help1.png",x=BTN_W,y=BTN_H)
    btn_help_hover = load(file="codemao/UI/help2.png",x=BTN_W,y=BTN_H)
    btn_close_normal = load(file="codemao/UI/close1.png",x=100)
    btn_close_hover = load(file="codemao/UI/close2.png",x=100)
    help_paper = load(file="codemao/UI/help_page2.png",x=3000)
    rec=load(file="codemao/UI/rec.png",x=190) #换弹药

    #加载围栏
    fence=pygame.image.load("codemao/Fence.png").convert_alpha()
    fence= pygame.transform.scale(fence, (move_x, (61/1128)*move_x))
    #加载树林
    tree1=load(file="codemao/tree1.png",y=int(move_y+800)) #左树
    tree2=load(file="codemao/tree2.png",y=int(move_y+3700)) #右树
    wall=load(file="codemao/wall.png",y=int(move_y+1600)) #墙
    wall_life=load(file="codemao/wall_life.png",x=450) #墙血量
    open_bar=load_ls(file=["codemao/open1.png","codemao/open2.png","codemao/open3.png"],y=50) #开箱子进度条
    weapon1=load_ls(file=["codemao/weapon/mondragon.png"],x=320) #武器1
    weapon2=weapon1
    grave=load(file="codemao/grave.png",y=220) #墓碑
    
    def move_item(img,x,y):#定义动类型物品绘制
        item_draw_x = x + cam_x
        item_draw_y = y + cam_y
        canvas.blit(img, (item_draw_x, item_draw_y))
    def static_item(img,x,y):#定义动类型物品绘制
        canvas.blit(img, (x,y))
    
    # 角色动画加载
    PLAYER_SIZE = 200
    ANIM_SPEED = 20 
    player_frames = []
    p_files = ["codemao/player1.png", "codemao/player2.png"] 

    for f in p_files:
        if os.path.exists(f):
            img = pygame.image.load(f).convert_alpha()
            player_frames.append(pygame.transform.scale(img, (PLAYER_SIZE, PLAYER_SIZE*(7/8))))
        else:
            s = pygame.Surface((PLAYER_SIZE, PLAYER_SIZE))
            s.fill((255, 0, 0) if "1" in f else (255, 100, 0))
            player_frames.append(s)

    # 敌人动画加载
    ENEMY_SIZE = 215
    ENEMY_ANIM_SPEED = 30 
    enemy_frames = []
    e_files = ["codemao/zombie/zombie1.png", "codemao/zombie/zombie2.png"]

    for i, f in enumerate(e_files):
        if os.path.exists(f):
            try:
                img = pygame.image.load(f).convert_alpha()
                enemy_frames.append(pygame.transform.scale(img, (ENEMY_SIZE, ENEMY_SIZE)))
            except: pass
        if len(enemy_frames) <= i:
            s = pygame.Surface((ENEMY_SIZE, ENEMY_SIZE))
            color = (200, 0, 0) if i == 0 else (255, 80, 0)
            s.fill(color)
            enemy_frames.append(s)

    # 背景加载
    TILE_W = 2800
    TILE_H = int(TILE_W * (9 / 16)) 
    tile_img2 = pygame.Surface((TILE_W, TILE_H))
    tile_img2.fill((34, 139, 34)) 

    if os.path.exists("codemao/background2.png"):
        try:
            raw_tile = pygame.image.load("codemao/background2.png").convert()
            tile_img2 = pygame.transform.scale(raw_tile, (TILE_W, TILE_H))
        except: pass
    
    if os.path.exists("codemao/background3.png"):
        try:
            raw_tile3 = pygame.image.load("codemao/background3.png").convert()
            tile_img3 = pygame.transform.scale(raw_tile3, (TILE_W, TILE_H))
        except: pass

    # --- 3. 游戏状态变量 ---
    scene = 'MENU'
    WORLD_WIDTH, WORLD_HEIGHT = move_x, move_y
    player_world_x, player_world_y = WORLD_WIDTH // 2, WORLD_HEIGHT // 2
    player_speed = 50
    frame_counter = 0 

    # 缩放相关变量
    nonlocal_current_scale = 1.0
    nonlocal_current_offset = (0, 0)

    # 敌人管理
    enemies = [] 
    ENEMY_SPEED = 12
    SPAWN_RATE = 120 

    # --- 4. 工具函数 (在main内部以访问变量) ---
    def get_logic_mouse():
        m_x, m_y = pygame.mouse.get_pos()
        return (m_x - nonlocal_current_offset[0]) / nonlocal_current_scale, (m_y - nonlocal_current_offset[1]) / nonlocal_current_scale

    def draw_btn(text, x, y, w, h, color):
        l_mx, l_my = get_logic_mouse()
        is_hover = x < l_mx < x + w and y < l_my < y + h
        c = [min(i+40, 255) for i in color] if is_hover else color
        pygame.draw.rect(canvas, c, (x, y, w, h), border_radius=15)
        txt = ui_font.render(text, True, (255, 255, 255))
        canvas.blit(txt, txt.get_rect(center=(x + w/2, y + h/2)))
        return is_hover and pygame.mouse.get_pressed()[0]
    def btn(img_normal, img_hover, x, y):
        # 1. 获取逻辑鼠标位置
        l_mx, l_my = get_logic_mouse()
        # 2. 获取图片矩形区域用于碰撞检测
        rect = img_normal.get_rect(topleft=(x, y))
        is_hover = rect.collidepoint(l_mx, l_my)
        curr_img = img_hover if is_hover else img_normal
        canvas.blit(curr_img, (x, y))
        
        # 5. 返回是否被点击
        return is_hover and pygame.mouse.get_pressed()[0]

    # --- 5. 主循环 ---
    while True:
        frame_counter += 1 
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.VIDEORESIZE:
                screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
            if event.type == pygame.KEYDOWN:
                if scene == 'GAME'and player_hp > 0 and wall_hp > 0:
                    if event.key == pygame.K_r: #换弹
                        add_hp+=5

        canvas.fill((0, 0, 0))

        if scene == 'MENU':
            if pygame.mixer.music.get_busy():
                pass
            else:
                if os.path.exists(bgm_path2):
                    pygame.mixer.music.load(bgm_path2)
                    pygame.mixer.music.set_volume(0.6) # 设置音量
                    pygame.mixer.music.play(-1) # 循环播放音乐

            # 背景渲染
            offset_x = (LOGIC_W//2 - (player_world_x + PLAYER_SIZE//2)) % TILE_W
            offset_y = (LOGIC_H//2 - (player_world_y + PLAYER_SIZE//2)) % TILE_H
            for x in range(-TILE_W, LOGIC_W + TILE_W, TILE_W):
                for y in range(-TILE_H, LOGIC_H + TILE_H, TILE_H):
                    canvas.blit(tile_img2, (x + offset_x, y + offset_y))
            title_x = LOGIC_W // 2 - title_img.get_width() // 2
            title_y = 200  # 距离顶部 200 像素
            canvas.blit(title_img, (title_x, title_y))
            btn_x = LOGIC_W // 2 - BTN_W // 2
            btn_y = LOGIC_H // 2
            if btn(btn_normal, btn_hover, btn_x, btn_y-100):
                scene = 'GAME'
                enemies = [] # 重置敌人
                player_hp = 100 # 重置血量
                wall_hp = 100 # 重置墙血量
                last_hit_time = 0 # 重置被撞时间戳
                p_idx=0
                delay_hp=100 #掉血动画用的延迟血量
                wall_delay_hp=100 #墙掉血动画用的延迟血量
                add_hp=0
                reload_data = {#弹药系统预留
                    "is_reloading": False,
                    "start_time": 0,
                    "duration": 0,    # 动态传入的时间
                    "icon": None      # 动态传入的图标
                }
                player_world_x, player_world_y = WORLD_WIDTH // 2, WORLD_HEIGHT // 2
                if os.path.exists(bgm_path):
                    pygame.mixer.music.stop()
                    pygame.mixer.music.load(bgm_path)
                    pygame.mixer.music.set_volume(0.6) # 设置音量
                    pygame.mixer.music.play(-1) # 循环播放音乐
                pygame.time.delay(200)
            
            if btn(btn_help_normal, btn_help_hover, btn_x, btn_y+320):
                help_paper.set_alpha(alpha)
                alpha = 0  # 从完全透明开始
                show1 = True
            
            if show1:
                rect = img.get_rect()
                rect.center = (1600, 900)
                help_paper.set_alpha(255)
                canvas.blit(help_paper, center(help_paper,1600,900))
                if btn(btn_close_normal, btn_close_hover, 2987, 70):
                    show1 = False


        elif scene == 'GAME':
            if player_hp > 0 and wall_hp > 0:
                # 移动逻辑
                keys = pygame.key.get_pressed()
                if keys[pygame.K_a]: player_world_x -= player_speed
                if keys[pygame.K_d]: player_world_x += player_speed
                if keys[pygame.K_w]: player_world_y -= player_speed
                if keys[pygame.K_s]: player_world_y += player_speed


                player_world_x = max(0, min(player_world_x, WORLD_WIDTH - PLAYER_SIZE))
                player_world_y = max(0, min(player_world_y, WORLD_HEIGHT - PLAYER_SIZE))

                cam_x = (LOGIC_W//2 - (player_world_x + PLAYER_SIZE//2))
                cam_y = (LOGIC_H//2 - (player_world_y + PLAYER_SIZE//2))

                offset_x = cam_x % TILE_W
                offset_y = cam_y % TILE_H
                
                for x in range(-TILE_W, LOGIC_W + TILE_W, TILE_W):
                    for y in range(-TILE_H, LOGIC_H + TILE_H, TILE_H):
                        canvas.blit(tile_img2, (x + offset_x, y + offset_y))
                move_item(fence,0,-100) #上围栏
                # 敌人生成
                if frame_counter % SPAWN_RATE == 0:
                    spawn_y = random.randint(0, WORLD_HEIGHT - ENEMY_SIZE)
                    enemies.append({"x": WORLD_WIDTH, "y": spawn_y, "born": frame_counter, "alpha": 255})

                # --- 碰撞检测准备 ---
                # 玩家在逻辑世界中的矩形 (x, y, w, h)
                player_rect = pygame.Rect(player_world_x, player_world_y, PLAYER_SIZE, PLAYER_SIZE)

                # --- 敌人更新与绘制 ---
                for e in enemies[:]:
                    e["x"] -= ENEMY_SPEED 
                    draw_x, draw_y = e["x"] + cam_x, e["y"] + cam_y
                    
                    # 创建敌人的矩形进行碰撞判定
                    enemy_rect = pygame.Rect(e["x"], e["y"], ENEMY_SIZE, ENEMY_SIZE)
                    
                    # 【碰撞逻辑】
                    if player_rect.colliderect(enemy_rect):
                        if current_time - last_hit_time > hit_cooldown:
                            player_hp -= 5
                            last_hit_time = current_time #更新被撞时间戳

                    if -ENEMY_SIZE < draw_x < LOGIC_W and -ENEMY_SIZE < draw_y < LOGIC_H:
                        alive_ticks = frame_counter - e["born"]
                        e_idx = (alive_ticks // ENEMY_ANIM_SPEED) % len(enemy_frames)
                        enemy_frames[e_idx].set_alpha(e["alpha"])
                        canvas.blit(enemy_frames[e_idx], (draw_x, draw_y))
                    
                    if e["x"] <= -ENEMY_SIZE-50:
                        e["alpha"] -= 5
                        if e["alpha"] <= 0:
                            wall_hp -= 5
                            enemies.remove(e)

                if delay_hp > player_hp:
                    delay_hp -= 0.2
                elif delay_hp < player_hp:
                    delay_hp = player_hp
                if wall_delay_hp > wall_hp:
                    wall_delay_hp -= 0.2
                elif wall_delay_hp < wall_hp:
                    wall_delay_hp = wall_hp

                if player_hp > 100:
                    player_hp = 100
                if add_hp > 0:
                    player_hp += 0.2
                    add_hp -= 0.2

                # 玩家绘制
                if keys[pygame.K_a] or keys[pygame.K_d] or keys[pygame.K_w] or keys[pygame.K_s]:
                    p_idx = (frame_counter // ANIM_SPEED) % len(player_frames)
                    canvas.blit(player_frames[p_idx], (LOGIC_W//2 - PLAYER_SIZE//2, LOGIC_H//2 - PLAYER_SIZE//2))
                else:
                    canvas.blit(player_frames[p_idx], (LOGIC_W//2 - PLAYER_SIZE//2, LOGIC_H//2 - PLAYER_SIZE//2))
                if True: #武器1
                    if p_idx==0:
                        static_item(weapon1[0],int(LOGIC_W//2 - PLAYER_SIZE//2),int(LOGIC_H//2 - PLAYER_SIZE//2+55))
                    elif p_idx==1:
                        static_item(weapon1[0],int(LOGIC_W//2 - PLAYER_SIZE//2),int(LOGIC_H//2 - PLAYER_SIZE//2+45))
                move_item(fence,0,2145) #下围栏
                move_item(tree1,-830,-630) #左树
                move_item(tree2,5400,-1900)#右树
                move_item(wall,-1500,-725) #墙
                move_item(wall_life,-1480,1050) #墙血量
                #static_item(open_bar[0], 30, 30) #开箱进度条
                static_item(rec, 70, 1550) #换弹药
                draw_health_bar(canvas, cam_x-1350, cam_y+1000, wall_hp, 100,wall_delay_hp)#墙血条
                draw_health_bar(canvas, LOGIC_W//2-118, LOGIC_H//2-140, player_hp, 100,delay_hp) #血条
                if developer_mode:
                    fps = int(clock.get_fps())
                    fps_text = ui_font.render(f"FPS: {fps}", True, (255, 255, 0))
                    current_time = pygame.time.get_ticks()
                    current_time_text = ui_font.render(f"Time: {current_time//1000}s", True, (255, 255, 0))
                    canvas.blit(fps_text, (120, 10))
                    canvas.blit(current_time_text, (120, 50))
                    health_text = ui_font.render(f"HP: {player_hp}", True, (255, 255, 0))
                    canvas.blit(health_text, (120, 90))
                    if draw_btn("buttun", 120, 160, 150, 60 ,(60, 60, 60)):
                        player_hp -= 3
                    
                if draw_btn("结束", LOGIC_W - 180, 30, 150, 60, (60, 60, 60)):
                    scene = 'RESULT'
                    pygame.mixer.music.stop()
                    pygame.time.delay(200)
            elif player_hp <= 0:
                static_item(grave, LOGIC_W//2 - PLAYER_SIZE//2,(LOGIC_H//2 - PLAYER_SIZE//2)-200) #玩家死亡后绘制墓碑
                scene = 'RESULT'
                pygame.mixer.music.stop()
                pygame.time.delay(200)
            elif wall_hp <= 0:
                scene = 'RESULT'
                pygame.mixer.music.stop()
                pygame.time.delay(200)

        elif scene == 'RESULT':
            for x in range(-TILE_W, LOGIC_W + TILE_W, TILE_W):
                for y in range(-TILE_H, LOGIC_H + TILE_H, TILE_H):
                    canvas.blit(tile_img3, (x + offset_x, y + offset_y))
            res_msg = title_font.render("Game Over", True, (255, 0, 0))
            canvas.blit(res_msg, res_msg.get_rect(center=(LOGIC_W//2, LOGIC_H//3)))
            if draw_btn("返回菜单", LOGIC_W//2-150, LOGIC_H//2, 300, 80, (50, 150, 255)):
                scene = 'MENU'
                pygame.time.delay(200)

        # 缩放投影
        win_w, win_h = screen.get_size()
        nonlocal_current_scale = min(win_w / LOGIC_W, win_h / LOGIC_H)
        new_size = (int(LOGIC_W * nonlocal_current_scale), int(LOGIC_H * nonlocal_current_scale))
        scaled_canvas = pygame.transform.scale(canvas, new_size)
        nonlocal_current_offset = ((win_w - new_size[0]) // 2, (win_h - new_size[1]) // 2)
        
        screen.fill((20, 20, 20)) 
        screen.blit(scaled_canvas, nonlocal_current_offset)

        pygame.display.flip()
        clock.tick(60)

# === 6. 程序入口 ===
if __name__ == "__main__":
    main()