import pygame
import sys
import math

class SpriteSheet:
    def __init__(self, filename: str):
        """Load a spritesheet PNG"""
        self.sheet = pygame.image.load(filename).convert_alpha()
        
    def get_sprite(self, x: int, y: int, width: int, height: int) -> Surface:
        """Extract a single sprite from the sheet"""
        sprite = pygame.Surface((width, height), pygame.SRCALPHA)
        sprite.blit(self.sheet, (0, 0), (x, y, width, height))
        return sprite

    def get_sprites_row(self, row: int, sprite_width: int, sprite_height: int, count: int):
        """Get multiple sprites from a single row"""
        sprites = []
        for i in range(count):
            x = i * sprite_width
            y = row * sprite_height
            sprites.append(self.get_sprite(x, y, sprite_width, sprite_height))
        return sprites
        
        
        