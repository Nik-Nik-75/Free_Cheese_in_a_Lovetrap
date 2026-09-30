import pygame
import random

##################################### Funktions #####################################

def get_mid_screen(screen):
    return pygame.Vector2(screen.get_width() / 2, screen.get_height() / 2)

def turn_to(who_pos, where):
    new_direction = pygame.Vector2(where - who_pos)
    new_direction = new_direction.normalize() if new_direction.length_squared() else new_direction
    return new_direction

def random_direction():
    return pygame.Vector2(random.randint(-1, 1), random.randint(-1, 1))

def teleport_from_mouse(distance, screen):
    mouse_pos = pygame.mouse.get_pos()
    max_attempts=500
    for _ in range(max_attempts):
        pos = pygame.Vector2(
            random.randint(0, screen.get_width()),
            random.randint(0, screen.get_height())
        )
        if pos.distance_to(mouse_pos) >= distance:
            return pos
    # fallback 
    for _ in range(max_attempts):
        pos = pygame.Vector2(
            random.randint(0, screen.get_width()),
            random.randint(0, screen.get_height())
        )
        if pos.distance_to(mouse_pos) >= distance/1.5:
            return pos
    # fallback 2
    print("fail teleport_from_mouse")
    return pygame.Vector2(
        random.randint(0, screen.get_width()),
        random.randint(0, screen.get_height())
    )