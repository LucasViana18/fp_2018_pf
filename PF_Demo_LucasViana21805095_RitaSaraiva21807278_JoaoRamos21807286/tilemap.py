# Definicoes do mapa e da camera

import pygame as pg
from settings import *
import pytmx

def collide_hit_rect(one, two):
    # Função que permite o uso de colisão do hitbox do player contra a parede 
    return one.hit_rect.colliderect(two.rect)

class TiledMap:
    # Classe do mapa feito no software Tiled
    def __init__(self, filename):
        tm = pytmx.load_pygame(filename, pixelalpha=True)
        self.width = tm.width * tm.tilewidth
        self.height = tm.height * tm.tileheight
        self.tmxdata = tm

    def render(self, surface):
        ti = self.tmxdata.get_tile_image_by_gid
        for layer in self.tmxdata.visible_layers:
            if isinstance(layer, pytmx.TiledTileLayer):
                for x, y, gid, in layer:
                    tile = ti(gid)
                    if tile:
                        surface.blit(tile, (x * self.tmxdata.tilewidth, y * self.tmxdata.tileheight))

    def make_map(self):
        temp_surface = pg.Surface((self.width, self.height))
        self.render(temp_surface)
        return temp_surface

class Camera:
    def __init__(self, width, height):
        self.camera = pg.Rect(0, 0, width, height)
        self.width = width
        self.height = height

    def apply(self, entity):
        # Aplica um retangulo à uma sprite
        return entity.rect.move(self.camera.topleft)

    def apply_rect(self, rect):
        # Aplica um retangulo ao mapa
        return rect.move(self.camera.topleft)

    def update(self, target):
        # Movimento da camera
        x = -target.rect.centerx + int(WIDTH / 2)
        y = -target.rect.centery + int(HEIGHT / 2)

        # margens do mapa
        x = min(0, x) 
        y = min(0, y) 
        x = max(-(self.width - WIDTH), x) 
        y = max(-(self.height - HEIGHT), y) 
        self.camera = pg.Rect(x, y, self.width, self.height)
