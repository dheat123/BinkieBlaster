"""Input handling for keyboard and gamepad in Isometric RPG"""

import pygame
import math

def setup_joystick():
    """Initialize joystick if available."""
    pygame.joystick.init()
    joystick = None
    if pygame.joystick.get_count() > 0:
        joystick = pygame.joystick.Joystick(0)
        joystick.init()
    return joystick

def get_movement_input(keys, joystick):
    """Get normalized movement vector from keyboard or gamepad."""
    dx, dy = 0.0, 0.0

    # Keyboard
    if keys[pygame.K_LEFT] or keys[pygame.K_a]: dx -= 1
    if keys[pygame.K_RIGHT] or keys[pygame.K_d]: dx += 1
    if keys[pygame.K_UP] or keys[pygame.K_w]: dy -= 1
    if keys[pygame.K_DOWN] or keys[pygame.K_s]: dy += 1

    # Gamepad
    if joystick:
        ax = joystick.get_axis(0)
        ay = joystick.get_axis(1)
        if abs(ax) > 0.15: dx += ax
        if abs(ay) > 0.15: dy += ay

    # Normalize
    mag = math.hypot(dx, dy)
    if mag > 1.0:
        dx /= mag
        dy /= mag

    return dx, dy, mag > 0.05

def vec_to_dir8(dx, dy):
    """Convert movement vector to 8-direction index (0=S, CW)."""
    if dx == 0 and dy == 0:
        return None
    angle = math.atan2(dy, dx)
    angle = (angle + math.tau) % math.tau
    idx = int((angle / math.tau) * 8 + 0.5) % 8
    remap = [6, 7, 0, 1, 2, 3, 4, 5]  # Remap to start with South=0
    return remap[idx]
