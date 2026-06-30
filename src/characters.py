"""Characters and sprites for Isometric RPG"""

import pygame
import math
from MelvinMosely import SpriteSheet  # If needed for external sheets

TILE_W, TILE_H = 64, 64
DIRS = 8
WALK_FRAMES = 4
ATTACK_FRAMES = 4
TOTAL_COLS = WALK_FRAMES + ATTACK_FRAMES

PALETTE = {
    "skin":   (230, 185, 140),
    "hair":   (80,  50,  20),
    "shirt":  (60,  100, 200),
    "pants":  (40,  60,  120),
    "boots":  (60,  40,  20),
    "sword":  (200, 210, 230),
    "guard":  (200, 160, 50),
    "shadow": (0,   0,   0,  60),
    "outline":(30,  20,  10),
}

def draw_character(surf, x, y, dir_idx, frame, is_attack):
    """Draw a tiny pixel-art character into surf at pixel (x,y)."""
    cx, cy = x + TILE_W // 2, y + TILE_H // 2

    # Bob for walk
    bob = 0
    if not is_attack:
        bob = int(math.sin(frame * math.pi / 2) * 2)

    angle = (dir_idx / DIRS) * math.tau  # facing angle

    # Helper: draw ellipse relative to character center
    def rel_ellipse(color, rx, ry, ox, oy, w=0):
        pygame.draw.ellipse(surf, color,
            (cx + ox - rx, cy + oy - ry + bob, rx*2, ry*2), w)

    def rel_rect(color, rw, rh, ox, oy, w=0):
        pygame.draw.rect(surf, color,
            (cx + ox - rw//2, cy + oy - rh//2 + bob, rw, rh), w)

    # Shadow
    shadow_surf = pygame.Surface((TILE_W, TILE_H), pygame.SRCALPHA)
    pygame.draw.ellipse(shadow_surf, (0, 0, 0, 40),
                        (TILE_W//2 - 14, TILE_H//2 + 18, 28, 10))
    surf.blit(shadow_surf, (x, y))

    # Legs
    leg_swing = int(math.sin(frame * math.pi / 2) * 5) if not is_attack else 0
    rel_ellipse(PALETTE["pants"], 5, 7, -5, 12 + leg_swing)
    rel_ellipse(PALETTE["pants"], 5, 7,  5, 12 - leg_swing)
    rel_ellipse(PALETTE["boots"], 4, 4, -5, 18 + leg_swing)
    rel_ellipse(PALETTE["boots"], 4, 4,  5, 18 - leg_swing)

    # Torso
    rel_rect(PALETTE["shirt"], 16, 14, 0, 2)

    # Arms
    arm_swing = int(math.sin(frame * math.pi / 2) * 6) if not is_attack else 0
    rel_ellipse(PALETTE["skin"], 4, 5, -10, 4 - arm_swing)
    if is_attack:
        # Sword arm swings forward
        attack_angle = (frame / ATTACK_FRAMES) * math.pi - math.pi / 4
        ax = int(math.cos(attack_angle) * 14)
        ay = int(math.sin(attack_angle) * 10) - 4
        rel_ellipse(PALETTE["skin"], 4, 5, 10 + ax, ay)
        # Sword
        sx1 = cx + 10 + ax
        sy1 = cy + ay + bob
        sx2 = sx1 + int(math.cos(attack_angle) * 20)
        sy2 = sy1 + int(math.sin(attack_angle) * 20)
        pygame.draw.line(surf, PALETTE["guard"], (sx1, sy1), (sx1 + int(math.cos(attack_angle)*5), sy1 + int(math.sin(attack_angle)*5)), 4)
        pygame.draw.line(surf, PALETTE["sword"], (sx1, sy1), (sx2, sy2), 2)
        # Swing arc flash
        if frame >= ATTACK_FRAMES - 1:
            pygame.draw.arc(surf, (255, 255, 200, 120),
                (sx1-15, sy1-15, 30, 30), attack_angle - 0.5, attack_angle + 0.5, 2)
    else:
        rel_ellipse(PALETTE["skin"], 4, 5, 10, 4 + arm_swing)
        # Sword held at side
        rel_rect(PALETTE["sword"], 2, 16, 14, 10)
        rel_rect(PALETTE["guard"], 6, 2, 14, 4)

    # Head
    rel_ellipse(PALETTE["skin"], 9, 9, 0, -8)
    rel_ellipse(PALETTE["hair"], 9, 5, 0, -14)

    # Eyes
    ex = int(math.sin(angle) * 4)
    rel_ellipse((30, 20, 10), 2, 2, ex - 2, -8)
    rel_ellipse((30, 20, 10), 2, 2, ex + 2, -8)

def generate_sprite_sheet():
    """Generate the full 8-dir walk + attack sprite sheet."""
    sheet_w = TILE_W * TOTAL_COLS
    sheet_h = TILE_H * DIRS
    sheet = pygame.Surface((sheet_w, sheet_h), pygame.SRCALPHA)
    sheet.fill((0, 0, 0, 0))

    for dir_idx in range(DIRS):
        for frame in range(WALK_FRAMES):
            x = frame * TILE_W
            y = dir_idx * TILE_H
            draw_character(sheet, x, y, dir_idx, frame, is_attack=False)

        for frame in range(ATTACK_FRAMES):
            x = (WALK_FRAMES + frame) * TILE_W
            y = dir_idx * TILE_H
            draw_character(sheet, x, y, dir_idx, frame, is_attack=True)

    return sheet


class Player:
    """Player entity with position, animation state, and sprite handling."""
    def __init__(self):
        self.px, self.py = 8.0, 8.0
        self.speed = 4.0
        self.facing = 0
        self.is_attacking = False
        self.attack_frame = 0
        self.attack_timer = 0.0
        self.ATTACK_DUR = 0.4

        self.walk_frame = 0
        self.walk_timer = 0.0
        self.WALK_FRAME_DUR = 0.12

        self.sprite_sheet = generate_sprite_sheet()

    def get_frame(self, dir_idx, frame, is_attack):
        """Extract frame from sprite sheet."""
        col = (WALK_FRAMES + frame) if is_attack else frame
        row = dir_idx
        return self.sprite_sheet.subsurface(
            pygame.Rect(col * TILE_W, row * TILE_H, TILE_W, TILE_H)
        )

    def update(self, dt, iso_dx, iso_dy, moving, keys=None, joystick=None):
        """Update player state."""
        if self.is_attacking:
            self.attack_timer += dt
            self.attack_frame = int((self.attack_timer / self.ATTACK_DUR) * ATTACK_FRAMES)
            if self.attack_timer >= self.ATTACK_DUR:
                self.is_attacking = False
                self.attack_frame = 0
        elif moving:
            # Facing update handled in game loop
            self.walk_timer += dt
            if self.walk_timer >= self.WALK_FRAME_DUR:
                self.walk_timer = 0.0
                self.walk_frame = (self.walk_frame + 1) % WALK_FRAMES
        else:
            self.walk_frame = 0
            self.walk_timer = 0.0

    def move(self, iso_dx, iso_dy, dt):
        """Attempt movement with collision."""
        nx = self.px + iso_dx * self.speed * dt
        ny = self.py + iso_dy * self.speed * dt

        from level import is_walkable
        if is_walkable(nx, self.py):
            self.px = nx
        if is_walkable(self.px, ny):
            self.py = ny
