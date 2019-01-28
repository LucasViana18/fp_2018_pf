import pygame as pg

# colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
DARKGREY = (40, 40, 40)
LIGHTGREY = (100, 100, 100)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
BLUE = (0, 0, 255)

# settings
WIDTH = 1280
HEIGHT = 720
FPS = 60

TILESIZE = 64
GRIDWIDTH = WIDTH / TILESIZE
GRIDHEIGHT = HEIGHT / TILESIZE

# Player
PLAYER_SPEED = 250
PLAYER_HIT_RECT = pg.Rect(0, 0, 35, 85)
PLAYER_SPRITESHEET = "Hero.png"

# Weapon
BULLET_IMG = 'bullet.png'
BULLET_SPEED = 500
BULLET_LIFETIME = 300
BULLET_RATE = 300
BULLET_DAMAGE = 100

# Dash
DASH_IMG = 'dash.png'
DASH_SPEED = 450
DASH_DISTANCE = 400
DASH_COOLDOWN = 1700

# Mob
MOB_SPRITESHEET = 'animals.png'
MOB_HIT_RECT = pg.Rect(0, 0, 15, 65)
MOB_DAMAGE = 100
MOB_KNOCKBACK = 20
MOB_HEALTH = 100

# Items
ITEM_IMAGES = {'weapon': 'bullet.png',
               'key': 'goldenkey_1.png'}

# Exit
EXIT_IMG = 'end.png'

# Sounds
BG_MUSIC = 'September.wav'

