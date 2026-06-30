"""Level maps and tile rendering for Isometric RPG"""

import pygame
import math

ISO_TILE_W = 64
ISO_TILE_H = 32

GRASS_COLORS = [
    (80, 140, 70),
    (85, 145, 72),
    (75, 135, 65),
    (90, 150, 75),
]
DIRT_COLOR  = (140, 110, 70)
WATER_COLOR = (60, 120, 200)
STONE_COLOR = (130, 130, 140)

WORLD_MAP = [
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,0,3,3,0,0,0,0,0,3,3,0,0,0,1],
    [1,0,3,3,3,3,0,0,0,3,3,3,3,0,0,1],
    [1,0,0,3,3,0,0,0,0,0,3,3,0,0,0,1],
    [1,0,0,0,0,0,0,2,0,0,0,0,0,0,0,1],
    [1,0,0,0,0,0,2,2,2,0,0,0,0,0,0,1],
    [1,0,0,0,0,0,0,2,0,0,0,0,0,0,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,0,4,4,4,0,0,0,0,0,0,0,0,0,1],
    [1,0,0,4,4,4,0,0,0,0,0,0,0,0,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
]
# 0=grass, 1=wall/stone, 2=water, 3=tree, 4=dirt

MAP_H = len(WORLD_MAP)
MAP_W = len(WORLD_MAP[0])

def cart_to_iso(cx, cy):
    """Convert cartesian grid coords to isometric screen coords."""
    sx = (cx - cy) * (ISO_TILE_W // 2)
    sy = (cx + cy) * (ISO_TILE_H // 2)
    return sx, sy

def is_walkable(gx, gy):
    """Check if a grid position is walkable."""
    gxi, gyi = int(gx), int(gy)
    if gxi < 0 or gyi < 0 or gxi >= MAP_W or gyi >= MAP_H:
        return False
    t = WORLD_MAP[gyi][gxi]
    return t not in (1, 2, 3)

def draw_iso_tile(surf, gx, gy, tile_type, offset_x, offset_y):
    """Draw a single isometric tile."""
    sx, sy = cart_to_iso(gx, gy)
    sx += offset_x
    sy += offset_y

    hw = ISO_TILE_W // 2
    hh = ISO_TILE_H // 2

    if tile_type == 1:   # wall
        color_top  = STONE_COLOR
        color_left = (100, 100, 110)
        color_right= (80,  80,  90)
        wall_h = 24
        # Front face left
        pygame.draw.polygon(surf, color_left, [
            (sx,      sy + hh),
            (sx - hw, sy + hh + hh),
            (sx - hw, sy + hh + hh + wall_h),
            (sx,      sy + hh + wall_h),
        ])
        # Front face right
        pygame.draw.polygon(surf, color_right, [
            (sx,      sy + hh),
            (sx + hw, sy + hh + hh),
            (sx + hw, sy + hh + hh + wall_h),
            (sx,      sy + hh + wall_h),
        ])
        # Top
        pygame.draw.polygon(surf, color_top, [
            (sx,      sy),
            (sx - hw, sy + hh),
            (sx,      sy + hh + hh),
            (sx + hw, sy + hh),
        ])
    elif tile_type == 2:  # water
        pygame.draw.polygon(surf, WATER_COLOR, [
            (sx,      sy),
            (sx - hw, sy + hh),
            (sx,      sy + hh + hh),
            (sx + hw, sy + hh),
        ])
        # shimmer
        shine = pygame.Surface((ISO_TILE_W, ISO_TILE_H), pygame.SRCALPHA)
        pygame.draw.ellipse(shine, (255, 255, 255, 40), (hw//2, hh//4, hw, hh//2))
        surf.blit(shine, (sx - hw, sy))
    elif tile_type == 3:  # tree
        c = GRASS_COLORS[(gx + gy) % len(GRASS_COLORS)]
        pygame.draw.polygon(surf, c, [
            (sx,      sy),
            (sx - hw, sy + hh),
            (sx,      sy + hh + hh),
            (sx + hw, sy + hh),
        ])
        # Trunk
        pygame.draw.rect(surf, (100, 70, 40), (sx - 4, sy - 10, 8, 20))
        # Canopy
        pygame.draw.circle(surf, (50, 120, 50), (sx, sy - 14), 18)
        pygame.draw.circle(surf, (40, 100, 40), (sx - 6, sy - 10), 13)
        pygame.draw.circle(surf, (60, 140, 55), (sx + 5, sy - 18), 12)
    elif tile_type == 4:  # dirt
        pygame.draw.polygon(surf, DIRT_COLOR, [
            (sx,      sy),
            (sx - hw, sy + hh),
            (sx,      sy + hh + hh),
            (sx + hw, sy + hh),
        ])
    else:  # grass
        c = GRASS_COLORS[(gx + gy) % len(GRASS_COLORS)]
        pygame.draw.polygon(surf, c, [
            (sx,      sy),
            (sx - hw, sy + hh),
            (sx,      sy + hh + hh),
            (sx + hw, sy + hh),
        ])
        # Outline
        pygame.draw.polygon(surf, (60, 110, 50), [
            (sx,      sy),
            (sx - hw, sy + hh),
            (sx,      sy + hh + hh),
            (sx + hw, sy + hh),
        ], 1)
