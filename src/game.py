"""Main Game Loop for Isometric RPG"""

import pygame
import math
import sys
from level import WORLD_MAP, MAP_H, MAP_W, cart_to_iso, draw_iso_tile, is_walkable
from characters import Player
from controller import setup_joystick, get_movement_input, vec_to_dir8

class Game:
    def __init__(self):
        self.W, self.H = 900, 600
        self.screen = pygame.display.set_mode((self.W, self.H))
        pygame.display.set_caption("Isometric RPG – Walk & Swing")
        self.clock = pygame.time.Clock()

        self.joystick = setup_joystick()

        self.player = Player()

        self.particles = []
        self.font_big = pygame.font.SysFont("monospace", 16, bold=True)
        self.font_tiny = pygame.font.SysFont("monospace", 13)

    def spawn_slash_particles(self):
        """Spawn particles for sword swing."""
        facing = self.player.facing
        for _ in range(18):
            a = math.radians(facing * 45 + (math.pi * (0.5 - hash(str(_)) % 100 / 100.0)))
            spd = 60 + (hash(str(_)) % 80)
            self.particles.append({
                "x": self.player.px, "y": self.player.py,
                "vx": math.cos(a) * spd * 0.01,
                "vy": math.sin(a) * spd * 0.01,
                "life": 0.35,
                "max_life": 0.35,
                "color": (255, 240, 150),
            })

    def world_to_screen(self, gx, gy):
        """Convert world grid to screen coords relative to camera (player)."""
        sx, sy = cart_to_iso(gx, gy)
        cam_sx, cam_sy = cart_to_iso(self.player.px, self.player.py)
        return sx - cam_sx + self.W // 2, sy - cam_sy + self.H // 2 + 40

    def update_particles(self, dt):
        """Update particle system."""
        for p in self.particles[:]:
            p["life"] -= dt
            p["x"] += p["vx"]
            p["y"] += p["vy"]
            if p["life"] <= 0:
                self.particles.remove(p)

    def draw(self):
        """Render the game world."""
        self.screen.fill((20, 15, 30))

        # Draw tiles
        for gy in range(MAP_H):
            for gx in range(MAP_W):
                tile = WORLD_MAP[gy][gx]
                sx, sy = self.world_to_screen(gx, gy)
                cam_sx, cam_sy = cart_to_iso(self.player.px, self.player.py)
                tile_sx, tile_sy = cart_to_iso(gx, gy)
                ox = tile_sx - cam_sx + self.W // 2
                oy = tile_sy - cam_sy + self.H // 2 + 40
                if -64 < ox < self.W + 64 and -96 < oy < self.H + 96:
                    draw_iso_tile(self.screen, gx, gy, tile, ox, oy)

        # Draw particles
        cam_sx, cam_sy = cart_to_iso(self.player.px, self.player.py)
        for p in self.particles:
            psx, psy = cart_to_iso(p["x"], p["y"])
            psx = psx - cam_sx + self.W // 2
            psy = psy - cam_sy + self.H // 2 + 40
            alpha = int(255 * (p["life"] / p["max_life"]))
            size = max(1, int(4 * p["life"] / p["max_life"]))
            s = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
            pygame.draw.circle(s, (*p["color"], alpha), (size, size), size)
            self.screen.blit(s, (int(psx) - size, int(psy) - size))

        # Draw player
        char_sx = self.W // 2 - 32
        char_sy = self.H // 2 + 40 - 64 + 16 - 8

        if self.player.is_attacking:
            frame_surf = self.player.get_frame(self.player.facing, min(self.player.attack_frame, 3), True)
        else:
            frame_surf = self.player.get_frame(self.player.facing, self.player.walk_frame, False)

        self.screen.blit(frame_surf, (char_sx, char_sy))

        # HUD
        hud = pygame.Surface((220, 80), pygame.SRCALPHA)
        hud.fill((0, 0, 0, 130))
        pygame.draw.rect(hud, (80, 200, 120, 180), (0, 0, 220, 80), 2)
        self.screen.blit(hud, (10, 10))

        label = self.font_big.render("ISO RPG", True, (80, 220, 140))
        self.screen.blit(label, (20, 16))

        ctrl = self.font_tiny.render("WASD/Arrows: Move", True, (180, 220, 180))
        self.screen.blit(ctrl, (20, 36))
        ctrl2 = self.font_tiny.render("Space/J/Gamepad A: Attack", True, (180, 220, 180))
        self.screen.blit(ctrl2, (20, 52))
        pos_lbl = self.font_tiny.render(f"Pos: ({self.player.px:.1f}, {self.player.py:.1f})", True, (140, 180, 140))
        self.screen.blit(pos_lbl, (20, 68))

        # Sprite sheet preview
        preview_w, preview_h = 128, 128  # scaled down
        preview = pygame.transform.scale(self.player.sprite_sheet, (preview_w, preview_h))
        px_pos = self.W - preview_w - 10
        py_pos = self.H - preview_h - 10
        bg = pygame.Surface((preview_w + 4, preview_h + 20), pygame.SRCALPHA)
        bg.fill((0, 0, 0, 160))
        self.screen.blit(bg, (px_pos - 2, py_pos - 18))
        sheet_lbl = self.font_tiny.render("Sprite Sheet", True, (180, 180, 200))
        self.screen.blit(sheet_lbl, (px_pos, py_pos - 16))
        self.screen.blit(preview, (px_pos, py_pos))

        # Highlight current
        cur_col = (4 + min(self.player.attack_frame, 3)) if self.player.is_attacking else self.player.walk_frame
        cur_row = self.player.facing
        hl = pygame.Surface((16, 16), pygame.SRCALPHA)
        pygame.draw.rect(hl, (255, 255, 0, 120), (0, 0, 16, 16))
        pygame.draw.rect(hl, (255, 255, 0, 220), (0, 0, 16, 16), 1)
        self.screen.blit(hl, (px_pos + cur_col * 16, py_pos + cur_row * 16))

        if self.player.is_attacking and self.player.attack_frame >= 3:
            flash = pygame.Surface((self.W, self.H), pygame.SRCALPHA)
            flash.fill((255, 240, 100, 18))
            self.screen.blit(flash, (0, 0))

    def run(self):
        """Main game loop."""
        running = True
        dt = 0.0

        while running:
            dt = self.clock.tick(60) / 1000.0

            # Events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN:
                    if event.key in (pygame.K_ESCAPE, pygame.K_q):
                        running = False
                    if event.key in (pygame.K_SPACE, pygame.K_j, pygame.K_z) and not self.player.is_attacking:
                        self.player.is_attacking = True
                        self.player.attack_frame = 0
                        self.player.attack_timer = 0.0
                        self.spawn_slash_particles()
                if event.type == pygame.JOYBUTTONDOWN:
                    if event.button in (0, 1, 2, 3) and not self.player.is_attacking:
                        self.player.is_attacking = True
                        self.player.attack_frame = 0
                        self.player.attack_timer = 0.0
                        self.spawn_slash_particles()

            # Input
            keys = pygame.key.get_pressed()
            dx, dy, moving = get_movement_input(keys, self.joystick)

            # Isometric movement
            iso_dx = (dx - dy) * 0.707
            iso_dy = (dx + dy) * 0.707

            # Attack handled in player.update

            # Movement
            if moving and not self.player.is_attacking:
                d = vec_to_dir8(iso_dx, iso_dy)
                if d is not None:
                    self.player.facing = d
                self.player.move(iso_dx, iso_dy, dt)

            self.player.update(dt, iso_dx, iso_dy, moving)

            self.update_particles(dt)

            self.draw()

            pygame.display.flip()

        pygame.quit()
        sys.exit()
