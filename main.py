import pygame
import sys
import os
import random
import traceback

# === 1. 配置与初始化函数 ===
def main():
    pygame.init()
    # 初始化混音器（必须在音乐播放前）
    pygame.mixer.init()
    LOGIC_W, LOGIC_H = 3200, 1800
    win_w, win_h = 1600, 900

    screen = pygame.display.set_mode((win_w, win_h), pygame.RESIZABLE)
    canvas = pygame.Surface((LOGIC_W, LOGIC_H))
    title="变异狂潮-十周年纪念版"
    pygame.display.set_caption(title)
    icon_img = pygame.image.load("codemao/r-logo.png").convert_alpha() 
    pygame.display.set_icon(icon_img)


    def get_font(size):
        return pygame.font.SysFont(["wqy-microhei", "notosanscjksc", "simhei", "sans-serif"], size)

    title_font = get_font(100)
    ui_font = get_font(40)
    clock = pygame.time.Clock()

    # --- 2. 资源加载与处理 ---
    # 背景音乐加载
    bgm_path = "codemao/music/bgm.mp3"
    bgm_path2 = "codemao/music/bgm2.mp3"
    #title_img图片加载
    title_img = pygame.image.load("codemao/UI/Byzomb.png").convert_alpha()
    title_img = pygame.transform.scale(title_img, (1716, 500))
    # 开始按钮图片加载
    # 按钮尺寸（根据你的图片实际大小调整）
    BTN_W, BTN_H = 912.5, 322.5

    # 加载常态图
    btn_normal = pygame.image.load("codemao/UI/buttun1.png").convert_alpha()
    btn_normal = pygame.transform.scale(btn_normal, (BTN_W, BTN_H))

    # 加载悬停图（比如带光效的图）
    btn_hover = pygame.image.load("codemao/UI/buttun2.png").convert_alpha()
    btn_hover = pygame.transform.scale(btn_hover, (BTN_W, BTN_H))

    # 角色动画加载
    PLAYER_SIZE = 180
    ANIM_SPEED = 35 
    player_frames = []
    p_files = ["codemao/player1.png", "codemao/player2.png"] 

    for f in p_files:
        if os.path.exists(f):
            img = pygame.image.load(f).convert_alpha()
            player_frames.append(pygame.transform.scale(img, (PLAYER_SIZE, PLAYER_SIZE)))
        else:
            s = pygame.Surface((PLAYER_SIZE, PLAYER_SIZE))
            s.fill((255, 0, 0) if "1" in f else (255, 100, 0))
            player_frames.append(s)

    # 敌人动画加载
    ENEMY_SIZE = 150
    ENEMY_ANIM_SPEED = 20 
    enemy_frames = []
    e_files = ["codemao/enemy1.png", "codemao/enemy2.png"]

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

    tile_img = pygame.Surface((TILE_W, TILE_H))
    tile_img.fill((34, 139, 34)) 

    if os.path.exists("codemao/background.png"):
        try:
            raw_tile = pygame.image.load("codemao/background.png").convert()
            tile_img = pygame.transform.scale(raw_tile, (TILE_W, TILE_H))
        except: pass

    tile_img2 = pygame.Surface((TILE_W, TILE_H))
    tile_img2.fill((34, 139, 34)) 

    if os.path.exists("codemao/background2.png"):
        try:
            raw_tile = pygame.image.load("codemao/background2.png").convert()
            tile_img2 = pygame.transform.scale(raw_tile, (TILE_W, TILE_H))
        except: pass

    # --- 3. 游戏状态变量 ---
    scene = 'MENU'
    WORLD_WIDTH, WORLD_HEIGHT = 7500, 4000
    player_world_x, player_world_y = WORLD_WIDTH // 2, WORLD_HEIGHT // 2
    player_speed = 12
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
    def start_btn(img_normal, img_hover, x, y):
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
            #msg = title_font.render(title, True, (255, 255, 255))
            #canvas.blit(msg, msg.get_rect(center=(LOGIC_W//2, LOGIC_H//3)))
            title_x = LOGIC_W // 2 - title_img.get_width() // 2
            title_y = 200  # 距离顶部 200 像素
            canvas.blit(title_img, (title_x, title_y))
            btn_x = LOGIC_W // 2 - BTN_W // 2
            btn_y = LOGIC_H // 2
            if start_btn(btn_normal, btn_hover, btn_x, btn_y):
                scene = 'GAME'
                enemies = [] # 重置敌人
                player_world_x, player_world_y = WORLD_WIDTH // 2, WORLD_HEIGHT // 2
                if os.path.exists(bgm_path):
                    pygame.mixer.music.stop()
                    pygame.mixer.music.load(bgm_path)
                    pygame.mixer.music.set_volume(0.6) # 设置音量
                    pygame.mixer.music.play(-1) # 循环播放音乐
                pygame.time.delay(200)


        elif scene == 'GAME':
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
                    canvas.blit(tile_img, (x + offset_x, y + offset_y))

            # 敌人生成
            if frame_counter % SPAWN_RATE == 0:
                spawn_y = random.randint(0, WORLD_HEIGHT - ENEMY_SIZE)
                enemies.append({"x": WORLD_WIDTH, "y": spawn_y, "born": frame_counter})

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
                    scene = 'RESULT'
                    pygame.mixer.music.stop() # 撞到了强制停音乐
                    pygame.time.delay(200)

                if -ENEMY_SIZE < draw_x < LOGIC_W and -ENEMY_SIZE < draw_y < LOGIC_H:
                    alive_ticks = frame_counter - e["born"]
                    e_idx = (alive_ticks // ENEMY_ANIM_SPEED) % len(enemy_frames)
                    canvas.blit(enemy_frames[e_idx], (draw_x, draw_y))
                
                if e["x"] <= -ENEMY_SIZE:
                    enemies.remove(e)

            # 玩家绘制
            p_idx = (frame_counter // ANIM_SPEED) % len(player_frames)
            canvas.blit(player_frames[p_idx], (LOGIC_W//2 - PLAYER_SIZE//2, LOGIC_H//2 - PLAYER_SIZE//2))

            if draw_btn("结束", LOGIC_W - 180, 30, 150, 60, (60, 60, 60)):
                scene = 'RESULT'
                pygame.mixer.music.stop()
                pygame.time.delay(200)

        elif scene == 'RESULT':
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