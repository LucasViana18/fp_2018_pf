# Pygame Tile-based game
# Trabalho Realizado por: João Ramos a21807286; Lucas Viana a21805095; Rita Saraiva a21807278

import pygame as pg
import sys
from os import path
from settings import *
from sprites import *
from tilemap import *

class Game:
    def __init__(self):
        pg.mixer.pre_init(44100, -16, 1, 2048)
        pg.init()
        pg.mixer.init()
        self.screen = pg.display.set_mode((WIDTH, HEIGHT))
        self.clock = pg.time.Clock()
        pg.key.set_repeat(500, 100)
        self.load_data()
        self.key = False
        self.weapon = False

    def load_data(self):
        # Carregamento de imagens, sons e mapa
        game_folder = path.dirname(__file__)
        map_folder = path.join(game_folder, 'maps')
        img_folder = path.join(game_folder, 'img')
        snd_folder = path.join(game_folder, 'snd')
        self.spritesheet_player = Spritesheet(path.join(img_folder, PLAYER_SPRITESHEET))
        self.spritesheet_mob = Spritesheet(path.join(img_folder, MOB_SPRITESHEET))
        self.map = TiledMap(path.join(map_folder, 'tiled1.tmx'))
        self.map_img = self.map.make_map()
        self.map_rect = self.map_img.get_rect()
        self.bullet_img = pg.image.load(path.join(img_folder, BULLET_IMG)).convert_alpha()
        self.dash_img = pg.image.load(path.join(img_folder, DASH_IMG)).convert_alpha()
        self.exit_img = pg.image.load(path.join(img_folder, EXIT_IMG)).convert_alpha()
        self.item_images = {}
        for item in ITEM_IMAGES:
            self.item_images[item] = pg.image.load(path.join(img_folder, ITEM_IMAGES[item])).convert_alpha()

        pg.mixer.music.load(path.join(snd_folder, BG_MUSIC))
        pg.mixer.music.set_volume(0.1)

    def draw_text(self, text, font_name, size, color, x, y, align="nw"):
        # Uma função predefinida para facilitar a inserção de texto no jogo
        font = pg.font.SysFont(font_name, size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        if align == "nw":
            text_rect.topleft = (x, y)
        if align == "ne":
            text_rect.topright = (x, y)
        if align == "sw":
            text_rect.bottomleft = (x, y)
        if align == "se":
            text_rect.bottomright = (x, y)
        if align == "n":
            text_rect.midtop = (x, y)
        if align == "s":
            text_rect.midbottom = (x, y)
        if align == "e":
            text_rect.midright = (x, y)
        if align == "w":
            text_rect.midleft = (x, y)
        if align == "center":
            text_rect.center = (x, y)
        self.screen.blit(text_surface, text_rect)

    def new(self):
        # Um novo começo do jogo
        self.all_sprites = pg.sprite.Group()
        self.walls = pg.sprite.Group()
        self.bullets = pg.sprite.Group()
        self.dashs = pg.sprite.Group()
        self.items = pg.sprite.Group()
        self.mobs = pg.sprite.Group()
        self.exits = pg.sprite.Group()
        for tile_object in self.map.tmxdata.objects:
            id_center = vec(tile_object.x + tile_object.width / 2,
                         tile_object.y + tile_object.height / 2)
            if tile_object.name == 'player':
                self.player = Player(self, id_center.x, id_center.y)
            if tile_object.name == 'wall':
                Obstacle(self, tile_object.x, tile_object.y, tile_object.width, tile_object.height)
            if tile_object.name == 'mob':
                Mob(self, id_center.x, id_center.y)
            if tile_object.name in ['weapon']:
                Item(self, id_center, tile_object.name)
            if tile_object.name in ['key']:
                Item(self, id_center, tile_object.name)
            if tile_object.name == 'exit':
                Exit(self, id_center.x, id_center.y)

        self.camera = Camera(self.map.width, self.map.height)
        self.controls = False

    def run(self):
        # Loop do jogo
        self.playing = True
        pg.mixer.music.play(loops=-1)
        while self.playing:
            self.dt = self.clock.tick(FPS) / 1000
            self.events()
            self.update()
            self.draw()

    def quit(self):
        pg.quit()
        sys.exit()

    def update(self):
        self.all_sprites.update()
        self.camera.update(self.player)
        # Player vs Items
        hits = pg.sprite.spritecollide(self.player, self.items, True)
        for hit in hits:
            if hit.type == 'key':
                self.key = True
                hit.kill()
            if hit.type == 'weapon':
                self.weapon = True
                hit.kill()

        #Bullets vs Mobs
        hits = pg.sprite.groupcollide(self.mobs, self.bullets, False, True)
        for hit in hits:
            hit.health -= BULLET_DAMAGE

        # Mobs vs Player
        hits = pg.sprite.spritecollide(self.player, self.mobs, False, collide_hit_rect)
        for hit in hits:
            self.player.health -= MOB_DAMAGE
            hit.vel = vec(0, 0)
            self.game_over()
            self.ok()
            self.new()

        # Player vs Exit
        hits = pg.sprite.spritecollide(self.player, self.exits, False)
        for hit in hits:
            if self.key:
                self.victory()
                self.ok()
                self.key = False
                self.new()

    def draw_grid(self):
        for x in range(0, WIDTH, TILESIZE):
            pg.draw.line(self.screen, LIGHTGREY, (x, 0), (x, HEIGHT))
        for y in range(0, HEIGHT, TILESIZE):
            pg.draw.line(self.screen, LIGHTGREY, (0, y), (WIDTH, y))

    def draw(self):
        pg.display.set_caption("Demo FPS: {:.2f}".format(self.clock.get_fps()))
        self.screen.blit(self.map_img, self.camera.apply_rect(self.map_rect))
        #self.draw_grid()
        for sprite in self.all_sprites:
            self.screen.blit(sprite.image, self.camera.apply(sprite))
        #pg.draw.rect(self.screen, WHITE, self.player.hit_rect, 2)
        if self.controls:
            self.draw_text("Controles:", 'arial', 30, BLACK, 5, 15, align="w")
            self.draw_text("Setas -> Movimento", 'arial', 30, BLACK, 5, 50, align="w")
            self.draw_text("SHIFT-> Sprint", 'arial', 30, BLACK, 5, 90, align="w")
            self.draw_text("CTRL-> Dash", 'arial', 30, BLACK, 5, 130, align="w")
            self.draw_text("Espaço-> Disparar", 'arial', 30, BLACK, 5, 170, align="w")
        self.draw_text("Pressione <H> para controles.", 'arial', 30, BLACK, 10, HEIGHT + 5, align="sw")
        pg.display.flip()

    def events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.quit()
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    self.quit()
                if event.key == pg.K_h:
                    self.controls = not self.controls

    def victory(self):
        self.screen.fill(BLUE)
        self.draw_text("GOOD JOB!", 'arial', 100, YELLOW, WIDTH / 2, HEIGHT / 2, align="center")
        pg.display.flip()
        self.ok()

    def game_over(self):
        self.screen.fill(BLACK)
        self.draw_text("DEAD", 'arial', 100, RED, WIDTH / 2, HEIGHT / 2, align="center")
        pg.display.flip()
        self.ok()

    def ok(self):
        a = True
        while a:
            self.clock.tick(FPS)
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    a = False
                    self.quit()
                if event.type == pg.KEYUP:
                    a = False

g = Game()
while True:
    g.new()
    g.run()
    g.game_over()
