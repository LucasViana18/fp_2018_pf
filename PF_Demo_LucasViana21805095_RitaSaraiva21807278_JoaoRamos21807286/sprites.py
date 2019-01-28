import pygame as pg
from settings import *
from tilemap import collide_hit_rect
vec = pg.math.Vector2

def collide_wall(sprite, group, direction):
    # Função para colisão do player com as paredes
    if direction == 'x':
        hits = pg.sprite.spritecollide(sprite, group, False, collide_hit_rect)
        if hits:
            if hits[0].rect.centerx > sprite.hit_rect.centerx:
                sprite.pos.x = hits[0].rect.left - sprite.hit_rect.width / 2
            if hits[0].rect.centerx < sprite.hit_rect.centerx:
                sprite.pos.x = hits[0].rect.right + sprite.hit_rect.width / 2
            sprite.vel.x = 0
            sprite.hit_rect.centerx = sprite.pos.x
    if direction == 'y':
        hits = pg.sprite.spritecollide(sprite, group, False, collide_hit_rect)
        if hits:
            if hits[0].rect.centery > sprite.hit_rect.centery:
                sprite.pos.y = hits[0].rect.top - sprite.hit_rect.height / 2
            if hits[0].rect.centery < sprite.hit_rect.centery:
                sprite.pos.y = hits[0].rect.bottom + sprite.hit_rect.height / 2
            sprite.vel.y = 0
            sprite.hit_rect.centery = sprite.pos.y

class Spritesheet:
    # Classe especial para retirar imagens de spritesheets
    def __init__(self, filename):
        self.spritesheet = pg.image.load(filename).convert_alpha()

    def get_image(self, x, y, width, height):
        image = pg.Surface((width, height))
        image.blit(self.spritesheet, (0, 0), (x, y, width, height))
        image = pg.transform.scale(image, ((width // 3) + 20, (height // 3) + 20))
        return image

class Player(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.walking_x = False
        self.walking_y = False
        self.left = False
        self.right = False
        self.up = False
        self.down = False
        self.current_frame = 0
        self.last_update = 0
        self.load_images()
        self.image = self.stand_down
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.hit_rect = PLAYER_HIT_RECT
        self.hit_rect.center = self.rect.center
        self.vel = vec(0, 0)
        self.pos = vec(x, y)
        self.last_shot = 0
        self.last_dash = 0
        self.health = 100

    def load_images(self):
        self.stand_down = self.game.spritesheet_player.get_image(0, 0, 256, 256)
        self.stand_down.set_colorkey(BLACK)
#-----------------------------------------------------------------------
        self.stand_up = self.game.spritesheet_player.get_image(0, 256, 256, 256)
        self.stand_up.set_colorkey(BLACK)
#-------------------------------------------------------------------------
        self.stand_left = self.game.spritesheet_player.get_image(256, 512, 256, 256)
        self.stand_left.set_colorkey(BLACK)
#--------------------------------------------------------------------------
        self.stand_right = self.game.spritesheet_player.get_image(256, 768, 256, 256)
        self.stand_right.set_colorkey(BLACK)
#---------------------------------------------------------------------------
        self.walk_right = [self.game.spritesheet_player.get_image(0, 768, 256, 256),
                           self.game.spritesheet_player.get_image(512, 768, 256, 256)]
        self.walk_left = []
        for frame in self.walk_right:
            frame.set_colorkey(BLACK)
            self.walk_left.append(pg.transform.flip(frame, True, False))
#----------------------------------------------------------------------------
        self.walk_up = [self.game.spritesheet_player.get_image(256, 256, 256, 256),
                        self.game.spritesheet_player.get_image(768, 256, 256, 256)]
        for frame in self.walk_up:
            frame.set_colorkey(BLACK)
#-----------------------------------------------------------------------------
        self.walk_down = [self.game.spritesheet_player.get_image(256, 0, 256, 256),
                          self.game.spritesheet_player.get_image(768, 0, 256, 256)]
        for frame in self.walk_down:
            frame.set_colorkey(BLACK)

    def keys(self):
        self.vel = vec(0, 0)
        keys = pg.key.get_pressed()
        if keys[pg.K_LEFT]:
            self.vel.x = -PLAYER_SPEED
            self.left = True
            self.right = False
            self.up = False
            self.down = False
        elif keys[pg.K_RIGHT]:
            self.vel.x = PLAYER_SPEED
            self.left = False
            self.right = True
            self.up = False
            self.down = False
        elif keys[pg.K_DOWN]:
            self.vel.y = PLAYER_SPEED
            self.left = False
            self.right = False
            self.up = False
            self.down = True
        elif keys[pg.K_UP]:
            self.vel.y = -PLAYER_SPEED
            self.left = False
            self.right = False
            self.up = True
            self.down = False

        if keys[pg.K_SPACE]:
            now = pg.time.get_ticks()
            if self.game.weapon:
                if now - self.last_shot > BULLET_RATE:
                    if self.right:
                        self.last_shot = now
                        direction = vec(1, 0)
                        Bullet(self.game, self.pos, direction)
                    if self.left:
                        self.last_shot = now
                        direction = vec(-1, 0)
                        Bullet(self.game, self.pos, direction)
                    if self.up:
                        self.last_shot = now
                        direction = vec(0, -1)
                        Bullet(self.game, self.pos, direction)
                    if self.down:
                        self.last_shot = now
                        direction = vec(0, 1)
                        Bullet(self.game, self.pos, direction)

        if keys[pg.K_LCTRL]:
            now = pg.time.get_ticks()
            if now - self.last_dash > DASH_COOLDOWN:
                if self.right:
                    self.last_dash = now
                    direction = vec(1, 0)
                    Dash(self.game, self.pos, direction)
                if self.left:
                    self.last_dash = now
                    direction = vec(-1, 0)
                    Dash(self.game, self.pos, direction)
                if self.up:
                    self.last_dash = now
                    direction = vec(0, -1)
                    Dash(self.game, self.pos, direction)
                if self.down:
                    self.last_dash = now
                    direction = vec(0, 1)
                    Dash(self.game, self.pos, direction)

        if keys[pg.K_LSHIFT]:
            if self.right:
                self.vel.x = PLAYER_SPEED + 100
            if self.left:
                self.vel.x = -PLAYER_SPEED - 100
            if self.up:
                self.vel.y = -PLAYER_SPEED - 100
            if self.down:
                self.vel.y = PLAYER_SPEED + 100

    def update(self):
        self.animate()
        self.keys()
        self.rect = self.image.get_rect()
        self.rect.center = self.pos
        self.pos += self.vel * self.game.dt
        self.hit_rect.centerx = self.pos.x
        collide_wall(self, self.game.walls, 'x')
        self.hit_rect.centery = self.pos.y
        collide_wall(self, self.game.walls, 'y')
        self.rect.center = self.hit_rect.center

    def animate(self):
        if not self.walking_x and not self.walking_y:
            if self.down:
                self.image = self.stand_down
            if self.up:
                self.image = self.stand_up
            if self.right:
                self.image = self.stand_right
            if self.left:
                self.image = self.stand_left

        now = pg.time.get_ticks()

        if self.vel.x != 0:
            self.walking_x = True
        else:
            self.walking_x = False

        if self.walking_x:
            if now - self.last_update > 200:
                self.last_update = now
                self.current_frame = (self.current_frame + 1) % len(self.walk_left)
                if self.vel.x > 0:
                    self.image = self.walk_right[self.current_frame]
                else:
                    self.image = self.walk_left[self.current_frame]

        if self.vel.y != 0:
            self.walking_y = True
        else:
            self.walking_y = False

        if self.walking_y:
            if now - self.last_update > 200:
                self.last_update = now
                self.current_frame = (self.current_frame + 1) % len(self.walk_up)
                if self.vel.y > 0:
                    self.image = self.walk_down[self.current_frame]
                else:
                    self.image = self.walk_up[self.current_frame]

class Bullet(pg.sprite.Sprite):
    def __init__(self, game, pos, direction):
        self.groups = game.all_sprites, game.bullets
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = game.bullet_img
        self.rect = self.image.get_rect()
        self.pos = vec(pos)
        self.rect.center = pos
        self.vel = direction * BULLET_SPEED
        self.spawn_time = pg.time.get_ticks()

    def update(self):
        self.pos += self.vel * self.game.dt
        self.rect.center = self.pos
        if pg.sprite.spritecollideany(self, self.game.walls):
            self.kill()
        now = pg.time.get_ticks()
        if now - self.spawn_time > BULLET_LIFETIME:
            self.kill()

class Dash(pg.sprite.Sprite):
    def __init__(self, game, pos, direction):
        self.groups = game.all_sprites, game.dashs
        pg.sprite.Sprite.__init__(self, self.groups)
        self.image = game.dash_img
        self.rect = self.image.get_rect()
        self.game = game
        self.pos = pos
        self.rect.center = pos
        self.vel = direction * DASH_SPEED
        self.distance_time = pg.time.get_ticks()

    def update(self):
        self.pos += self.vel * self.game.dt
        now = pg.time.get_ticks()
        if now - self.distance_time > DASH_DISTANCE:
            self.kill()

class Mob(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites, game.mobs
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = self.game.spritesheet_mob.get_image(0, 0, 128, 128)
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.pos = vec(x, y)
        self.rect.center = (x, y)
        self.hit_rect = MOB_HIT_RECT.copy()
        self.hit_rect.center = self.rect.center
        self.health = MOB_HEALTH
        self.counter = 0

    def move(self):
        distance = 40
        speed = 8

        if self.counter >= 0 and self.counter <= distance:
            self.image = self.game.spritesheet_mob.get_image(32, 192, 32, 32)
            self.image.set_colorkey(BLACK)
            self.image = pg.transform.scale(self.image, (64, 64))
            self.pos.x += speed
        elif self.counter >= distance and self.counter <= distance * 2:
            self.image = self.game.spritesheet_mob.get_image(32, 128, 32, 32)
            self.image.set_colorkey(BLACK)
            self.image = pg.transform.scale(self.image, (64, 64))
            self.pos.y += speed
        elif self.counter >= distance * 2 and self.counter <= distance * 3:
            self.image = self.game.spritesheet_mob.get_image(32, 160, 32, 32)
            self.image.set_colorkey(BLACK)
            self.image = pg.transform.scale(self.image, (64, 64))
            self.pos.x -= speed
        elif self.counter >= distance * 3 and self.counter <= distance * 4:
            self.image = self.game.spritesheet_mob.get_image(32, 224, 32, 32)
            self.image.set_colorkey(BLACK)
            self.image = pg.transform.scale(self.image, (64, 64))
            self.pos.y -= speed
        else:
            self.counter = 0

        self.counter += 1

    def update(self):
        self.move()
        self.rect = self.image.get_rect()
        self.rect.center = self.pos
        if self.health <= 0:
            self.kill()

class Item(pg.sprite.Sprite):
    def __init__(self, game, pos, type):
        self.groups = game.all_sprites, game.items
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = game.item_images[type]
        self.rect = self.image.get_rect()
        self.type = type
        self.rect.center = pos

class Exit(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites, game.exits
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = game.exit_img
        self.rect = self.image.get_rect()
        self.pos = vec(x, y)
        self.rect.center = self.pos

class Obstacle(pg.sprite.Sprite):
    def __init__(self, game, x, y, w, h):
        self.groups = game.walls
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.rect = pg.Rect(x, y, w, h)
        self.x = x
        self.y = y
        self.rect.x = x
        self.rect.y = y
