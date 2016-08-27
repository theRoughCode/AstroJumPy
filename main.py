from __future__ import division
import os
import random
import pickle

import pygame_sdl2
pygame_sdl2.import_as_pygame()
import pygame


# SET WINDOW POSITION
import sys

pygame.mixer.pre_init(44100, 16, 2, 2048)  # prevents audio lag
pygame.mixer.init()
pygame.init()

try:
    import android
except ImportError:
    android = None

def get_display_dimensions(width, height):
    monitor_res = pygame.display.Info()  # gets display screen resolution
    monitor_x = monitor_res.current_w
    monitor_y = monitor_res.current_h
    # SCALING TO ADAPT TO DIFFERENT SCREEN SIZES
    scaling_x = 1
    scaling_y = 1
    # BLACK SPACE TO FILL UP LARGER SCREENS
    padding_x = 0
    padding_y = 0
    
    if android:
        scaling_x = monitor_x / width
        scaling_y = monitor_y / height
        
        if scaling_x < scaling_y:  # HAS EMPTY SPACE VERT.
            scaling_y = scaling_x
            width = monitor_x
            height *= scaling_y
            padding_y = monitor_y - height
        else:  # HAS EMPTY SPACE HOR.
            scaling_x = scaling_y
            width *= scaling_x
            height = monitor_y
            padding_x = monitor_x - width
    
    else:
        if (width > monitor_x):
            scaling_factor = monitor_x / width
            width = monitor_x
            height *= scaling_factor
        elif (height > monitor_y):
            scaling_factor = monitor_y / height
            height = monitor_y
            width *= scaling_factor

    return (int(width), int(height), scaling_x, scaling_y, padding_x, padding_y)

display_dim = get_display_dimensions(640, 960)
DISPLAY_WIDTH = display_dim[0]
DISPLAY_HEIGHT = display_dim[1]
SCALING_X = display_dim[2]
SCALING_Y = display_dim[3]
PADDING_X = display_dim[4]  
PADDING_Y = display_dim[5]  


# SET UP DISPLAY WINDOW
gameDisplay = pygame.display.set_mode((DISPLAY_WIDTH + PADDING_X, DISPLAY_HEIGHT + PADDING_Y))
pygame.display.set_caption('Astrojump')
gameClock = pygame.time.Clock()



# ------  PYGAME  ------
pygame.init()

# GLOBAL CONSTANTS
folder_dir = 'resource_files/'
p_astro = folder_dir + 'astro.p'  # pickled files (saved states)
p_stars = folder_dir + 'stars.p'
p_panels = folder_dir + 'panels.p'
SLEEPING = False
difficulty = ((0, 50), (3000, 60), (6000, 70), (9000, 80), (10000, "orange"), (12000, 90), (15000, 100), (16000, "red"),
              (18000, 110), (21000, 120), (24000, 130))
GAME_PAUSED = False
# GAME_FPS = 60  # SETS GAME FPS
NUM_ASTROS = 5
ASTRO_CHOSEN = 0
DT = 0.1  # higher = Faster FPS, but lesser accuracy
SCROLL_SPEED = 0
RED_PANELS_ACTIVE = False
ORANGE_PANELS_ACTIVE = False
BUTTON_SELECTED = None
B_DOWN = False
BUTTON_WIDTH = 280 * SCALING_X
BUTTON_HEIGHT = 55 * SCALING_Y
BUTTON_X = int((DISPLAY_WIDTH - BUTTON_WIDTH) / 2)

# initialize sprite groups
playergroup = pygame.sprite.Group()
panelgroup = pygame.sprite.Group()
opanelgroup = pygame.sprite.Group()
rpanelgroup = pygame.sprite.Group()

# POWER-UPS
power_timer = 0
has_power_up = False
jump_inc = False

# COLOURS
black = (0, 0, 0)
grey = (220, 220, 220)
white = (255, 255, 255)
red = (200, 0, 0)
green = (0, 200, 0)
blue = (0, 153, 255)
yellow = (200, 200, 0)
bright_red = (255, 0, 0)
bright_green = (0, 255, 0)
bright_blue = (51, 204, 255)
bright_yellow = (255, 255, 0)
neon_green = (124, 245, 54)
dark_green = (0, 153, 0)

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


# IMPORT DATA FILES
def load_file(url, pic='sprite', resize=False):
    # load image
    if pic == 'sprite':
        rfile = pygame.image.load(resource_path(folder_dir + url)).convert_alpha()
    elif pic == 'bg':
        rfile = pygame.image.load(resource_path(folder_dir + url)).convert()
    else:
        rfile = resource_path(folder_dir + url)
        
    # resize image to fit window size
    if resize:
        width = rfile.get_width()
        height = rfile.get_height()
        rfile = pygame.transform.scale(rfile, (int(width * SCALING_X), int(height * SCALING_Y)))    
    
    return rfile

try:
    # CHARACTERS
    astro_blue = load_file('astro_sprite_blue.png')
    astro_green = load_file('astro_sprite_green.png')
    astro_black = load_file('astro_sprite_black.png')
    astro_red = load_file('astro_sprite_red.png')
    astro_pink = load_file('astro_sprite_pink.png')
    # BACKGROUND
#     bg_green = load_file('bg_green.png', 'bg', resize=True)
#     bg_blue = load_file('bg_blue.png', 'bg', resize=True)
    pause_screen_bg = load_file('pause_screen_bg.png')
    dead_screen_bg = load_file('dead_screen_bg.png')
    pause_screen_bg = pygame.transform.scale(pause_screen_bg, (DISPLAY_WIDTH, DISPLAY_HEIGHT))
    dead_screen_bg = pygame.transform.scale(dead_screen_bg, (DISPLAY_WIDTH, DISPLAY_HEIGHT))
    # PANELS
    panel_green = load_file('panel_green.png', resize=True)
    panel_red = load_file('panel_red.png', resize=True)
    panel_orange = load_file('panel_orange.png', resize=True)
    PANEL_WIDTH = panel_green.get_width()
    PANEL_HEIGHT = panel_green.get_height()
    # FONTS
    # magneto_bold = load_file('MAGNETOB.ttf', False)
    # courbd = load_file('courbd.ttf', False)
    magneto_bold = courbd = gills = trajan = load_file('TrajanPro-Regular.otf', False)
    # gills = load_file('gills.ttf', False)
    # SOUND
    bounce_fx = pygame.mixer.Sound(load_file('bounce.wav', False))
    dead_fx = pygame.mixer.Sound(load_file('dead_fx.wav', False))
    intro_music = load_file('Videogame2.wav', False)
    soundtrack1 = load_file('Retro1.wav', False)
    soundtrack2 = load_file('Arcade_Funk.wav', False)
    soundtrack3 = load_file('Star Commander1.wav', False)
    soundtrack4 = load_file('Starlight.wav', False)
    soundtrack = (soundtrack1, soundtrack2, soundtrack3, soundtrack4)
    current_track = None
except:
    print('Error loading image')  
    

# FADE BACKGROUND IMAGE
def fade_bg (colour1, colour2, alpha):  # colour1 is fading bg
    alpha_vel = 0.01  # speed of fade
    c1 = [0 for i in range(3)]  # temp list
    for num in range(3):
        c1[num] = int(colour1[num] + (colour2[num] - colour1[num]) * alpha)  # move tuple elements 
    alpha += alpha_vel
    colour1 = tuple(c1)  # convert from temp list back to tuple
    return (colour1, alpha)

# play sound
def play_soundtrack(sound, repeat=False):  
    pygame.mixer.music.load(sound)
    global current_track
    current_track = sound
    if repeat:
        pygame.mixer.music.play(-1)
    else:
        pygame.mixer.music.play()
    
    

# CHARACTER    
class Astro(pygame.sprite.Sprite):
    # original dimensions
    img_height = astro_blue.get_height()
    img_width = astro_blue.get_width() / 6
    # scaled dimensions
    width = int(img_width * SCALING_X)
    height = int(img_height * SCALING_Y)
    astro_sel = ASTRO_CHOSEN  # astro sprite
    # MOVEMENT VARIABLES (self.x, self.y = UPPER-LEFT CORNER)
    x = int(DISPLAY_WIDTH / 2 - width / 2)
    dx = 0
    isDescending = False
    jump_h = None  # record height of jump
    start_y = DISPLAY_HEIGHT - (130 * SCALING_Y)  # start pos
    y = start_y
    start_dy = dy = 1.3 * SCALING_Y  # bounce velocity
    grav = -0.3 / 100 * SCALING_Y
    x_speed = 0.7 * SCALING_X  # hor velocity
    empty_x = 15 * SCALING_X  # empty space between outer rect and boots (for collisions)
    coll_y_allowance = DT * 3
    
    # INITIALIZE SPRITES FOR EASY REFERENCE
    astro_sprites = [[0 for a in range(6)] for b in range(NUM_ASTROS)]
    
    for num in range (0, 6):
        astro_sprites[0][num] = pygame.transform.scale(astro_blue.subsurface(img_width * num, 0, img_width, img_height), (width, height))
        astro_sprites[1][num] = pygame.transform.scale(astro_green.subsurface(img_width * num, 0, img_width, img_height), (width, height))
        astro_sprites[2][num] = pygame.transform.scale(astro_black.subsurface(img_width * num, 0, img_width, img_height), (width, height))
        astro_sprites[3][num] = pygame.transform.scale(astro_red.subsurface(img_width * num, 0, img_width, img_height), (width, height))
        astro_sprites[4][num] = pygame.transform.scale(astro_pink.subsurface(img_width * num, 0, img_width, img_height), (width, height))
        
    # astro[] = blue,green,black,red,pink
    # astro[][] = down,up,down_left,up_left,down_right,up_right


    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.astro_down = self.astro_sprites[ASTRO_CHOSEN][0]
        self.astro_up = self.astro_sprites[ASTRO_CHOSEN][1]
        self.astro_down_left = self.astro_sprites[ASTRO_CHOSEN][2]
        self.astro_up_left = self.astro_sprites[ASTRO_CHOSEN][3]
        self.astro_down_right = self.astro_sprites[ASTRO_CHOSEN][4]
        self.astro_up_right = self.astro_sprites[ASTRO_CHOSEN][5]
        self.image = self.astro_down
        self.rect = self.image.get_rect()
        
    def change_sprite(self, astro):
        self.astro_down = self.astro_sprites[astro][0]
        self.astro_up = self.astro_sprites[astro][1]
        self.astro_down_left = self.astro_sprites[astro][2]
        self.astro_up_left = self.astro_sprites[astro][3]
        self.astro_down_right = self.astro_sprites[astro][4]
        self.astro_up_right = self.astro_sprites[astro][5]
        self.image = self.astro_down
        self.rect = self.image.get_rect()
        self.astro_sel = astro

    def jump(self, dt):
        if self.dy < 0:  # if player is descending
            self.isDescending = True
            if not self.jump_h: 
                self.jump_h = self.y  # records jump height

            if self.dx < 0:
                self.image = self.astro_down_left
            elif self.dx > 0:
                self.image = self.astro_down_right
            else:
                self.image = self.astro_down
        else:
            self.isDescending = False
            self.jump_h = None
            
            if self.dx < 0:
                self.image = self.astro_up_left
            elif self.dx > 0:
                self.image = self.astro_up_right
            else:
                self.image = self.astro_up
        self.move(dt)
        # UPDATE MOVEMENT
        self.dy += self.grav * dt
        self.y -= self.dy * dt - SCROLL_SPEED    
        # UPDATE SPRITE RECT
        self.rect.x = self.x
        self.rect.y = self.y

    def setDir(self, pdir):
        self.dx = pdir * self.x_speed

    def move(self, dt):
        if (self.x + self.width / 2) <= 0 and self.dx < 0:
            self.x = int(DISPLAY_WIDTH + self.width / 2)
        elif (self.x - self.width / 2) >= DISPLAY_WIDTH and self.dx > 0:
            self.x = -int(self.width / 2)
        else:
            self.x += self.dx * dt

    def reset_jump(self, jump_y):
        bounce_fx.play()
        self.dy = self.start_dy
        self.y = jump_y - self.height
        
    def collide(self, sprite):
        if pygame.sprite.collide_rect(self, sprite):
            if panelgroup.has(sprite):  # panel
                collided = False
                # PREVENT JUMPING FROM PANEL SIDE
                if abs(sprite.y - (self.y + self.height)) <= self.coll_y_allowance:   
                    # REDUCES COLLISION BOX TO BOOTS PIXELS  
                    if sprite.x - self.empty_x < self.x + self.width / 2 < sprite.x + sprite.width + self.empty_x:  
                        collided = True
                return collided
            
#     def jump_inc(self):
#         self.grav = -0.2 * SCALING_Y
#     def reset_abilities(self):
#         self.grav = -0.4 * SCALING_Y

    def render(self):
        gameDisplay.blit(self.image, (self.x, self.y))  # self.x, self.y = UPPER-LEFT CORNER
    
    def update(self, *args):
        pygame.sprite.Sprite.update(self, *args)
        self.rect.x = self.x
        self.rect.y = self.y
        # UPDATE HITBOX
        self.prev_boot_pos = ((self.x + self.empty_x, self.y + self.height), (self.x + self.width - self.empty_x, self.y + self.height))
        
    def save_state(self):
        state = [self.x, self.y, self.dx, self.prev_vel, self.isDescending, self.astro_sel]  
        pickle.dump(state, open(p_astro, 'wb'), -1)
        
    def load_state(self):
        state = pickle.load(open(p_astro, 'rb'))
        self.x = state[0]
        self.y = state[1]
        self.dx = state[2]
        self.prev_vel = state[3]
        self.isDescending = state[4]
        self.change_sprite(state[5])

# def power_up(ability):
#     if ability == 'jump':
#         print("Jump Increased!")
#         global jump_inc, has_power_up, power_timer
#         jump_inc = True
#         has_power_up = True
#         power_timer = pygame.time.get_ticks()
#     elif ability == None:
#         print('Power Up Finished')
#         power_timer = 0
#         has_power_up = False
#         jump_inc = False


# PANELS
class Panel(pygame.sprite.Sprite):
    move_speed = 1 * SCALING_Y
    ttl_dist = 0
    move_finished = True
    panel_type = 'green'
    image = panel_green

    def __init__(self, x, y, width, height):
        pygame.sprite.Sprite.__init__(self)

        self.x = x
        self.y = y
        self.width = width
        self.height = height

        self.rect = self.image.get_rect()
        self.rect.x = self.x
        self.rect.y = self.y

    def is_moving(self, dist):  # initiated when panels first start shifting down
        self.ttl_dist += dist
        self.move_finished = False

    def move_down(self, dt):
        if not self.move_finished:
            global SCROLL_SPEED 
            SCROLL_SPEED = self.move_speed * dt
            if self.ttl_dist > SCROLL_SPEED:
                self.y += SCROLL_SPEED
                self.ttl_dist -= SCROLL_SPEED
            else:  # done moving
                self.y += self.ttl_dist
                self.ttl_dist = 0
                self.move_finished = True
                SCROLL_SPEED = 0

    def move_hor(self):
        pass

    def collide(self, player_obj, panel_obj):
        pass
    
    def update(self, *args):
        pygame.sprite.Sprite.update(self, *args)
        self.rect.x = self.x
        self.rect.y = self.y


class Vanish_Panel(Panel):
    def __init__(self, x, y, width, height):
        Panel.__init__(self, x, y, width, height)
        self.panel_type = 'red'
        self.image = panel_red


class Moving_Panel(Panel):
    x_speed = 0.15 * SCALING_X
    x_dist = (DISPLAY_WIDTH / 2 - PANEL_WIDTH) / 2
    dir = 1

    def __init__(self, x, y, width, height):
        Panel.__init__(self, x, y, width, height)
        self.panel_type = 'orange'
        self.image = panel_orange

        if x < self.x_dist:  # too far left
            self.min_x = 0
            self.max_x = self.x_dist * 2
        elif x + width + self.x_dist > DISPLAY_WIDTH:  # too far right
            self.max_x = DISPLAY_WIDTH - width
            self.min_x = self.max_x - self.x_dist * 2
        else:
            self.min_x = x - self.x_dist
            self.max_x = x + self.x_dist
            
        # randomize starting position
        self.x = random.randrange(int(self.min_x), int(self.max_x))
        rand = random.randint(0, 1)
        if rand == 0: self.dir = -1
        else: self.dir = 1

    def move_hor(self, dt):
        if self.dir > 0:
            if self.x > self.max_x:
                self.x = self.max_x
                self.dir = -1
        elif self.dir < 0:
            if self.x < self.min_x:
                self.x = self.min_x
                self.dir = 1
        self.x += self.x_speed * self.dir * dt



def new_panel(y):
    orange_Panel_chance = 0
    red_Panel_chance = 0

    x = random.randrange(0, DISPLAY_WIDTH - PANEL_WIDTH)

    if ORANGE_PANELS_ACTIVE:
        orange_Panel_chance = 0.3
    if RED_PANELS_ACTIVE:
        red_Panel_chance = 0.2

    pick_panel = random.randrange(0, 100)
    if pick_panel < orange_Panel_chance * 100:
        panel = Moving_Panel(x, y, PANEL_WIDTH, PANEL_HEIGHT)
        opanelgroup.add(panel)
    elif pick_panel < (orange_Panel_chance + red_Panel_chance) * 100:
        panel = Vanish_Panel(x, y, PANEL_WIDTH, PANEL_HEIGHT)
        rpanelgroup.add(panel)
    else:
        panel = Panel(x, y, PANEL_WIDTH, PANEL_HEIGHT)

    panelgroup.add(panel)

    return panel


def create_panels(start, fin, gap):
    panels = []

    gap += PANEL_HEIGHT

    for y in range(int(start - gap), fin, -int(gap)):
        panels.append(new_panel(y))

    return panels


def remove_panels(panel_list, panel):
    panel_list.remove(panel)
    panelgroup.remove(panel)
    if opanelgroup.has(panel): opanelgroup.remove(panel)
    if rpanelgroup.has(panel): rpanelgroup.remove(panel)

    return panel_list


# DISPLAY MESSAGE
def text_objects(text, font, colour):
    textSurface = font.render(text, True, colour)
    return textSurface, textSurface.get_rect()


def message_display(text, size, x, y, font, colour, centre=False):
    text_attr = pygame.font.Font(font, int(size * SCALING_X))  # DOUBLE CHECK SCALING
    textSurf, textRect = text_objects(text, text_attr, colour)
    if centre:
        textRect.center = (x, y)
    else:
        textRect.x = x
        textRect.y = y
    gameDisplay.blit(textSurf, textRect)


# BUTTONS
def button(msg, y, font, colour, hover_colour):
    global BUTTON_SELECTED, B_DOWN
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()
    border_w = int(2 * SCALING_X)
    x = BUTTON_X

    pygame.draw.rect(gameDisplay, black, [x, y, BUTTON_WIDTH, BUTTON_HEIGHT])
    if (x + BUTTON_WIDTH) > mouse[0] > x and (y + BUTTON_HEIGHT) > mouse[1] > y:
        pygame.draw.rect(gameDisplay, hover_colour, [x + border_w, y + border_w, BUTTON_WIDTH - border_w * 2, BUTTON_HEIGHT - border_w * 2])
        if not B_DOWN:
            if click[0] == 1 and not BUTTON_SELECTED:
                BUTTON_SELECTED = msg
                B_DOWN = True
        else:
            if click[0] == 0 and BUTTON_SELECTED == msg:
                BUTTON_SELECTED = None
                B_DOWN = False
                return True
    else:
        pygame.draw.rect(gameDisplay, colour, [x + border_w, y + border_w, BUTTON_WIDTH - border_w * 2, BUTTON_HEIGHT - border_w * 2])

    message_display(msg, 26, x + (BUTTON_WIDTH / 2), y + (BUTTON_HEIGHT / 2), font, black, True)
    return False

class Stars:
    num_stars = 200
    stars = [[0 for x in range(4)] for y in range(num_stars)]
    for num in range(0, num_stars):
        stars[num][0] = random.randrange(0, DISPLAY_WIDTH)  # x
        stars[num][1] = random.randrange(-DISPLAY_HEIGHT, DISPLAY_HEIGHT)  # y
        stars[num][2] = random.randrange(1, 5) * SCALING_Y / 20  # speed
        stars[num][3] = random.randrange(1, 4)  # size

    def render(self, dt):
        for star in self.stars:
            star[1] += star[2] * dt
            if star[1] > DISPLAY_HEIGHT:  # if stars fall off-screen, re-draw them above
                star[0] = random.randrange(0, DISPLAY_WIDTH)  # x
                star[1] = random.randrange(-DISPLAY_HEIGHT, -200)  # y
                star[2] = random.randrange(1, 5) * SCALING_Y / 20  # speed
            pygame.draw.circle(gameDisplay, bright_yellow, (star[0], int(star[1])), star[3])
            
            
            
            
# SAVE STATES WHEN APP GOES INTO BACKGROUND
def save_state(obj, url):
    pickle.dump(obj, open(url, 'wb'), -1)


def load_state(url):
    try:
        p_obj = pickle.load(open(url, 'rb'))
        return (p_obj)
    except:
        return None

def delete_state():
    if os.path.exists(p_astro):
        os.unlink(p_astro)
    if os.path.exists(p_stars):
        os.unlink(p_stars)
    if os.path.exists(p_panels):
        os.unlink(p_panels)


# MAIN MENU
def game_intro():
    SLEEPING = False
    main_astro = Astro()
    main_astro.x = int((DISPLAY_WIDTH - main_astro.width) / 2)
    main_astro.y = start_y = int(170 * SCALING_Y)
    main_astro.start_dy = main_astro.dy = 0.5 * SCALING_Y
    main_astro.grav = -0.08 / 100 * SCALING_Y

    bg_stars = Stars()
    play_soundtrack(intro_music, True)
    if(os.path.exists(p_astro)):
        main_astro.load_state()
        os.unlink(p_astro)
    if (os.path.exists(p_stars)):
        bg_stars.stars = load_state(p_stars)
        os.unlink(p_stars)
    try:
        pygame.mixer.music.unpause()
    except:
        pass


    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or event.type == pygame.APP_TERMINATING:
                delete_state()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    main_astro.save_state()
                    save_state(bg_stars.stars, p_stars)
                    pygame.mixer.music.pause()
                    print("game saved")
                    SLEEPING = True
                elif event.key == pygame.K_2:
                    main_astro.load_state()
                    bg_stars.stars = load_state(p_stars)
                    pygame.mixer.music.unpause()
                    SLEEPING = False
                    
            elif event.type == pygame.APP_WILLENTERBACKGROUND:
                # The app is about to go to sleep. It should save state, cancel
                # any timers, and stop drawing the screen until an APP_DIDENTERFOREGROUND
                # event shows up.
    
                    main_astro.save_state()
                    save_state(bg_stars.stars, p_stars)
                    pygame.mixer.music.pause()
                    SLEEPING = True
                
            elif event.type == pygame.APP_DIDENTERFOREGROUND:
                # The app woke back up. Delete the saved state (we don't need it),
                # restore any times, and start drawing the screen again.
                
                main_astro.load_state()
                bg_stars.stars = load_state(p_stars)
                pygame.mixer.music.unpause()
                os.unlink(p_astro)
                os.unlink(p_stars)
                SLEEPING = False
    
                # For now, we have to re-open the window when entering the
                # foreground.
                global gameDisplay
                gameDisplay = pygame.display.set_mode((DISPLAY_WIDTH + PADDING_X, DISPLAY_HEIGHT + PADDING_Y))
        if not SLEEPING:
            frameTime = gameClock.tick(60)
            print frameTime
            
            gameDisplay.fill(black)
            bg_stars.render(frameTime)
                
            message_display('A RoughCode Project', 15, 5, DISPLAY_HEIGHT - 20 * SCALING_Y, trajan, bright_green, False)    
            message_display('ASTROJUMP', 80, (DISPLAY_WIDTH / 2), start_y + Astro.height + 40 * SCALING_Y, trajan, neon_green, True)
    
            if button('Play', 420 * SCALING_Y, courbd, green, bright_green):
                game_loop()
            if button('Select Character', 520 * SCALING_Y, courbd, yellow, bright_yellow):
                    character_select(bg_stars)
            if button('Exit Game', 620 * SCALING_Y, courbd, red, bright_red):
                sys.exit()

            while (frameTime > 0):
                if frameTime >= DT:
                    dt = DT
                else:
                    dt = frameTime
                main_astro.jump(dt)
                if main_astro.y > start_y:
                    main_astro.reset_jump(start_y + main_astro.height)
                frameTime -= dt
            print gameClock.get_time()
            main_astro.render()
            pygame.display.update()

def character_select(bg_stars):
    SLEEPING = False  # MAKE GLOBAL
    global ASTRO_CHOSEN
                
    start_x = int (50 * SCALING_X)
    gap = (DISPLAY_WIDTH - start_x * 2 - Astro.width) / (NUM_ASTROS - 1)
    y = int(DISPLAY_HEIGHT * 0.4)
    
    sprites = [0 for num in range(NUM_ASTROS)]
    for i in range(NUM_ASTROS):
        sprites[i] = Astro()  # init sprites
        sprites[i].change_sprite(i)
        sprites[i].x = start_x + gap * i
        sprites[i].y = y
        sprites[i].start_dy = sprites[i].dy = 0.7 * SCALING_Y
        sprites[i].grav = -0.2 / 100 * SCALING_Y
    
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or event.type == pygame.APP_TERMINATING:
                sys.exit()
            elif event.type == pygame.APP_WILLENTERBACKGROUND:
                # The app is about to go to sleep. It should save state, cancel
                # any timers, and stop drawing the screen until an APP_DIDENTERFOREGROUND
                # event shows up.
                pygame.mixer.music.pause()
                SLEEPING = True
                
            elif event.type == pygame.APP_DIDENTERFOREGROUND:
                # The app woke back up. Delete the saved state (we don't need it),
                # restore any times, and start drawing the screen again.
                SLEEPING = False
    
                # For now, we have to re-open the window when entering the
                # foreground.
                global gameDisplay
                gameDisplay = pygame.display.set_mode((DISPLAY_WIDTH + PADDING_X, DISPLAY_HEIGHT + PADDING_Y))
                
        if not SLEEPING:
            gameDisplay.fill(black)
            frameTime = gameClock.tick()
            bg_stars.render(frameTime)
            
            mouse = pygame.mouse.get_pos()
            click = pygame.mouse.get_pressed()
                
            for num in range(0, len(sprites)):
                if y < mouse[1] < y + Astro.height:
                    if (start_x + gap * num) <= mouse[0] <= (start_x + gap * num + Astro.width):
                        if click[0] == 1 and ASTRO_CHOSEN != num:
                            sprites[num].start_dy = sprites[num].dy = 0.7 * SCALING_Y
                            sprites[num].grav = -0.2 / 100 * SCALING_Y
                            ASTRO_CHOSEN = num                            
            
            for num in range(0, len(sprites)):
                if num == ASTRO_CHOSEN:
                    while (frameTime > 0):
                        if frameTime >= DT: dt = DT
                        else: dt = frameTime
                        sprites[num].jump(dt)
                        if sprites[num].y > y: sprites[num].reset_jump(y + sprites[0].height)
                        frameTime -= dt
                else:
                    sprites[num].image = sprites[num].astro_down
                    sprites[num].y = y
                sprites[num].render()
            
            message_display('Character Select', 55, (DISPLAY_WIDTH / 2), int(DISPLAY_HEIGHT * 0.2), trajan,
                                        neon_green, True)
            if button('Confirm', int(DISPLAY_HEIGHT * 0.6), courbd, green, bright_green):
                game_intro()
            if button('Exit Game', int(DISPLAY_HEIGHT * 0.75), courbd, red, bright_red):
                sys.exit()
                
            pygame.display.update()
                



# PAUSE SCREEN
def pause(score):
    gameDisplay.blit(pause_screen_bg, (0, 0))
    message_display('Pause', 100, int(DISPLAY_WIDTH / 2 - 2 * SCALING_X), int(DISPLAY_HEIGHT * 0.20 + 2 * SCALING_Y), trajan, black, True)
    message_display('Pause', 100, int(DISPLAY_WIDTH / 2), int(DISPLAY_HEIGHT * 0.20), trajan, dark_green, True)
    message_display(('Score: ' + str(score)), 60, int(DISPLAY_WIDTH / 2 - 3 * SCALING_X),
                    int(DISPLAY_HEIGHT * 0.35 + 3 * SCALING_Y), gills, black, True)
    message_display(('Score: ' + str(score)), 60, int(DISPLAY_WIDTH / 2),
                    int(DISPLAY_HEIGHT * 0.35), gills, neon_green, True)
    pygame.mixer.music.pause()

    while GAME_PAUSED:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or event.type == pygame.APP_TERMINATING:
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE or event.key == pygame.K_AC_BACK:
                    resume()

        if button('Resume', DISPLAY_HEIGHT * 0.5, courbd, green, bright_green):
            resume()
        if button('Restart', DISPLAY_HEIGHT * 0.6, courbd, yellow, bright_yellow):
            game_loop()
        if button('Main Menu', DISPLAY_HEIGHT * 0.7, courbd, blue, bright_blue):
            game_intro()
        if button('Exit Game', DISPLAY_HEIGHT * 0.8, courbd, red, bright_red):
            sys.exit()

        pygame.display.update()
        gameClock.tick()


def resume():
    global GAME_PAUSED
    GAME_PAUSED = False
    pygame.mixer.music.unpause()

# GAME OVER
def dead(score, new_hs=False):
    pygame.mixer.music.stop()
    dead_fx.play()
    gameDisplay.blit(dead_screen_bg, (0, 0))
    message_display('GAME OVER', 80, (DISPLAY_WIDTH / 2), int(DISPLAY_HEIGHT * 0.3), trajan, black, True)
    message_display(('Score: ' + str(score)), 70, (DISPLAY_WIDTH / 2),
                    int(DISPLAY_HEIGHT * 0.45), gills, black, True)
    if new_hs:  # new highscore
        message_display('New High Score!!', 40, (DISPLAY_WIDTH / 2), int(DISPLAY_HEIGHT * 0.56), trajan, black, True)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or event.type == pygame.APP_TERMINATING:
                sys.exit()

        if button('Restart', int(DISPLAY_HEIGHT * 0.63), courbd, yellow, bright_yellow):
            game_loop()
        if button('Main Menu', int(DISPLAY_HEIGHT * 0.73), courbd, blue, bright_blue):
            game_intro()
        if button('Exit Game', int(DISPLAY_HEIGHT * 0.83), courbd, red, bright_red):
            sys.exit()

        pygame.display.update()
        gameClock.tick()

class HighScore():
    y = 0
    on_screen = False
    
    def __init__(self):
        with open(folder_dir + 'highscore.txt', 'a+', 1) as hs:
            hs.seek(0)
            
            try:
                self.highscore = int(hs.read())
            except:
                self.highscore = 0
        
    def get_highscore(self):
        return(self.highscore)
    
    def check_highscore(self, score):
        if score > self.highscore:
            with open(folder_dir + 'highscore.txt', 'w') as hs:
                hs.write(str(score))
            return True
        else:
            return False
        
    def move_down(self, dist):
        self.y += dist
        if self.y > DISPLAY_HEIGHT:
            self.on_screen = False
    
    def create_line(self, y):
        if not self.on_screen:
            self.on_screen = True
            self.y = y
    
    def render(self, score):
        if self.on_screen:
            # message_display('High Score', 50 * SCALING_X , int(DISPLAY_WIDTH / 2), self.y - 30 * SCALING_Y, magneto_bold, bright_yellow, True)
            pygame.draw.rect(gameDisplay, bright_yellow, (0, self.y, DISPLAY_WIDTH, 2 * SCALING_Y))


# MAIN GAME LOOP
def game_loop():
    if android:
        pygame.joystick.init()
        for i in range (pygame.joystick.get_count()):
            joystick = pygame.joystick.Joystick(i)
            joystick.init()
            if joystick.get_name() == 'Android Accelerometer':
                break
    
    # FUNCTION CONSTANTS
    SLEEPING = False
    score = 0
    panel_gap = difficulty[0][1] * SCALING_Y
    global RED_PANELS_ACTIVE
    global ORANGE_PANELS_ACTIVE
    RED_PANELS_ACTIVE = False
    ORANGE_PANELS_ACTIVE = False
    bg = [((179, 60, 0), 5000), ((179, 230, 255), 10000), ((0, 0, 0), None)]
    bg_num = 0
    alpha = 1
    JOYSTICK_SENSITIVITY = 3.5  # HIGHER = MORE SENSITIVE

    # initialize sprites
    bg_stars = None
    playergroup.empty()
    panelgroup.empty()

    player = Astro()
    playergroup.add(player)

    panels = [
        Panel(player.x + player.width / 2 - PANEL_WIDTH / 2, player.start_y + player.height, PANEL_WIDTH,
              PANEL_HEIGHT)]
    panelgroup.add(panels[0])
    prev_panel = panels[0]
    panels += create_panels(player.start_y + player.height, 0, panel_gap)
    remove_panels_list = []
    
    highscore = HighScore()
    if highscore.get_highscore() < DISPLAY_HEIGHT and highscore.get_highscore() != 0 and not highscore.on_screen:
        highscore.create_line(panels[0].y - highscore.get_highscore())
    
    
    play_soundtrack(soundtrack[0], True)

    while True:
        global gameDisplay
        gameDisplay.fill(black)
        if android:
            if joystick:
                j_pos = joystick.get_axis(0)
                 
                if j_pos < -0.1:  # left
                    player.setDir(j_pos * JOYSTICK_SENSITIVITY)
                elif j_pos > 0.1:  # right
                    player.setDir(j_pos * JOYSTICK_SENSITIVITY)
                else:
                    player.setDir(0)
            
        for event in pygame.event.get():
            if event.type == pygame.QUIT or event.type == pygame.APP_TERMINATING:
                pygame.joystick.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    player.setDir(-1)
                elif event.key == pygame.K_RIGHT:
                    player.setDir(1)
                elif event.key == pygame.K_ESCAPE or event.key == pygame.K_AC_BACK:
                    global GAME_PAUSED
                    GAME_PAUSED = True
                    pause(score)
#                 elif event.key == pygame.K_1:
#                     power_up('jump')
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                    player.setDir(0)
            elif event.type == pygame.APP_WILLENTERBACKGROUND:
                # The app is about to go to sleep. It should save state, cancel
                # any timers, and stop drawing the screen until an APP_DIDENTERFOREGROUND
                # event shows up.
                    pygame.mixer.music.pause()
                    SLEEPING = True
            elif event.type == pygame.APP_DIDENTERFOREGROUND:
                # The app woke back up. Delete the saved state (we don't need it),
                # restore any times, and start drawing the screen again.
                SLEEPING = False
    
                # For now, we have to re-open the window when entering the
                # foreground.
                gameDisplay = pygame.display.set_mode((DISPLAY_WIDTH + PADDING_X, DISPLAY_HEIGHT + PADDING_Y))
                game_intro()

        if not SLEEPING:
            # GAME FPS           
            frameTime = gameClock.tick()
            
            # PAINT DISPLAY   
            if bg_num < len (bg) - 1:
                gameDisplay.fill(bg[bg_num][0])
                if alpha >= 1:
                    if score > bg[bg_num][1]:
                        bg_num += 1
                        alpha = 0
            else:
                gameDisplay.fill(black)
                if not bg_stars:
                    bg_stars = Stars()
                else:
                    bg_stars.render(frameTime)
            
            # TRANSITIONAL FADE BETWEEN BACKGROUNDS
            if alpha < 1:
                bg_vars = fade_bg(bg[bg_num - 1][0], bg[bg_num][0], alpha)
                bg1 = bg_vars[0]
                alpha = bg_vars[1]
                gameDisplay.fill(bg1)
                
            while frameTime > 0:
                if frameTime >= DT: dt = DT
                else: dt = frameTime
                if not panels[0].move_finished:
                    for p in panels:
                        p.move_down(dt)
                    for p in panels:
                        if p.y > DISPLAY_HEIGHT:  # if off-screen
                            panels = remove_panels(panels, p)
                            if p in remove_panels_list:
                                remove_panels_list.remove(p)  # remove unused obj from list
                    # generate more panels
                    if panels[len(panels) - 2].y > 0:
                        new_panels = create_panels(panels[len(panels) - 1].y, -DISPLAY_HEIGHT, panel_gap)
                        h_diff = panels[0].ttl_dist
                        for p in new_panels:
                                    p.is_moving(h_diff)  # moves the newly-created panels
                        panels += new_panels
                    
                    if highscore.on_screen:
                        highscore.move_down(SCROLL_SPEED)  # shift high score line
                    else:
                        if DISPLAY_HEIGHT > highscore.get_highscore() - score > 0:
                            highscore.create_line(-(DISPLAY_HEIGHT - (player.start_y + player.height)))
                            
                player.jump(dt)
                
                if player.isDescending:  # if player is descending
                    for panel in panels:
                        if player.collide(panel):
                            player.reset_jump(panel.y)
                            if panel.y < prev_panel.y:  # if landed on higher panel
                                height_diff = prev_panel.y - panel.y
                                for p in panels:
                                    p.is_moving(height_diff)
                                score += int(height_diff)
                                prev_panel = panel
                            if isinstance(panel, Vanish_Panel):  # removes red panels
                                remove_panels_list.append(panel)  # prevents messing up list order
                                panelgroup.remove(panel)
                                rpanelgroup.remove(panel)
                for panel in opanelgroup.sprites():
                    panel.move_hor(dt)  # moves orange panels
                # UPDATE SPRITES
                playergroup.update()
                panelgroup.update()
                
                frameTime -= dt
            
            
            # checks death
            if player.y > DISPLAY_HEIGHT:
                dead(score, highscore.check_highscore(score))
    
            # update difficulty
            for x in range(0, len(difficulty)):
                level = difficulty[x][0]
                value = difficulty[x][1]
    
                if level < score:
                    if isinstance(value, int):
                        panel_gap = int(value * SCALING_Y)
                    else:
                        if value == 'red':
                            RED_PANELS_ACTIVE = True
                        elif value == 'orange':
                            ORANGE_PANELS_ACTIVE = True
                        else:
                            print("Error activating panels")
                            
                # update soundtrack
                track_no = int(score / 5000)
                if track_no < len(soundtrack):  # prevents error
                    track = soundtrack[track_no]
                    if current_track != track:
                        play_soundtrack(track, True)
            
            
    #         # POWER UP
    #         if has_power_up:
    #             player.jump_inc()
    #             global power_timer
    #             if (pygame.time.get_ticks() - power_timer) > 5000:
    #                 player.reset_abilities()
    #                 power_up(None)                       
                    
            if highscore.on_screen:highscore.render(score)

            # DRAW SPRITES
            panelgroup.draw(gameDisplay)
            playergroup.draw(gameDisplay)
            
            message_display(('Score: ' + str(score)), 30, int(10 * SCALING_X), int(10 * SCALING_Y), courbd, white)
    
    
            if android:                
                if PADDING_X != 0: 
                    pygame.draw.rect(gameDisplay, black, (DISPLAY_WIDTH, 0, PADDING_X, DISPLAY_HEIGHT))   
                if PADDING_Y != 0:
                    pygame.draw.rect(gameDisplay, black, (0, DISPLAY_HEIGHT, DISPLAY_WIDTH, PADDING_Y))
            
#             print gameClock.get_fps()
            pygame.display.update()

# INITIALIZE PROGRAM
if __name__ == "__main__":
    game_intro()
