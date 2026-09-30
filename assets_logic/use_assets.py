import pygame
import random
from . import get_assets

class Music():
    def __init__(self, calm, activ):
        self.calm = calm
        self.activ = activ
        self.ch1 = None
        self.ch2 = None
        self.ch1_volume = 1
        self.ch2_volume = 0
        self.ch1_volume_moveto = 1
        self.ch2_volume_moveto = 0

    def update(self, dt):
        if self.ch1 != None:

            self.ch1_volume += (self.ch1_volume_moveto-self.ch1_volume)*dt*2
            self.ch2_volume += (self.ch2_volume_moveto-self.ch2_volume)*dt*2
            if abs(self.ch1_volume_moveto-self.ch1_volume) < 0.01:
                self.ch1_volume = self.ch1_volume_moveto
            if abs(self.ch2_volume_moveto-self.ch2_volume) < 0.01:
                self.ch2_volume = self.ch2_volume_moveto

            self.ch1.set_volume(self.ch1_volume)
            self.ch2.set_volume(self.ch2_volume)

    def play(self):
        self.ch1 = get_assets.play_sound(self.calm, 0.9, -1)
        self.ch2 = get_assets.play_sound(self.activ, 0.9, -1)

    def switch(self):
        new_ch1_volume = self.ch2_volume_moveto
        new_ch2_volume = self.ch1_volume_moveto
        
        self.ch1_volume_moveto = new_ch1_volume
        self.ch2_volume_moveto = new_ch2_volume




class Animation:
    def __init__(self, frames, frame_duration=0.5):
        self.frames = frames
        self.frame_duration = frame_duration  # frames per second
        self.current_frame = 0
        self.timer = 0

    def get_frame(self, dt):
        if len(self.frames) == 1:
            return self.frames[0]
        self.timer += dt

        if self.timer >= self.frame_duration:
            self.timer = 0
            self.current_frame = (self.current_frame + 1) % len(self.frames) 
        return self.frames[self.current_frame]

    def get_random_frame(self, dt):
        if len(self.frames) == 1:
            return self.frames[0]
        self.timer += dt

        if self.timer >= self.frame_duration:
            self.timer = 0
            self.current_frame = random.randint(0, len(self.frames)-1)
        return self.frames[self.current_frame]

    def set_random_frame(self):
        if len(self.frames) == 1:
            return self.frames[0]
        self.current_frame = random.randint(0, len(self.frames)-1)
        return self.frames[self.current_frame]


class Dialogue:
    def __init__(self, lines, line_duration=5, looping_line=None, loop_action=None):
        self.lines = lines
        self.line_duration = line_duration  # lines per second
        self.current_line = 0
        self.timer = 0
        self.looping_line = looping_line  #If they said all the lines, which one should they loop
        self.loop_action = loop_action
        if self.looping_line == None:
            self.looping_line = len(self.lines)-1

    def get_line(self, dt, random=False):
        if self.line_duration == -1:
            return self.lines[self.current_line].split('\n')
        else:
            if len(self.lines) == 1:
                self.timer += dt
                if self.timer >= self.line_duration:
                    if self.loop_action:
                        self.loop_action()
                return self.lines[0].split('\n')
            self.timer += dt
    
            if self.timer >= self.line_duration:
                self.timer = 0
                if random:
                    self.set_random_line()
                else:
                    self.current_line = (self.current_line + 1)
                    if self.current_line > len(self.lines)-1:
                        self.current_line = self.looping_line
                        if self.loop_action:
                            self.loop_action()
            return self.lines[self.current_line].split('\n')

    def set_random_line(self):
        self.current_line = random.randint(self.looping_line, len(self.lines)-1)
        self.timer = 0

    def go_to_line(self,line=None):
        self.timer = 0
        if line != None:
            self.current_line = line
        else:
            if self.looping_line:
                self.current_line = self.looping_line


class Spritesheet:
    def __init__(self, image):
        self.sprite_sheet = image

    def get_sprite(self, x, y, w, h, x_m=1, y_m=1):
        sprite = pygame.Surface((w *x_m, h *y_m), pygame.SRCALPHA)
        sprite.blit(self.sprite_sheet,(0,0),(x *x_m, y *y_m, w *x_m, h *y_m))
        return sprite

class ProgressBar:
    def __init__(self, max_hp, pos, size=500, color="white", low_hp_percent=-1, name=None, sprites=None, low_hp_sprites=None, draw_background=True, low_hp_action = None):
        self.max_hp = max_hp
        self.hp = max_hp
        self.low_hp_percent = low_hp_percent
        self.low_hp_action = low_hp_action
        self.pos = pos
        self.size = size
        self.color = color
        self.draw_background = draw_background
        self.name = name #important to find sprites
        if name:
            if sprites:
                self.spritesheet = Spritesheet(get_assets.get_image(name + ".png"))
                self.sprites = Animation([self.spritesheet.get_sprite(*sprite) for sprite in sprites])
            if low_hp_sprites:
                self.spritesheet = Spritesheet(get_assets.get_image(name + ".png"))
                self.low_hp_sprites = Animation([self.spritesheet.get_sprite(*sprite) for sprite in low_hp_sprites])
            


    def update(self, current_hp):
        self.hp = current_hp

    def draw(self, screen, dt):
        bar_surface = pygame.Surface((self.pos.x + self.size, 30), pygame.SRCALPHA)

        if self.draw_background:
            pygame.draw.rect(bar_surface, (22,22,66, 100), pygame.Rect(0, 0, self.size, 30))    #background

        percent = (self.hp / self.max_hp)


        color_with_alpha = pygame.Color(self.color)
        if self.low_hp_action and self.low_hp_action <= 1:
            if self.low_hp_percent < percent:
                color_with_alpha.a = 255 
            else:
                color_with_alpha.a = 80

        pygame.draw.rect(bar_surface, (color_with_alpha), pygame.Rect(0, 0, self.size*percent, 30))

        screen.blit(bar_surface, (self.pos.x - (self.size//2), self.pos.y))

        if self.name:
            sprite = self.sprites.get_frame(dt)
            if self.low_hp_action and self.low_hp_action >= 1 and self.low_hp_percent >= percent:
                sprite = self.low_hp_sprites.get_frame(dt)

            screen.blit(sprite, (self.pos.x - ((self.size//2)+70), self.pos.y - 23))