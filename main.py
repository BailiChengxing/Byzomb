import pygame
import sys
import os
import random
import math
import copy

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
    pygame.mixer.set_num_channels(32) # 默认是 8，设置为32声道
    pygame.display.set_caption(title)
    icon_img = pygame.image.load("codemao/r-logo2.png").convert_alpha() 
    pygame.display.set_icon(icon_img)
    show1 = False #是否显示帮助界面
    show2 = False #游戏是否暂停
    score_x ,score_y = 2800,10 #分数显示位置
    current_mag_x ,current_mag_y = 70,10 #当前弹匣显示位置
    reserve_ammo_x ,reserve_ammo_y = 290,40 #当前备用弹药显示位置
    developer_x ,developer_y = 60,150 #开发者模式信息显示位置
    drop_status = False
    developer_mode = False  # 开发者模式开关
    mute = False  # 静音状态
    drop_x,drop_y = random.randint(400,4800),random.randint(-200,1500)
    drop_cooldown = random.randint(30000, 40000) #刷新后下次刷新间隔30-40秒
    current_time = pygame.time.get_ticks()
    hotbar_status = True #背包状态
    is_fullscreen = False #全屏状态

    last_hit_time = 0 # 重置被撞时间戳
    score = 0 #分数
    score_x ,score_y = 2800,10 #分数显示位置
    current_mag_x ,current_mag_y = 70,10 #当前弹匣显示位置
    reserve_ammo_x ,reserve_ammo_y = 290,40 #当前备用弹药显示位置
    developer_x ,developer_y = 60,150 #开发者模式信息显示位置

    rec_status = False #是否在更换弹药中
    pygame.mouse.set_visible(False)



    if os.name == 'nt': # 只在 Windows 生效
        import ctypes
        # 获取当前窗口句柄并禁用输入法
        hwnd = pygame.display.get_wm_info()['window']
        ctypes.windll.imm32.ImmAssociateContext(hwnd, None)


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

    def open_bar(surface, x, y, current):
        bar_width = 230
        bar_height = 22
        ratio = max(0, min(current/100, 1))
        pygame.draw.rect(surface, (30, 30, 30), (x, y, bar_width, bar_height))
        color = (89, 212, 205)
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
        try:
            for i in file:
                if os.path.exists(i):
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
            
    def load_main_weapon(**files):
        """
        批量加载武器图片
        :param files: 格式为 name="path" 的参数
        :return: 包含 {名称: pygame图片对象} 的字典
        """
        weapon_assets = {}
        for name, path in files.items():
            try:
                img = pygame.image.load(path).convert_alpha()
                img = pygame.transform.scale(img, (320, 145))
                weapon_assets[name] = img
            except pygame.error as e:
                print(f"error to load img{path}: {e}")
        return weapon_assets
    
    def load_vice_weapons(weapon_dict):
        vice_assets = {}
        for name, img in weapon_dict.items():
            rotated_img = pygame.transform.rotate(img, -90)
            final_img = pygame.transform.flip(rotated_img, True, False)
            vice_assets[name] = final_img
        return vice_assets
    
    
    '''def draw_rotating_gun(surface, image, pivot, angle):
        rotated_image = pygame.transform.rotate(image, angle)
        new_rect = rotated_image.get_rect(center=pivot)
        surface.blit(rotated_image, new_rect)'''
    
    def draw_rotating_gun(surf, image, pos, angle):
        """
        pos: 旋转中心的坐标 (红点位置)
        angle: 旋转角度
        """
        # --- 第一步：计算偏移量 ---
        # 你的枪支是竖着的，所以中心点到顶端的偏移是 y 方向的
        # 我们向上偏移 (负 y)，这样红点就会出现在枪的“上端”
        # 假设你想让红点在枪顶端往下 10 像素的位置，就写 -image.get_height()/2 + 10
        offset_y = -image.get_height() / 2 +60  
        center_offset = pygame.math.Vector2(0, offset_y)
        
        # --- 第二步：旋转偏移向量 ---
        # 注意：向量旋转必须和图片旋转角度一致
        # .rotate() 在 pygame 中是顺时针旋转，所以 angle 可能需要加负号，取决于你 atan2 的算法
        rotated_offset = center_offset.rotate(-angle) 
        
        # --- 第三步：旋转图像 ---
        rotated_image = pygame.transform.rotate(image, angle)
        rect = rotated_image.get_rect(center=pos - rotated_offset)
        surf.blit(rotated_image, rect)
        # 开发者模式调试
        if developer_mode:
            pygame.draw.circle(surf, (255, 0, 0), pos, 5)  # 旋转中心（红点）
            # 绘制一条线连接红点和图片现在的中心点
            pygame.draw.line(surf, (0, 255, 0), pos, rect.center, 2)


    def get_font(size):
        return pygame.font.Font("codemao/SourceHanSansCN.ttf", size)

    def move_item(img,x,y):#定义动类型物品绘制
        item_draw_x = x + cam_x
        item_draw_y = y + cam_y
        canvas.blit(img, (item_draw_x, item_draw_y))
    def static_item(img,x,y):#定义动类型物品绘制
        canvas.blit(img, (x,y))
    def center_static_item(img,x,y):#定义动类型物品绘制
        img_rect = img.get_rect(center=(x, y))
        canvas.blit(img, img_rect)

    title_font = get_font(100)
    ui_font = get_font(40)
    score_font = get_font(200)
    clock = pygame.time.Clock()

    # --- 2. 资源加载与处理 ---

    hit_cooldown = 300 # 被撞后无敌时间（毫秒）

    # 背景音乐加载
    bgm_path = "codemao/music/bgm.mp3"
    bgm_path2 = "codemao/music/bgm2.mp3"
    bgm_path4 = "codemao/music/bgm4.mp3"
    bgm_path5 = "codemao/music/bgm5.mp3"
    game_over_sound = pygame.mixer.Sound("codemao/music/game_over.wav")
    game_over_sound.set_volume(0.8)
    #——————枪支音效——————
    reload_sound = pygame.mixer.Sound("codemao/music/reload.wav")
    reload_sound.set_volume(0.3)

    rifle_sound = pygame.mixer.Sound("codemao/music/rifle.wav")#步枪音效
    rifle_sound.set_volume(0.5)
    lmg_sound = pygame.mixer.Sound("codemao/music/lmg.wav")#机枪音效
    lmg_sound.set_volume(0.4)
    sniper_sound = pygame.mixer.Sound("codemao/music/sniper.wav")#狙击枪音效
    sniper_sound.set_volume(0.1)
    submachine_sound = pygame.mixer.Sound("codemao/music/submachine.wav")#冲锋枪音效
    submachine_sound.set_volume(0.3)
    shotgun_sound = pygame.mixer.Sound("codemao/music/shotgun.wav")#霰弹枪音效
    shotgun_sound.set_volume(0.5)
    laser_sound = pygame.mixer.Sound("codemao/music/laser.wav")#激光枪音效
    laser_sound.set_volume(0.3)
    howitzer_sound = pygame.mixer.Sound("codemao/music/howitzer.wav")#榴弹炮音效
    howitzer_sound.set_volume(0.3)
    rocket_boom_sound = pygame.mixer.Sound("codemao/music/rocket_boom.wav")#火箭炮音效
    rocket_boom_sound.set_volume(0.3)


    bgm_tuple=(bgm_path,bgm_path4,bgm_path5)
    play_bgm = bgm_tuple[random.randint(0,2)]
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

    #加载返回按钮
    btn_back_normal = load(file="codemao/UI/back1.png",x=BTN_W*0.5)
    btn_back_hover = load(file="codemao/UI/back2.png",x=BTN_W*0.5)

    #加载暂停菜单
    menu_normal = load(file="codemao/UI/menu1.png",x=180)
    menu_hover = load(file="codemao/UI/menu2.png",x=180)
    continue_normal = load(file="codemao/UI/continue1.png",x=180)
    continue_hover = load(file="codemao/UI/continue2.png",x=180)
    exit_normal = load(file="codemao/UI/exit1.png",x=180)
    exit_hover = load(file="codemao/UI/exit2.png",x=180)
    mute_f_normal = load(file="codemao/UI/mute1.png",x=180)
    mute_f_hover = load(file="codemao/UI/mute2.png",x=180)
    mute_t_normal = load(file="codemao/UI/mute3.png",x=180)
    mute_t_hover = load(file="codemao/UI/mute4.png",x=180)
    pause_page = load(file="codemao/UI/pause_page.png",x=1700)

    #加载围栏
    fence=load(file="codemao/Fence.png",x=move_x) #围栏
    #加载树林
    tree1=load(file="codemao/tree1.png",y=int(move_y+800)) #左树
    tree2=load(file="codemao/tree2.png",y=int(move_y+2700)) #右树

    wall_img=load(file="codemao/wall.png",y=int(move_y+1600)) #墙
    wall_life=load(file="codemao/wall_life.png",x=450) #墙血量


    cursor = load(file="codemao/cursor.png",x=60) #自定义鼠标指针

    grave=load(file="codemao/grave.png",y=230) #墓碑

    #加载空投
    drop1=load(file="codemao/drop1.png",y=660)
    drop2=load(file="codemao/drop2.png",y=660)

    #——————加载数字——————
    num_img = load_ls(["codemao/num/0.png","codemao/num/1.png","codemao/num/2.png","codemao/num/3.png","codemao/num/4.png","codemao/num/5.png","codemao/num/6.png","codemao/num/7.png","codemao/num/8.png","codemao/num/9.png"],x=70) #数字图片列表
    num_img2 = load_ls(["codemao/num/0.png","codemao/num/1.png","codemao/num/2.png","codemao/num/3.png","codemao/num/4.png","codemao/num/5.png","codemao/num/6.png","codemao/num/7.png","codemao/num/8.png","codemao/num/9.png"],x=50) #数字图片列表
    num_img0 = load_ls(["codemao/num0/0.png","codemao/num0/1.png","codemao/num0/2.png","codemao/num0/3.png","codemao/num0/4.png","codemao/num0/5.png","codemao/num0/6.png","codemao/num0/7.png","codemao/num0/8.png","codemao/num0/9.png"],x=50) #数字图片列表

    #——————道具加载——————
    empty_icon = load(file="codemao/items/icons/empty-1.png",x=160) #空道具图标
    use_item_sign = load(file="codemao/sign.png", x =75)#道具使用指示

    ITEMS_CONFIG = {"bandage":{
        "name": "bandage",
        "image": load(file="codemao/items/bandage.png",x=160),
        "icon": load(file="codemao/items/icons/bandage-1.png",x=160),
    },
    "kit":{
        "name": "kit",
        "image": load(file="codemao/items/kit.png",x=160),
        "icon": load(file="codemao/items/icons/kit-1.png",x=160),
    }
    }
    
    class Items:
        def __init__(self, name, config):
            self.name = name
            self._image = config["image"]
            self._icon = config["icon"]

        def use(self, player):
            if self.name == "bandage":
                player.hp += 5
            if self.name == "kit":
                player.hp += 15

        @property
        def image(self):
            return self._image
        @property
        def icon(self):
            return self._icon


    #——————武器加载——————
    main_weapon_img=load_main_weapon(empty="codemao/weapon/empty.png",
                                 mondragon="codemao/weapon/mondragon.png",
                                 AK47="codemao/weapon/AK47.png",
                                 M249="codemao/weapon/M249.png",
                                    AWN="codemao/weapon/AWN.png",
                                    QBU="codemao/weapon/QBU.png",
                                    _950M="codemao/weapon/950M.png"
                                    ) #主武器字典
    vice_weapon_img=load_vice_weapons(main_weapon_img) #副武器字典
    weapon_list=list(main_weapon_img) #主武器列表
    bullet_img=load(r"codemao\bullet.png",x=20)

    WEAPON_CONFIG = {
        "empty": {
            "name": "空手",
            "damage": 0,
            "speed":0,
            "gun_type": "empty",
            "weight": 0,
            "mag_capacity": 0,
            "reserve_ammo": 0,
            "reload_time": 0,
            "cool_down": 0
        }, #空武器配置
        "mondragon": {
            "name": "mondragon",
            "damage": 10,
            "speed":200,
            "gun_type": "rifle",
            "weight": 6,
            "mag_capacity": 12,
            "reserve_ammo": 48,
            "reload_time": 1500,
            "cool_down" : 500
        },
        "AK47": {
            "name": "AK47",
            "damage": 8,
            "speed":200,
            "gun_type": "rifle",
            "weight": 7,
            "mag_capacity": 30,
            "reserve_ammo": 120,
            "reload_time": 2000,
            "cool_down" : 100
        },
        "M249": {
            "name": "M249",
            "damage": 6,
            "speed":200,
            "gun_type": "lmg",
            "weight": 15,
            "mag_capacity": 100,
            "reserve_ammo": 400,
            "reload_time": 3200,
            "cool_down" : 65
        },
        "AWN": {
            "name": "AWN",
            "damage": 15,
            "speed":200,
            "gun_type": "sniper",
            "weight": 13,
            "mag_capacity": 5,
            "reserve_ammo": 25,
            "reload_time": 2500,
            "cool_down" : 900
        },
        "QBU": {
            "name": "QBU",
            "damage": 12,
            "speed":200,
            "gun_type": "markman_rifle",
            "weight": 8,
            "mag_capacity": 10,
            "reserve_ammo": 50,
            "reload_time": 2200,
            "cool_down" : 300
        },
        "_950M": {
            "name": "950M",
            "damage": 20,
            "speed":200,
            "gun_type": "shotgun",
            "weight": 9,
            "mag_capacity": 5,
            "reserve_ammo": 30,
            "reload_time": 2200,
            "cool_down" : 300
        }
    }
    test_weapon = "AWN" #测试用武器ID

    class Weapon:
        def __init__(self, name, config):
            self.name = name
            self.damage = config["damage"]
            self.gun_type = config["gun_type"]
            self._weight = config["weight"]
            self.mag_capacity = config["mag_capacity"]
            self.current_mag = config["mag_capacity"]
            self.reserve_ammo = config["reserve_ammo"]
            self.reload_time = config["reload_time"]
            self.cool_down = config["cool_down"]

            #——————实现相关功能——————
            self._reloading = False
            self.reload_start_time = 0
            self.last_fire_time = 0

            #定义枪支射击声音
            if self.gun_type == "rifle":
                self.weapon_sound = rifle_sound
            elif self.gun_type == "markman_rifle":
                self.weapon_sound = rifle_sound
            elif self.gun_type == "lmg":
                self.weapon_sound = lmg_sound
            elif self.gun_type == "sniper":
                self.weapon_sound = sniper_sound
            elif self.gun_type == "submachine":
                self.weapon_sound = submachine_sound
            elif self.gun_type == "laser":
                self.weapon_sound = laser_sound
            elif self.gun_type == "shotgun":
                self.weapon_sound = shotgun_sound
            elif self.gun_type == "howitzer":
                self.weapon_sound = howitzer_sound
            else:
                self.weapon_sound = rifle_sound

        def fire(self):
            if self.gun_type == "shotgun":#霰弹枪可在换弹过程中继续开枪，开枪中断换弹
                if self.current_mag > 0:
                    now = pygame.time.get_ticks()
                    if now-self.last_fire_time >= self.cool_down:
                        if self.reloading:
                            self.reloading = False # 开枪中断换弹
                        self.current_mag -= 1
                        self.weapon_sound.play()
                        self.last_fire_time = pygame.time.get_ticks()
                else:
                    self.reload()
                pass
            else:#其他枪换弹过程中无法开枪，必须等换弹结束才能开枪
                if self.current_mag > 0 and self.reloading == False:
                    now = pygame.time.get_ticks()
                    if now-self.last_fire_time >= self.cool_down:
                        self.current_mag -= 1
                        self.weapon_sound.play()
                        self.last_fire_time = pygame.time.get_ticks()
                else:
                    self.reload()

        def reload(self):
            if self.name != "empty" and not self.reloading:
                if self.reserve_ammo > 0 and self.current_mag < self.mag_capacity:
                    self.reload_start_time = pygame.time.get_ticks()
                    self._reloading = True
                    pygame.mixer.Sound(reload_sound).play()

        def update(self):
            """这个方法需要在主循环里每一帧都调用"""
            bar_width,bar_height = 15,120
            x,y=30,5  
            if self.reloading:
                now = pygame.time.get_ticks()

                # 检查时间是否到了
                if self.gun_type == "shotgun":#霰弹枪每发子弹单独换弹，换弹过程中可以继续开枪，开枪中断换弹
                    ratio = max(0, min(self.current_mag / self.mag_capacity, 1))
                    current_bar_h = bar_height * ratio
                    pygame.draw.rect(canvas, (30, 30, 30), (x, y, bar_width, bar_height))
                    pygame.draw.rect(canvas, (222, 222, 222),(x, y + bar_height - current_bar_h, bar_width, current_bar_h))
                    pygame.draw.rect(canvas, (100, 100, 100), (x, y, bar_width, bar_height), 2)
                    each_reload_time = self.reload_time / self.mag_capacity
                    if now - self.reload_start_time >= each_reload_time:
                        if self.current_mag < self.mag_capacity and self.reserve_ammo > 0:
                            self.current_mag += 1
                            self.reserve_ammo -= 1
                            self.reload_start_time = now # 重置换弹计时，继续下一发换弹
                            if self.current_mag == self.mag_capacity or self.reserve_ammo == 0:
                                self.reloading = False # 换弹结束
                else:#其他枪换弹过程中无法开枪，必须等换弹结束才能开枪
                    ratio = max(0, min((now-self.reload_start_time) / self.reload_time, 1))
                    current_bar_h = bar_height * ratio
                    pygame.draw.rect(canvas, (30, 30, 30), (x, y, bar_width, bar_height))
                    pygame.draw.rect(canvas, (222, 222, 222),(x, y + bar_height - current_bar_h, bar_width, current_bar_h))
                    pygame.draw.rect(canvas, (100, 100, 100), (x, y, bar_width, bar_height), 2)
                    if now - self.reload_start_time >= self.reload_time:
                        needed = self.mag_capacity - self.current_mag
                        reload_amount = min(self.reserve_ammo, needed)
                        self.current_mag += reload_amount
                        self.reserve_ammo -= reload_amount
                        self.reloading = False # 换弹结束
            else:
                if self.name != "empty":
                    ratio = max(0, min(self.current_mag / self.mag_capacity, 1))
                    current_bar_h = bar_height * ratio
                    pygame.draw.rect(canvas, (30, 30, 30), (x, y, bar_width, bar_height))
                    pygame.draw.rect(canvas, (222, 222, 222),(x, y + bar_height - current_bar_h, bar_width, current_bar_h))
                    pygame.draw.rect(canvas, (100, 100, 100), (x, y, bar_width, bar_height), 2)

            
        
        @property
        def reloading(self):
            return self._reloading
        @property
        def weight(self):
            return self._weight
        
        @reloading.setter
        def reloading(self, value):
            self._reloading = value

    class Bullet(pygame.sprite.Sprite):
        def __init__(self,speed,damage,x,y):
            super().__init__()
            self.image=bullet_img
            self.rect = self.image.get_rect(center=(x, y))
            self.speed=speed
            self.damage=damage

        def update(self):
            self.rect.x += self.speed
            # 超出屏幕自动销毁
            if self.rect.x > 1280: 
                self.kill() # 从所有精灵组中移除


    class Player:
        def __init__(self, config):
            #——————枪支属性——————
            self.config = config
            mondragon = Weapon("mondragon", copy.deepcopy(config["mondragon"]))
            empty = Weapon("empty", copy.deepcopy(config["empty"]))
            self.inventory = [mondragon, empty]
            self.hotbar = [None, None, None, None, None,None] # 预留的快捷栏
            self.active_index = 0
            self.sniper_mode = False

            #——————血量属性——————
            self.max_hp = 100 #最大血量
            self._hp = 100          # 1. 实际血量
            self.goal_hp = 100      # 2. 预期值（用于回血深绿条）
            self.display_hp = 100   # 3. 显示值（彩色主体条）
            self.residual_hp = 100  # 4. 残留值（用于扣血白条）
            self.bool_add=False
            self.bool_sub=False

            #——————其他属性——————
            self._last_hit_time= 0


        #——————受伤冷却时间——————
        @property
        def last_hit_time(self):
            return self._last_hit_time
        
        @last_hit_time.setter
        def last_hit_time(self, value):
            self._last_hit_time = value

        #——————枪支方法——————
        def switch_weapon(self):
            if not self.current_weapon.reloading:
                self.active_index = 1 - self.active_index
                if player.current_weapon.gun_type == "sniper" or player.current_weapon.gun_type == "markman_rifle":
                    self.sniper_mode = True
                else:
                    self.sniper_mode = False

        def pick_up(self, weapon_id):
            new_data = copy.deepcopy(self.config[weapon_id])
            new_weapon = Weapon(weapon_id, new_data)
            if self.inventory[1-self.active_index].name == "empty":
                self.inventory[1-self.active_index] = new_weapon
            else:
                self.inventory[self.active_index] = new_weapon
            if player.current_weapon.gun_type == "sniper" or player.current_weapon.gun_type == "markman_rifle":
                self.sniper_mode = True
            else:
                self.sniper_mode = False

        def get_item(self, item_id):
            new_item = Items(item_id, ITEMS_CONFIG[item_id])
            for i in range(len(self.hotbar)):
                if self.hotbar[i] is None:
                    self.hotbar[i] = new_item
                    break
            else:
                print("hotbar is full!!")

        def use_item(self, index ,player):
            if 0 <= index < len(self.hotbar) and self.hotbar[index] is not None:
                item = self.hotbar[index]
                item.use(player)
                self.hotbar[index] = None

        @property
        def current_weapon(self):
            return self.inventory[self.active_index]
        @property
        def vice_weapon(self):
            return self.inventory[1-self.active_index]
        

        #——————血量方法——————
        @property
        def hp(self):
            return self._hp
        
        @hp.setter
        def hp(self, value):
            """当执行 player.hp = ... 或 player.hp += ... 时自动触发"""
            old_hp = self._hp
            self._hp = max(0, min(value, self.max_hp))# 1. 自动限制范围
            if self._hp > old_hp:
                # 回血瞬间：预期值立刻拉满，引导显示值追赶
                self.goal_hp = self._hp
                self.bool_sub=False
                self.bool_add=True
            elif self._hp < old_hp:
                # 扣血瞬间：显示值立刻缩回，留下残留值在后面追赶
                self.display_hp = self._hp
                self.bool_sub=True
                self.bool_add=False
            else:
                self.bool_sub=False
                self.bool_add=False
            if self._hp == 0:#角色死亡后的处理
                pass

        def update_vitals(self):
            """三阶动画同步"""
            # 1. 回血逻辑：让显示值追赶预期值
            if self.bool_add and self.display_hp < self.goal_hp:
                self.display_hp += (self.goal_hp - self.display_hp) * 0.05
            # 2. 扣血逻辑：让残留值追赶显示值
            if self.bool_sub and self.residual_hp > self.display_hp:
                self.residual_hp -= (self.residual_hp - self.display_hp) * 0.1
            # 3. 静态对齐
            if self.bool_sub==False:
                self.residual_hp = self.display_hp

        def draw_health_bar(self, surface, x, y):
            bar_width = 230
            bar_height = 28
            # 1. 背景层 (深灰)
            pygame.draw.rect(surface, (30, 30, 30), (x, y, bar_width, bar_height))
            # 2. 残留层 (白色) - 只有扣血时 residual_hp > display_hp 才有意义
            if self.bool_sub and self.residual_hp > self.display_hp:
                white_w = int(bar_width * (self.residual_hp / self.max_hp))
                pygame.draw.rect(surface, (255, 255, 255), (x, y, white_w, bar_height))
            # 3. 预期层 (深绿) - 只有回血时 goal_hp > display_hp 才有意义
            if self.bool_add and self.goal_hp > self.display_hp:
                goal_w = int(bar_width * (self.goal_hp / self.max_hp))
                pygame.draw.rect(surface, (24,100,24), (x, y, goal_w, bar_height))
            # 4. 主色条层 (当前显示)
            ratio = self.display_hp / self.max_hp
            color = (42, 174, 42) if ratio > 0.5 else (218, 165, 32) if ratio > 0.2 else (178, 34, 34)
            pygame.draw.rect(surface, color, (x, y, int(bar_width * ratio), bar_height))
            # 5. 边框与装饰
            pygame.draw.rect(surface, (100, 100, 100), (x, y, bar_width, bar_height), 2)
            # 高光效果叠加在主色条上
            if int(bar_width * ratio) > 0:
                h_surf = pygame.Surface((int(bar_width * ratio), bar_height // 2), pygame.SRCALPHA)
                h_surf.fill((255, 255, 255, 40))
                surface.blit(h_surf, (x, y))
    

    class Wall:
        def __init__(self):
                self.max_hp = 100
                self._hp = 100
                self._delay_hp = 100

        @property
        def hp(self):
            return self._hp
        
        @hp.setter
        def hp(self, value):
            self._hp = max(0, min(value, self.max_hp))
            if self._hp == 0:
                pass

        @property
        def delay_hp(self):
            return self._delay_hp
        
        def update_vitals(self):
            if self._delay_hp > self._hp:
                self._delay_hp -= (self._delay_hp - self._hp) * 0.1
                if self._delay_hp < 0.1:
                    self._delay_hp = 0
            else:
                self._delay_hp = self._hp
        
        def draw_health_bar(self,x,y):
            if self.delay_hp > 0:
                #canvas, cam_x-1350, cam_y+1000
                bar_width = 350    # 血条总长度（像素）
                bar_height = 28    # 血条高度
                ratio = max(0, min(self._hp / self.max_hp, 1))
                ratio2 = max(0, min(self.delay_hp / self.max_hp, 1))
                pygame.draw.rect(canvas, (30, 30, 30), (x, y, bar_width, bar_height))
                pygame.draw.rect(canvas, (255, 255, 255), (x, y, int(bar_width * ratio2), bar_height))
                #color = (42, 174, 42) if ratio > 0.5 else (218, 165, 32) if ratio > 0.2 else (178, 34, 34)
                color =(70,150,190)
                pygame.draw.rect(canvas, color, (x, y, int(bar_width * ratio), bar_height))
                pygame.draw.rect(canvas, (100, 100, 100), (x, y, bar_width, bar_height), 2)
                # 创建一个带 Alpha 的临时 Surface 来画半透明高光
                highlight_surf = pygame.Surface((int(bar_width * ratio), bar_height // 2), pygame.SRCALPHA)
                highlight_surf.fill((255, 255, 255, 40)) # 最后一个值 40 是透明度，非常淡
                canvas.blit(highlight_surf, (x, y))


    #僵尸加载
    ZOMBIE_CONFIG={
        "common":{
            "name":"common",
            "img":[load(file="codemao\zombie\common1.png",x=225),load(file="codemao\zombie\common2.png",x=225)],
            "hp":200,
            "speed":15
        },
        "crazy":{
            "name":"crazy",
            "img":[load(file="codemao\zombie\crazy1.png",x=225),load(file="codemao\zombie\crazy2.png",x=225)],
            "hp":100,
            "speed":18
        },
        "evil":{
            "name":"evil",
            "img":[load(file="codemao\zombie\evil1.png",x=225),load(file="codemao\zombie\evil2.png",x=225)],
            "hp":100,
            "speed":12
        },
        "iron":{
            "name":"iron",
            "img":[load(file="codemao\zombie\iron1.png",x=225),load(file="codemao\zombie\iron2.png",x=225)],
            "hp":500,
            "speed":12
        },
        "ghost":{
            "name":"ghost",
            "img":[load(file="codemao\zombie\ghost.png",x=225),load(file="codemao\zombie\ghost.png",x=225)],
            "hp":150,
            "speed":12
        },
        "virus":{
            "name":"virus",
            "img":[load(file=r"codemao\zombie\virus1.png",x=225),load(file=r"codemao\zombie\virus2.png",x=225)],
            "hp":700,
            "speed":12
        }

    }
    class Zombie(pygame.sprite.Sprite):
        def __init__(self,config):
            super().__init__()
            self.name=config["name"]
            self.img = [image.copy() for image in config["img"]]
            self.max_hp=config["hp"]
            self.current_hp=config["hp"]
            self.speed=config["speed"]
            self.x=WORLD_WIDTH- 225
            self.alpha=255
            self.y=random.randint(0, WORLD_HEIGHT - 225)
            self.idx=0
            self.rect = None
            self.size= 225
            self.alive_time = None
            self.last_switch_time = 0

        def take_damage(self, amount):
                """受伤逻辑"""
                self.current_hp -= amount

        def update(self):
            """每一帧的动作：比如向左移动"""
            if wall.hp > 0 and player.hp > 0 and show2 == False:#确保游戏没有暂停

                canvas.blit(self.img[self.idx], (self.x+ cam_x, self.y+ cam_y))
                self.x -= self.speed  # 移动逻辑

                if current_time - self.last_switch_time > 300:
                    self.idx= 1 - self.idx
                    self.last_switch_time = current_time

                if self.x < -self.size-250:
                    self.alpha -=5
                    self.img[self.idx].set_alpha(self.alpha)
                    if self.alpha <=0:
                        self.current_hp = 0

                self.rect = pygame.Rect(self.x, self.y, 225, 225)#碰撞逻辑
                if player_rect.colliderect(self.rect):
                    if current_time - player.last_hit_time > hit_cooldown:
                        player.hp -= 5
                        player.last_hit_time= current_time
    

    class Manage:
        def __init__(self,config):
            self.config=config
            self.zombie_list=[]

        def add(self,name):
            new_zombie=Zombie(self.config[name])
            self.zombie_list.append(new_zombie)
            
        def update_all(self):
            for zombie in self.zombie_list:
                zombie.update() #
            # 2. 创建一个空列表，用来存放“还活着”的僵尸
            alive_zombies = []
            # 3. 遍历当前的僵尸名单
            for zombie in self.zombie_list:
                # 检查血量是否大于 0
                if zombie.current_hp > 0:
                    # 如果活着，就把它放进临时名单里
                    alive_zombies.append(zombie)
                else:
                    print(f"{zombie.name} is dead")
            # 4. 最后，用这个只包含活僵尸的新名单替换掉旧名单
            self.zombie_list = alive_zombies


    # 角色动画加载
    PLAYER_SIZE = 200
    ANIM_SPEED = 20
    player_x,player_y=LOGIC_W//2 - PLAYER_SIZE//2, LOGIC_H//2 - PLAYER_SIZE//2
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
    ENEMY_SIZE = 225
    ENEMY_ANIM_SPEED = 30 
    enemy_frames = []
    e_files = ["codemao\zombie\common1.png", "codemao\zombie\common2.png"]

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
        global mouse_was_pressed
        l_mx, l_my = get_logic_mouse()
        is_hover = x < l_mx < x + w and y < l_my < y + h
        c = [min(i+40, 255) for i in color] if is_hover else color
        pygame.draw.rect(canvas, c, (x, y, w, h), border_radius=15)
        txt = ui_font.render(text, True, (255, 255, 255))
        canvas.blit(txt, txt.get_rect(center=(x + w/2, y + h/2)))
        clicked = False
        mouse_down = pygame.mouse.get_pressed()[0] # 获取左键实时状态
        if is_hover and mouse_down:
            if not mouse_was_pressed:
                clicked = True
                mouse_was_pressed = True
        elif not mouse_down:
            mouse_was_pressed = False
        return clicked


    '''def draw_btn(text, x, y, w, h, color):#长按普通按钮
        l_mx, l_my = get_logic_mouse()
        is_hover = x < l_mx < x + w and y < l_my < y + h
        c = [min(i+40, 255) for i in color] if is_hover else color
        pygame.draw.rect(canvas, c, (x, y, w, h), border_radius=15)
        txt = ui_font.render(text, True, (255, 255, 255))
        canvas.blit(txt, txt.get_rect(center=(x + w/2, y + h/2)))
        return is_hover and pygame.mouse.get_pressed()[0]'''
    

    def draw_aim_scope(surface, pos, size=40):#绘制瞄镜
        """
        在指定位置绘制红色瞄准镜
        :param surface: 绘图表面
        :param pos: 鼠标位置 (x, y)
        :param size: 瞄准镜基准大小 (建议范围 10-50)
        """
        RED = (255, 0, 0)
        px, py = pos
        if px < player_x+PLAYER_SIZE: 
            px = player_x+PLAYER_SIZE
            pos = (px, py)
        # --- 1. 比例参数计算 ---
        # 我们让所有尺寸都随 size 等比例变化
        dot_radius = max(1, int(size * 0.2))      # 中心红点半径 (size的20%)
        ring_radius = size                        # 外圈半径
        ring_width = max(1, int(size * 0.15))     # 外圈线宽 (size的15%)
        
        line_gap = int(size * 0.6)                # 十字线起始点（距离中心的间隙）
        line_length = int(size * 1.5)             # 十字线延伸终点
        line_width = max(1, int(size * 0.1))      # 十字线宽度
        # 绘制中心红点
        pygame.draw.circle(surface, RED, pos, dot_radius)
        pygame.draw.circle(surface, RED, pos, ring_radius, ring_width)
        pygame.draw.line(surface, RED, (px - line_length, py), (px - line_gap, py), line_width)
        pygame.draw.line(surface, RED, (px + line_gap, py), (px + line_length, py), line_width)
        pygame.draw.line(surface, RED, (px, py - line_length), (px, py - line_gap), line_width)
        pygame.draw.line(surface, RED, (px, py + line_gap), (px, py + line_length), line_width)

    def draw_custom_cursor(surface, pos, cursor_image):#绘制自定义光标
        """
        在鼠标位置绘制图片光标
        :param surface: 绘图表面 (canvas)
        :param pos: 鼠标位置 (mx, my)
        :param cursor_image: 已经加载好的光标图片
        """
        cursor_rect = cursor_image.get_rect(topleft=pos)
        surface.blit(cursor_image, cursor_rect)


    class UIButton:
        def __init__(self, img_normal, img_hover, x, y):
            self.img_normal = img_normal
            self.img_hover = img_hover
            self.rect = self.img_normal.get_rect(topleft=(x, y))
            
            # 核心状态：这才是类最强大的地方，每个实例都有自己的“记忆”
            self.is_pressed = False
            
        def click(self):#点击按钮
                """核心逻辑：自己获取坐标，自己判断点击，在主循环中只需 if btn.check_click(): """
                self.clicked = False
                # 1. 直接在类方法内部获取逻辑鼠标位置
                l_mx, l_my = get_logic_mouse()
                mouse_down = pygame.mouse.get_pressed()[0]
                is_hover = self.rect.collidepoint(l_mx, l_my)
                if is_hover:
                    if mouse_down:
                        self.is_pressed = True # 记录在按钮内按下了
                    else:
                        if self.is_pressed: # 如果上一帧按着，这一帧松开了
                            self.is_pressed = False
                            self.clicked = True
                else:
                    if not mouse_down:
                        self.is_pressed = False

                curr_img = self.img_hover if (is_hover or self.is_pressed) else self.img_normal
                if is_hover and mouse_down and self.is_pressed:
                    # 复制一份图片避免污染原始素材
                    display_img = curr_img.copy()
                    # 创建黑色遮罩，数值越大越暗（40-60效果较好）
                    dark_mask = pygame.Surface(display_img.get_size()).convert_alpha()
                    dark_mask.fill((50, 50, 50)) 
                    # 使用减法混合实现变暗
                    display_img.blit(dark_mask, (0, 0), special_flags=pygame.BLEND_RGB_SUB)
                    canvas.blit(display_img, self.rect)
                else:
                    # 正常显示
                    canvas.blit(curr_img, self.rect)
                return self.clicked
        
        def press(self):
            l_mx, l_my = get_logic_mouse()
            rect = self.img_normal.get_rect(topleft=self.rect.topleft)
            is_hover = rect.collidepoint(l_mx, l_my)
            mouse_down = pygame.mouse.get_pressed()[0]
            curr_img = self.img_hover if is_hover else self.img_normal
            if is_hover and mouse_down and self.is_pressed:
                # 复制一份图片避免污染原始素材
                display_img = curr_img.copy()
                # 创建黑色遮罩，数值越大越暗（40-60效果较好）
                dark_mask = pygame.Surface(display_img.get_size()).convert_alpha()
                dark_mask.fill((50, 50, 50)) 
                # 使用减法混合实现变暗
                display_img.blit(dark_mask, (0, 0), special_flags=pygame.BLEND_RGB_SUB)
                canvas.blit(display_img, self.rect)
            else:
                # 正常显示
                canvas.blit(curr_img, self.rect)
            return is_hover and pygame.mouse.get_pressed()[0]
        
    
    

    def draw_drop_rect():
        return pygame.Rect(drop_x+130, drop_y+445, 180, 125)
    drop_rect = pygame.Rect(drop_x+130, drop_y+445, 180, 125)


    btn_x = LOGIC_W // 2 - BTN_W // 2
    btn_y = LOGIC_H // 2

    start_btn = UIButton(btn_normal, btn_hover, btn_x, btn_y-100)
    help_btn = UIButton(btn_help_normal, btn_help_hover,btn_x, btn_y+320)
    close_help_btn = UIButton(btn_close_normal, btn_close_hover, 2987, 70)

    back_btn = UIButton(btn_back_normal, btn_back_hover, btn_x+223, btn_y+350)
    exit_btn = UIButton(exit_normal, exit_hover, 930, 900)
    continue_btn = UIButton(continue_normal, continue_hover, 1330, 900)
    mute_f_btn = UIButton(mute_f_normal, mute_f_hover, 1730, 900)
    mute_t_btn = UIButton(mute_t_normal, mute_t_hover, 1730, 900)

    menu_btn = UIButton(menu_normal, menu_hover, 2130, 900)
    

    # --- 5. 主循环 ---
    while True:
        frame_counter += 1 
        # 获取鼠标实时坐标
        mouse_pos = pygame.mouse.get_pos()
        mouse_x, mouse_y = mouse_pos
        
        # --- 枪械指向逻辑 ---
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.VIDEORESIZE:
                screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)

            if event.type == pygame.KEYDOWN:
                if scene == 'GAME' and player.hp > 0 and wall.hp > 0:
                    if event.key == pygame.K_F3: #开发者模式开关
                        developer_mode = not developer_mode

                    elif event.key == pygame.K_ESCAPE or event.key == pygame.K_p:
                        show2 = not show2
                        if show2:
                            # 记录开始暂停的时间点
                            start_pause_time = pygame.time.get_ticks()
                        else:
                            # 取消暂停时，计算刚才停了多久，并累加到总暂停时间里
                            total_paused_time += (pygame.time.get_ticks() - start_pause_time)

                    elif not show2:
                        if event.key == pygame.K_r: #换弹
                            player.current_weapon.reload()
                        elif event.key == pygame.K_q: #换武器
                            if rec_status == False:
                                player.switch_weapon()
                        elif event.key == pygame.K_e: #背包开关
                            hotbar_status = not hotbar_status
                        elif hotbar_status:
                            if event.key in [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5, pygame.K_6]: #使用物品
                                key_idx = event.key - pygame.K_1
                                player.use_item(key_idx, player)


        canvas.fill((0, 0, 0))

        if scene == 'MENU':
            if pygame.mixer.music.get_busy():
                pass
            else:
                if os.path.exists(bgm_path2):
                    pygame.mixer.music.load(bgm_path2)
                    if mute == False:
                        pygame.mixer.music.set_volume(0.6) # 设置音量
                    pygame.mixer.music.play(-1) # 循环播放音乐

            # 背景渲染
            offset_x = (LOGIC_W//2 - (player_world_x + PLAYER_SIZE//2)) % TILE_W
            offset_y = (LOGIC_H//2 - (player_world_y + PLAYER_SIZE//2)) % TILE_H
            for x in range(-TILE_W, LOGIC_W + TILE_W, TILE_W):
                for y in range(-TILE_H, LOGIC_H + TILE_H, TILE_H):
                    canvas.blit(tile_img2, (x + offset_x, y + offset_y))
            canvas.blit(title_img, (LOGIC_W // 2 - title_img.get_width() // 2, 200))

            #if btn(btn_normal, btn_hover, btn_x, btn_y-100):
            if start_btn.click() and show1==False:
                scene = 'GAME'
                enemies = [] # 重置敌人
                last_hit_time = 0 # 重置被撞时间戳
                p_idx=0 #玩家动画帧索引
                grave_move=0 #墓碑移动距离
                grave_a=0 #墓碑加速度
                grave_alpha=0 #墓碑透明度
                wall_alpha=255 #墙透明度
                final_x, final_y = None, None #墙死后玩家位置
                wall_img.set_alpha(wall_alpha)
                wall_life.set_alpha(wall_alpha)
                show2 = False
                last_drop_time = -2500 #上次空投时间戳
                total_paused_time = 0
                start_pause_time = 0
                begin_time = pygame.time.get_ticks() #游戏开始时间戳
                t_drop_y = -1410 #空投真实y坐标
                drop_alpha = 255 #空投图标透明度
                drop_opening = 0 #开箱动画计时
                drop_status = False #是否可开箱
                draw_open_bar= False
                game_over_sound_status = False
                hotbar_status=False

                score = 0 #分数
                rec_status = False #是否在更换弹药中
                drop_list=[]#掉落物列表
                cursor_visible = True
                last_mouse_move_time = pygame.time.get_ticks()#记录光标最后移动时间

                player = Player(WEAPON_CONFIG) #实例化玩家
                zombie_manager = Manage(ZOMBIE_CONFIG)
                wall = Wall() #实例化城墙

                player_world_x, player_world_y = WORLD_WIDTH // 2, WORLD_HEIGHT // 2
                if os.path.exists(bgm_path):
                    pygame.mixer.music.stop()
                    pygame.mixer.music.load(play_bgm)
                    if mute == False:
                        pygame.mixer.music.set_volume(0.6) # 设置音量
                    pygame.mixer.music.play(-1) # 循环播放音乐
                pygame.time.delay(200)
            
            #if btn(btn_help_normal, btn_help_hover, btn_x, btn_y+320):
            if help_btn.click() and show1==False:
                show1 = True
            
            
            if show1:
                rect = img.get_rect()
                rect.center = (1600, 900)
                help_paper.set_alpha(255)
                canvas.blit(help_paper, center(help_paper,1600,900))
                if close_help_btn.click() and show1==True:
                    show1 = False
            
            draw_custom_cursor(canvas, get_logic_mouse(), cursor)


        elif scene == 'GAME':

            player.update_vitals() 
            wall.update_vitals()


            if show2 == False:
                current_time = pygame.time.get_ticks() - total_paused_time - begin_time
            # 移动逻辑
            if player.hp > 0 and wall.hp > 0 and show2 == False:
                keys = pygame.key.get_pressed()
                if keys[pygame.K_a]: player_world_x -= (player_speed-player.current_weapon.weight)
                if keys[pygame.K_d]: player_world_x += (player_speed-player.current_weapon.weight)
                if keys[pygame.K_w]: player_world_y -= (player_speed-player.current_weapon.weight)
                if keys[pygame.K_s]: player_world_y += (player_speed-player.current_weapon.weight)

                if keys[pygame.K_j]: player.current_weapon.fire()


            
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

            # --- 碰撞检测准备 ---
            # 玩家在逻辑世界中的矩形 (x, y, w, h)
            player_rect = pygame.Rect(player_world_x, player_world_y, PLAYER_SIZE, PLAYER_SIZE)



            #空投绘制
            if show2 == False:
                if player_rect.colliderect(drop_rect) and drop_status == True:
                    drop_opening += 1
                    draw_open_bar = True
                    #open_bar(canvas,cam_x+drop_x+118,cam_y+t_drop_y+290,drop_opening,100)
                    if drop_opening >= 100:
                        if developer_mode:
                            drop_list.append({"type":test_weapon,"x":drop_x,"y":t_drop_y})
                        else:
                            drop_list.append({"type":weapon_list[random.randint(2, len(weapon_list)-1)],"x":drop_x,"y":t_drop_y})
                        drop_status = False
                        draw_open_bar = False
                elif  not player_rect.colliderect(drop_rect) and drop_status ==True:
                    draw_open_bar = False
                    drop_opening = 0
                if drop_status == False:
                    drop_rect=pygame.Rect(4800, -1410, 0, 0)
            if current_time - last_drop_time > drop_cooldown: #每32秒刷新一次空投
                drop_x,drop_y = random.randint(400,4800),random.randint(-200,1500)
                t_drop_y = -1410
                move_item(drop1, drop_x, t_drop_y)
                last_drop_time = current_time
                drop_alpha = 255
                drop2.set_alpha(drop_alpha)
                drop_opening = 0
                drop_cooldown = random.randint(30000, 40000) #刷新后下次刷新间隔15-30秒
            elif drop_cooldown- current_time + last_drop_time < 5000 and drop_opening <100: #刷新前5秒闪烁提示
                if (current_time // 400) % 2 == 0: #每600毫秒闪烁一次
                    drop_alpha = 255
                    drop2.set_alpha(drop_alpha)
                    move_item(drop2, drop_x, t_drop_y)
                    drop_status=True
                    drop_rect=draw_drop_rect()
                else:
                    drop_alpha = 160
                    drop2.set_alpha(drop_alpha)
                    move_item(drop2, drop_x, t_drop_y)
                    drop_status=True
                    drop_rect=draw_drop_rect()        
            elif drop_opening < 100:
                if drop_y > t_drop_y:
                    if show2 == False:
                        t_drop_y += 10
                    move_item(drop1, drop_x, t_drop_y)
                else:
                    move_item(drop2, drop_x, t_drop_y)
                    drop_status=True
                    drop_rect=draw_drop_rect()


            #掉落物绘制
            if drop_list:
                for drop in drop_list[:]:
                    pygame.draw.ellipse(canvas, (45,29,36), [cam_x+drop["x"]+123, cam_y+drop["y"]+502, 260, 50], width=0)
                    move_item(main_weapon_img[drop["type"]], drop["x"]+90, drop["y"]+420)
                    drop_item_rect = pygame.Rect(drop["x"]+180, drop["y"]+450, 140, 68)
                    if player_rect.colliderect(drop_item_rect):
                        pick_text = ui_font.render(f"按下F拾取{drop['type'].strip('_')}", True, (0, 49, 207))
                        canvas.blit(pick_text, (player_x-20, player_y+240))
                        if show2 == False and player.hp>0 and wall.hp>0 and keys[pygame.K_f]:
                            if rec_status == False:
                                player.pick_up(drop["type"])
                                drop_list.remove(drop)




            # --- 敌人更新与绘制 ---

            # 敌人生成
            if wall.hp > 0 and player.hp > 0 and show2 == False:
                if frame_counter % SPAWN_RATE == 0:
                    spawn_y = random.randint(0, WORLD_HEIGHT - ENEMY_SIZE)
                    enemies.append({"x": WORLD_WIDTH, "y": spawn_y, "born": frame_counter, "alpha": 255})

            for e in enemies[:]:
                draw_x, draw_y = e["x"] + cam_x, e["y"] + cam_y
                if wall.hp > 0 and player.hp > 0 and show2 == False:
                    e["x"] -= ENEMY_SPEED 
                    # 创建敌人的矩形进行碰撞判定
                    enemy_rect = pygame.Rect(e["x"], e["y"], ENEMY_SIZE, ENEMY_SIZE)

                    # 【碰撞逻辑】
                    if player_rect.colliderect(enemy_rect):
                        if current_time - last_hit_time > hit_cooldown:
                            player.hp -= 5
                            last_hit_time = current_time #更新被撞时间戳
                    if e["x"] <= -ENEMY_SIZE-250: #敌人走出左边界后消失
                        e["alpha"] -= 5
                        if e["alpha"] <= 0:
                            wall.hp -= 5
                            enemies.remove(e)

                if -ENEMY_SIZE < draw_x < LOGIC_W and -ENEMY_SIZE < draw_y < LOGIC_H:
                    alive_ticks = frame_counter - e["born"]
                    e_idx = (alive_ticks // ENEMY_ANIM_SPEED) % len(enemy_frames)
                    enemy_frames[e_idx].set_alpha(e["alpha"])
                    canvas.blit(enemy_frames[e_idx], (draw_x, draw_y))
            
            #——————僵尸绘制——————
            zombie_manager.update_all()
            
            
            if wall.hp > 0:
                # 玩家绘制
                if keys[pygame.K_a] or keys[pygame.K_d] or keys[pygame.K_w] or keys[pygame.K_s]:
                    p_idx = (frame_counter // ANIM_SPEED) % len(player_frames)
                    canvas.blit(player_frames[p_idx], (player_x, player_y))
                else:
                    canvas.blit(player_frames[p_idx], (player_x, player_y))
                #枪械绘制
                if player.hp > 0:
                    static_item(vice_weapon_img[player.vice_weapon.name],player_x-48,player_y-50-10*p_idx)#副武器
                    if not player.sniper_mode:#主武器
                        static_item(main_weapon_img[player.current_weapon.name],player_x,player_y+55-10*p_idx)
                    else:
                        # --- 枪械指向逻辑 ---
                        player_display_x = player_world_x + cam_x+156
                        player_display_y = player_world_y + cam_y+120-10*p_idx
                        dx = get_logic_mouse()[0] - player_display_x
                        if dx < 44:
                            dx = 44
                        dy = get_logic_mouse()[1] - player_display_y
                        rads = math.atan2(dy, dx) #计算鼠标与玩家中心的角度
                        final_angle = -(math.degrees(rads))
                        draw_rotating_gun(canvas, main_weapon_img[player.current_weapon.name],[player_x+156,player_y+120-10*p_idx], final_angle)


            move_item(fence,0,2190) #下围栏
            move_item(tree1,-830,-630) #左树
            move_item(tree2,5400,-1900)#右树
            move_item(wall_img,-1500,-725) #墙
            move_item(wall_life,-1480,1050) #墙血量
            if draw_open_bar == True:
                open_bar(canvas,cam_x+drop_x+118,cam_y+t_drop_y+290,drop_opening)

            wall.draw_health_bar(cam_x-1422, cam_y+1000)
            if wall.hp > 0:
                player.draw_health_bar(canvas, LOGIC_W//2-120, LOGIC_H//2-160)
            
            player.current_weapon.update() # 更新武器状态（如换弹计时,由于需要换弹药进度条，所以要放在下面，确保图层在上面）

                #——————道具栏绘制——————
            if wall.hp > 0 and player.hp > 0:
                if hotbar_status:
                    for i,k in zip(player.hotbar, range(6)):
                        if i !=None:
                            center_static_item(i.icon,90, 380+180*k)#player.hotbar.index(i)
                        else:
                            center_static_item(empty_icon,90, 380+180*k)
                        center_static_item(use_item_sign ,160 ,400+180*k)
                        canvas.blit(ui_font.render(f"{k+1}", True, (27, 27, 27)), (150 ,370+180*k))

            #----弹药显示----
            if player.current_weapon.name != "empty":
                if player.current_weapon.current_mag >= 100:#显示主弹夹
                    static_item(num_img[player.current_weapon.current_mag//100], current_mag_x, current_mag_y) 
                if player.current_weapon.current_mag >= 10:
                    static_item(num_img[(player.current_weapon.current_mag//10)%10], current_mag_x + 60, current_mag_y) 
                static_item(num_img[player.current_weapon.current_mag%10], current_mag_x + 120, current_mag_y) 

                if player.current_weapon.reserve_ammo >= 100:#显示副弹夹
                    static_item(num_img2[player.current_weapon.reserve_ammo//100], reserve_ammo_x, reserve_ammo_y) 
                elif 100>player.current_weapon.reserve_ammo >= 10:
                    static_item(num_img2[(player.current_weapon.reserve_ammo//10)%10], reserve_ammo_x, reserve_ammo_y) 
                else:
                    static_item(num_img2[player.current_weapon.reserve_ammo%10], reserve_ammo_x, reserve_ammo_y) 
                if player.current_weapon.reserve_ammo >= 100:
                    static_item(num_img2[(player.current_weapon.reserve_ammo//10)%10], reserve_ammo_x + 45, reserve_ammo_y) 
                elif 100>player.current_weapon.reserve_ammo >= 10:
                    static_item(num_img2[player.current_weapon.reserve_ammo%10], reserve_ammo_x + 45, reserve_ammo_y)
                else:
                    pass
                if player.current_weapon.reserve_ammo >= 100:
                    static_item(num_img2[player.current_weapon.reserve_ammo%10], reserve_ammo_x + 90, reserve_ammo_y)


            #----得分显示----
            if score < 100000:
                if score >=10000:
                    static_item(num_img0[score//10000], score_x, score_y)
                if score >=1000:
                    static_item(num_img0[(score//1000)%10], score_x + 50, score_y)
                if score >=100:
                    static_item(num_img0[(score//100)%10], score_x + 100, score_y)
                if score >=10:
                    static_item(num_img0[(score//10)%10], score_x + 150, score_y)
                static_item(num_img0[score%10], score_x + 200, score_y)
            else:
                static_item(num_img0[9], score_x, score_y)
                static_item(num_img0[9], score_x + 50, score_y)
                static_item(num_img0[9], score_x + 100, score_y)
                static_item(num_img0[9], score_x + 150, score_y)
                static_item(num_img0[9], score_x + 200, score_y)
            


            #暂停菜单
            if show2:
                rect = img.get_rect()
                rect.center = (1600, 900)
                pause_page.set_alpha(255)
                canvas.blit(pause_page, center(pause_page,1600,900))

                if continue_btn.click():
                    show2 = not show2
                    if show2:
                        # 记录开始暂停的时间点
                        start_pause_time = pygame.time.get_ticks()
                    else:
                        # 取消暂停时，计算刚才停了多久，并累加到总暂停时间里
                        total_paused_time += (pygame.time.get_ticks() - start_pause_time)

                if exit_btn.click():
                    scene = 'RESULT'
                    pygame.mixer.music.stop()
                    pygame.time.delay(200)

                if menu_btn.click():
                    play_bgm = bgm_tuple[random.randint(0,2)]
                    scene = 'MENU'
                    pygame.mixer.music.stop()
                    pygame.time.delay(200)

                if not mute:
                    if mute_f_btn.click():
                        pygame.mixer.music.set_volume(0) # 静音
                        game_over_sound.set_volume(0) # 静音

                        rifle_sound.set_volume(0)
                        lmg_sound.set_volume(0)
                        sniper_sound.set_volume(0)
                        submachine_sound.set_volume(0)
                        shotgun_sound.set_volume(0)
                        laser_sound.set_volume(0)
                        howitzer_sound.set_volume(0)
                        rocket_boom_sound.set_volume(0)

                        mute = True
                else:
                    if mute_t_btn.click():
                        pygame.mixer.music.set_volume(0.6) # 取消静音
                        game_over_sound.set_volume(0.8) # 取消静音

                        rifle_sound.set_volume(0.5)
                        lmg_sound.set_volume(0.5)
                        sniper_sound.set_volume(0.1)
                        submachine_sound.set_volume(0.3)
                        shotgun_sound.set_volume(0.5)
                        laser_sound.set_volume(0.3)
                        howitzer_sound.set_volume(0.3)
                        rocket_boom_sound.set_volume(0.3)

                        mute = False


            #开发者模式
            if developer_mode:
                fps = int(clock.get_fps())
                fps_text = ui_font.render(f"FPS: {fps}", True, (255, 255, 0))
                current_time_text = ui_font.render(f"Time: {current_time//1000}s", True, (255, 255, 0))
                health_text = ui_font.render(f"HP: {player.hp}", True, (255, 255, 0))
                location_text = ui_font.render(f"cam_x: {cam_x}, cam_y: {cam_y}", True, (255, 255, 0))
                location_text2 = ui_font.render(f"player_world_x: {player_world_x}, player_world_y: {player_world_y}", True, (255, 255, 0))
                frame_counter_text = ui_font.render(f"Toatal_pause_time: {total_paused_time}", True, (255, 255, 0))
                wall_delay_hp_text = ui_font.render(f"Wall Delay HP: {wall.delay_hp}", True, (255, 255, 0))
                develop_show_list=[
                    fps_text,
                    current_time_text,
                    health_text,
                    location_text,
                    location_text2,
                    frame_counter_text,
                    wall_delay_hp_text
                ]
                for i, text in enumerate(develop_show_list):
                    canvas.blit(text, (developer_x, developer_y + i*40))
                    final_developer_y = developer_y + i*40
                if draw_btn("+player.hp", developer_x, final_developer_y+70, 150, 60 ,(60, 60, 60)):
                    player.hp += 10
                if draw_btn("-wall.hp", developer_x, final_developer_y+140, 150, 60 ,(60, 60, 60)):
                    wall.hp -= 10
                if draw_btn("结束", developer_x, final_developer_y+210, 150, 60, (60, 60, 60)):
                    scene = 'RESULT'
                    pygame.mixer.music.stop()
                    pygame.time.delay(200)
                if draw_btn("add_score", developer_x, final_developer_y+280, 150, 60, (60, 60, 60)):
                    score +=1
                if draw_btn("weapon", developer_x, final_developer_y+350, 150, 60, (60, 60, 60)):
                    player.pick_up(test_weapon)
                if draw_btn("+item", developer_x, final_developer_y+420, 150, 60, (60, 60, 60)):
                    player.get_item("kit")
                if draw_btn("+zombie", developer_x, final_developer_y+490, 150, 60, (60, 60, 60)):
                    zombie_manager.add("crazy")

            #——————光标显示变化——————
            for event in pygame.event.get():
                if event.type == pygame.MOUSEMOTION:
                    last_mouse_move_time = current_time
            if current_time - last_mouse_move_time > 2000 and not show2: #没动鼠标就隐藏光标
                cursor_visible = False
            else:
                cursor_visible = True
            if player.sniper_mode and show2==False and player.hp > 0 and wall.hp > 0:#绘制瞄准镜
                draw_aim_scope(canvas, get_logic_mouse())
            else:
                if cursor_visible:
                    draw_custom_cursor(canvas, get_logic_mouse(), cursor)
            
            if player.hp <= 0:#玩家死亡
                if not game_over_sound_status:
                    game_over_sound.play()
                    game_over_sound_status=True
                if pygame.mixer.music.get_busy():
                    pygame.mixer.music.stop()
                grave_move+=2+grave_a #墓碑移动
                grave_a+=0.5 #墓碑加速度
                if grave_alpha < 255:
                    grave_alpha += 16 #墓碑淡出
                    grave.set_alpha(grave_alpha)
                static_item(grave, (LOGIC_W//2 - PLAYER_SIZE//2)-20,((LOGIC_H//2 - PLAYER_SIZE//2)-224)+grave_move) #玩家死亡后绘制墓碑
                if grave_move > 200:
                    pygame.time.delay(600)
                    scene = 'RESULT'
                    pygame.time.delay(200)

            elif wall.hp <= 0:#墙被破坏
                if pygame.mixer.music.get_busy():
                    pygame.mixer.music.stop()
                if final_x == None and final_y == None:
                    final_x , final_y = player_world_x, player_world_y
                move_item(player_frames[0],final_x,final_y)
                move_item(main_weapon_img[player.current_weapon.name],final_x,final_y+55)
                move_item(vice_weapon_img[player.vice_weapon.name],final_x-48,final_y-55)
                if cam_x < 1500:
                    if not game_over_sound_status:
                        game_over_sound.play()
                        game_over_sound_status = True
                    player_world_x -= 30
                else:
                    if cam_x == 1500 and not game_over_sound_status:
                        game_over_sound.play()
                        game_over_sound_status = True
                    if wall.delay_hp <= 0 :
                        wall_alpha -= 5
                        wall_img.set_alpha(wall_alpha)
                        wall_life.set_alpha(wall_alpha)
                        if wall_alpha <= 0:
                            scene = 'RESULT'
                            pygame.time.delay(200)

        elif scene == 'RESULT':
            player.sniper_mode = False
            for x in range(-TILE_W, LOGIC_W + TILE_W, TILE_W):
                for y in range(-TILE_H, LOGIC_H + TILE_H, TILE_H):
                    canvas.blit(tile_img3, (x + offset_x, y + offset_y))
            res_msg = title_font.render("得分：", True, (211,211,211))
            title_font.set_bold(True)
            canvas.blit(res_msg, res_msg.get_rect(center=(LOGIC_W//2+30, LOGIC_H//3)))
            score_msg = score_font.render(str(score), True, (211,211,211))
            score_font.set_bold(True)
            canvas.blit(score_msg, score_msg.get_rect(center=(LOGIC_W//2, LOGIC_H//3+320)))
            '''if draw_btn("返回菜单", LOGIC_W//2-150, LOGIC_H//2, 300, 80, (50, 150, 255)):
                scene = 'MENU'
                pygame.time.delay(200)'''
            if back_btn.click():
                game_over_sound.stop()
                play_bgm = bgm_tuple[random.randint(0,2)]
                scene = 'MENU'
                pygame.mixer.music.stop()
                pygame.time.delay(200)
                # 缩放投影
            draw_custom_cursor(canvas, get_logic_mouse(), cursor)
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