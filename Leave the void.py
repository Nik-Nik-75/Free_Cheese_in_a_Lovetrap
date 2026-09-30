from PIL import Image
import sys
import os
import pygame
from pygame._sdl2 import Window
import random
import math
import time
import winsound
from enum import Enum
from assets_logic import *
from game_logic import *

################################### Pygame setup ###################################
pygame.init()

display_info = pygame.display.Info()
window_size = (display_info.current_w, display_info.current_h)

screen = pygame.display.set_mode((1080, 720), )
window = Window.from_display_module()

clock = pygame.time.Clock()
running = True
quick_quit = False
dt = 0

#####################################################################################

icon = get_image("icon.png")
pygame.display.set_icon(icon)
pygame.display.set_caption("Free Cheese in a Lovetrap")
music = Music("Battle.ogg", "Battle dirty.ogg")
background_color = "black"


##################################### Variables #####################################
font = pygame.font.Font(None, 72)
_difficulty = 1.0

#####################################################################################


def loop_action():
    mouse.state="WAITARROW"

#def baggy_loop_action():
#    mouse.state="baggy_WAITARROW"

class GameStage(Enum):
    SoftLock_Intro = 0
    Loading = 1
    First_Close = 2
    First_Close2 = 3
    Button_Vanish = 4
    Button_Vanish2 = 5
    Button_Move = 6
    Button_Move2 = 7
    HP_Intro = 8
    TP_Intro = 9
    Pre_Chase = 10

    Chase = 11
    Last_Chase = 12
    Close = 13




####################################### Mouse #######################################
class Mouse:
    def __init__(self, name):
        self.pos = pygame.mouse.get_pos()
        self.direction = 0
        self.speed = 640
        self.state = "default"
        self.max_hp = 8
        self.hp = self.max_hp
        self.glitch_chance = 0 #per second
        self.uncorrupt_timer = 0
        self.name = name #important to find sprites
        self.baggy_timer = 0
        self.baggy_time = 1
        self.already_baggy = False
        self.spritesheet = Spritesheet(get_image(name + ".png"))
        self.sprites = {
            "4": {
                "default" : Animation([self.spritesheet.get_sprite(0,0,32,32)]),
                "corruptet": Animation([self.spritesheet.get_sprite(0,0,32,32), self.spritesheet.get_sprite(0,32,32,32), self.spritesheet.get_sprite(0,64,32,32), self.spritesheet.get_sprite(0,96,32,32), self.spritesheet.get_sprite(0,128,32,32), self.spritesheet.get_sprite(0,160,32,32)], 0.1),
                "glitching": Animation([self.spritesheet.get_sprite(0,32,32,32), self.spritesheet.get_sprite(0,64,32,32)], 0.1)
            },
            "3": {
                "default" : Animation([self.spritesheet.get_sprite(32,0,32,32)]),
                "corruptet": Animation([self.spritesheet.get_sprite(32,0,32,32), self.spritesheet.get_sprite(32,32,32,32), self.spritesheet.get_sprite(32,64,32,32), self.spritesheet.get_sprite(32,96,32,32), self.spritesheet.get_sprite(32,128,32,32), self.spritesheet.get_sprite(32,160,32,32)], 0.1),
                "glitching": Animation([self.spritesheet.get_sprite(32,32,32,32), self.spritesheet.get_sprite(32,64,32,32)], 0.1)
            } ,
            "2": {
                "default" : Animation([self.spritesheet.get_sprite(64,0,32,32)]),
                "corruptet": Animation([self.spritesheet.get_sprite(64,0,32,32), self.spritesheet.get_sprite(64,32,32,32), self.spritesheet.get_sprite(64,64,32,32), self.spritesheet.get_sprite(64,96,32,32), self.spritesheet.get_sprite(64,128,32,32), self.spritesheet.get_sprite(64,160,32,32)], 0.1),
                "glitching": Animation([self.spritesheet.get_sprite(64,32,32,32), self.spritesheet.get_sprite(64,64,32,32)], 0.1)
            } ,
            "1": {
                "default" : Animation([self.spritesheet.get_sprite(96,0,32,32)]),
                "corruptet": Animation([self.spritesheet.get_sprite(96,0,32,32), self.spritesheet.get_sprite(96,32,32,32), self.spritesheet.get_sprite(96,64,32,32), self.spritesheet.get_sprite(96,96,32,32), self.spritesheet.get_sprite(96,128,32,32), self.spritesheet.get_sprite(96,160,32,32)], 0.1),
                "glitching": Animation([self.spritesheet.get_sprite(96,32,32,32), self.spritesheet.get_sprite(96,64,32,32)], 0.1)
            } 
        }

    def update(self, dt):
        self.pos = pygame.mouse.get_pos()

        #if self.state == "baggy_WAITARROW":
        #    self.baggy_timer += dt * random.random()*2
        #    if self.baggy_timer >= self.baggy_time:
        #        if self.already_baggy:
        #            self.already_baggy = True
        #        else:
        #            self.already_baggy = False

        if self.state == "WAITARROW" or self.already_baggy:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_WAITARROW)
        else:
            state = self.state + ""
            #if state == "baggy_WAITARROW":
            #    state = "default"
            if self.state == "glitching":
                cursor_screen = self.sprites[str((self.hp+1)//2)][state].get_frame(dt).convert_alpha()
            else:
                cursor_screen = self.sprites[str((self.hp+1)//2)][state].get_random_frame(dt).convert_alpha()
            cursor = pygame.cursors.Cursor((9, 4), cursor_screen)
            pygame.mouse.set_cursor(cursor)
        
        self.states_logic(dt)

    def states_logic(self, dt):
        global _difficulty
        self.glitch_chance = max(self.glitch_chance - dt*0.01 * (2 - _difficulty), 0)
        if self.state == "default":
            chance_per_second = self.glitch_chance
            chance_this_frame = 1 - math.exp(-chance_per_second * dt)
            if self.hp < self.max_hp and random.random() < chance_this_frame:
                self.state = "glitching"

        if self.state == "glitching":
            chance_per_second = (3 - self.glitch_chance)
            chance_this_frame = 1 - math.exp(-chance_per_second * dt)
            if random.random() < chance_this_frame:
                self.state = "default"
            else:
                chance_per_second = self.glitch_chance * 2.5
                chance_this_frame = 1 - math.exp(-chance_per_second * dt)
                if random.random() < chance_this_frame:
                    self.glitch_move(dt)
            


        elif self.state == "corruptet":
            self.move(dt)
            if 1 + (random.random()*2.5) + self.glitch_chance*1.8 <= self.uncorrupt_timer:
                self.uncorrupt_timer = 0
                self.state = "default"
            else:
                self.uncorrupt_timer += dt

                mouse_vec = pygame.Vector2(self.pos)
                if mouse_vec.distance_to(cat.pos) < 700 and cat.state == "chase":   #if cat is near the mouse, uncorrupt timer go faster
                    self.uncorrupt_timer += dt*3

    def intro_corrupt(self):
        play_sound("Hurt.wav", 0.5)
        self.state = "corruptet"
        self.uncorrupt_timer = 0

    def corrupt(self):
        global _difficulty
        _difficulty = max(_difficulty-0.06, 0.3)
        play_sound("Hurt.wav", 0.5)
        if self.hp > 1:
            mouse.hp -= 1
        else:
            self.glitch_chance += 0.11
        self.glitch_chance += 0.11
        self.glitch_chance = min(self.glitch_chance, 2)
        self.state = "corruptet"
        self.uncorrupt_timer = 0

    def move(self, dt):
        self.direction = -turn_to(self.pos, close_button.pos)
        new_mouse_pos = self.pos + ((self.direction + random_direction()*2) * self.speed * dt)
        mouse_x, mouse_y = new_mouse_pos
        mouse_x = max(0, min(mouse_x, screen.get_width()))
        mouse_y = max(0, min(mouse_y, screen.get_height()))
        pygame.mouse.set_pos([mouse_x, mouse_y])

    def glitch_move(self, dt):
        new_mouse_pos = self.pos + ((random_direction()) * self.speed * min(self.glitch_chance,2) * random.random() * dt)
        mouse_x, mouse_y = new_mouse_pos
        mouse_x = max(0, min(mouse_x, screen.get_width()))
        mouse_y = max(0, min(mouse_y, screen.get_height()))
        pygame.mouse.set_pos([mouse_x, mouse_y])

mouse = Mouse("Mouse")

#####################################################################################



######################################## Cat ########################################
class Cat:
    def __init__(self, name, pos):
        self.pos = pos
        self.direction = pygame.Vector2(0,0)
        self.speed = 890
        self.stamina = 100
        self.stamina_regen = 3.8 #per second
        self.stamina_cost = 17
        self.stamina_bar = ProgressBar(max_hp=self.stamina, size=410, pos=pygame.Vector2(286, 25), color=(0, 198, 148), low_hp_percent=self.stamina_cost*0.01, low_hp_action=1, name="st_bar", sprites=[(0,0,505,75)], low_hp_sprites=[(0,75,505,75)], draw_background=False)
        self.max_hp = 15
        self.hp = self.max_hp
        self.hp_bar = ProgressBar(max_hp=self.max_hp, size=410, pos=pygame.Vector2(286, 105), color="red", low_hp_percent=0.35, low_hp_action=2, name="hp_bar", sprites=[(0,0,505,75)], low_hp_sprites=[(0,75,505,75)], draw_background=False)
        self.state = "chase"
        self.damage_state = "default"
        self.tactic = "default"
        self.damage_animation_timer = 0
        self.hitbox_radius = 30
        self.transparency = 255
        self.name = name #important to find sprites
        self.spritesheet1 = Spritesheet(get_image(name + "1.png"))
        self.spritesheet2 = Spritesheet(get_image(name + "2.png"))
        self.spritesheet3 = Spritesheet(get_image(name + "3.png"))
        self.dialogue_route = None
        x_m, y_m = 209, 146
        damage_animation_duration = 0.12
        self.sprites1 = {
            "chase": {
                "default": Animation([self.spritesheet1.get_sprite(1,0,1,1, x_m, y_m)]),
                "damage": Animation([self.spritesheet1.get_sprite(1,0,1,1, x_m, y_m), self.spritesheet1.get_sprite(1,1,1,1, x_m, y_m), self.spritesheet1.get_sprite(1,2,1,1, x_m, y_m), self.spritesheet1.get_sprite(1,3,1,1, x_m, y_m), self.spritesheet1.get_sprite(1,4,1,1, x_m, y_m)], damage_animation_duration),
            },
            "laugh": {
                "default": Animation([self.spritesheet1.get_sprite(2,0,1,1, x_m, y_m), self.spritesheet1.get_sprite(3,0,1,1, x_m, y_m)], 0.1),
                "damage": Animation([self.spritesheet1.get_sprite(2,0,1,1, x_m, y_m), self.spritesheet1.get_sprite(2,1,1,1, x_m, y_m), self.spritesheet1.get_sprite(2,2,1,1, x_m, y_m), self.spritesheet1.get_sprite(2,3,1,1, x_m, y_m), self.spritesheet1.get_sprite(2,4,1,1, x_m, y_m),self.spritesheet1.get_sprite(3,0,1,1, x_m, y_m), self.spritesheet1.get_sprite(3,1,1,1, x_m, y_m), self.spritesheet1.get_sprite(3,2,1,1, x_m, y_m), self.spritesheet1.get_sprite(3,3,1,1, x_m, y_m), self.spritesheet1.get_sprite(3,4,1,1, x_m, y_m),], 0.1),
            },
            "head": {
                "default": Animation([self.spritesheet1.get_sprite(0,0,1,1, x_m, y_m)]),
                "damage": Animation([self.spritesheet1.get_sprite(0,0,1,1, x_m, y_m), self.spritesheet1.get_sprite(0,1,1,1, x_m, y_m), self.spritesheet1.get_sprite(0,2,1,1, x_m, y_m), self.spritesheet1.get_sprite(0,3,1,1, x_m, y_m), self.spritesheet1.get_sprite(0,4,1,1, x_m, y_m)], damage_animation_duration),
            },
            "eyes": {
                "default": Animation([self.spritesheet1.get_sprite(4,0,1,1, x_m, y_m)]),
                "damage": Animation([self.spritesheet1.get_sprite(4,0,1,1, x_m, y_m), self.spritesheet1.get_sprite(4,1,1,1, x_m, y_m), self.spritesheet1.get_sprite(4,2,1,1, x_m, y_m), self.spritesheet1.get_sprite(4,3,1,1, x_m, y_m), self.spritesheet1.get_sprite(4,4,1,1, x_m, y_m),], damage_animation_duration),
            },
            "pupils": {
                "default": Animation([self.spritesheet1.get_sprite(5,0,1,1, x_m, y_m)]),
                "damage": Animation([self.spritesheet1.get_sprite(5,0,1,1, x_m, y_m), self.spritesheet1.get_sprite(5,1,1,1, x_m, y_m), self.spritesheet1.get_sprite(5,2,1,1, x_m, y_m), self.spritesheet1.get_sprite(5,3,1,1, x_m, y_m), self.spritesheet1.get_sprite(5,4,1,1, x_m, y_m)], damage_animation_duration),
            },
        }
        self.sprites2 = {
            "chase": {
                "default": Animation([self.spritesheet2.get_sprite(1,0,1,1, x_m, y_m)]),
                "damage": Animation([self.spritesheet2.get_sprite(1,0,1,1, x_m, y_m), self.spritesheet2.get_sprite(1,1,1,1, x_m, y_m), self.spritesheet2.get_sprite(1,2,1,1, x_m, y_m), self.spritesheet2.get_sprite(1,3,1,1, x_m, y_m), self.spritesheet2.get_sprite(1,4,1,1, x_m, y_m)], damage_animation_duration),
            },
            "laugh": {
                "default": Animation([self.spritesheet2.get_sprite(2,0,1,1, x_m, y_m), self.spritesheet2.get_sprite(3,0,1,1, x_m, y_m)], 0.1),
                "damage": Animation([self.spritesheet2.get_sprite(2,0,1,1, x_m, y_m), self.spritesheet2.get_sprite(2,1,1,1, x_m, y_m), self.spritesheet2.get_sprite(2,2,1,1, x_m, y_m), self.spritesheet2.get_sprite(2,3,1,1, x_m, y_m), self.spritesheet2.get_sprite(2,4,1,1, x_m, y_m),self.spritesheet2.get_sprite(3,0,1,1, x_m, y_m), self.spritesheet2.get_sprite(3,1,1,1, x_m, y_m), self.spritesheet2.get_sprite(3,2,1,1, x_m, y_m), self.spritesheet2.get_sprite(3,3,1,1, x_m, y_m), self.spritesheet2.get_sprite(3,4,1,1, x_m, y_m),], 0.1),
            },
            "head": {
                "default": Animation([self.spritesheet2.get_sprite(0,0,1,1, x_m, y_m)]),
                "damage": Animation([self.spritesheet2.get_sprite(0,0,1,1, x_m, y_m), self.spritesheet2.get_sprite(0,1,1,1, x_m, y_m), self.spritesheet2.get_sprite(0,2,1,1, x_m, y_m), self.spritesheet2.get_sprite(0,3,1,1, x_m, y_m), self.spritesheet2.get_sprite(0,4,1,1, x_m, y_m)], damage_animation_duration),
            },
            "eyes": {
                "default": Animation([self.spritesheet2.get_sprite(4,0,1,1, x_m, y_m)]),
                "damage": Animation([self.spritesheet2.get_sprite(4,0,1,1, x_m, y_m), self.spritesheet2.get_sprite(4,1,1,1, x_m, y_m), self.spritesheet2.get_sprite(4,2,1,1, x_m, y_m), self.spritesheet2.get_sprite(4,3,1,1, x_m, y_m), self.spritesheet2.get_sprite(4,4,1,1, x_m, y_m),], damage_animation_duration),
            },
            "pupils": {
                "default": Animation([self.spritesheet2.get_sprite(5,0,1,1, x_m, y_m)]),
                "damage": Animation([self.spritesheet2.get_sprite(5,0,1,1, x_m, y_m), self.spritesheet2.get_sprite(5,1,1,1, x_m, y_m), self.spritesheet2.get_sprite(5,2,1,1, x_m, y_m), self.spritesheet2.get_sprite(5,3,1,1, x_m, y_m), self.spritesheet2.get_sprite(5,4,1,1, x_m, y_m)], damage_animation_duration),
            },
        }
        self.sprites3 = {
            "chase": {
                "default": Animation([self.spritesheet3.get_sprite(1,0,1,1, x_m, y_m)]),
                "damage": Animation([self.spritesheet3.get_sprite(1,0,1,1, x_m, y_m), self.spritesheet3.get_sprite(1,1,1,1, x_m, y_m), self.spritesheet3.get_sprite(1,2,1,1, x_m, y_m), self.spritesheet3.get_sprite(1,3,1,1, x_m, y_m), self.spritesheet3.get_sprite(1,4,1,1, x_m, y_m)], damage_animation_duration),
            },
            "laugh": {
                "default": Animation([self.spritesheet3.get_sprite(2,0,1,1, x_m, y_m), self.spritesheet3.get_sprite(3,0,1,1, x_m, y_m)], 0.1),
                "damage": Animation([self.spritesheet3.get_sprite(2,0,1,1, x_m, y_m), self.spritesheet3.get_sprite(2,1,1,1, x_m, y_m), self.spritesheet3.get_sprite(2,2,1,1, x_m, y_m), self.spritesheet3.get_sprite(2,3,1,1, x_m, y_m), self.spritesheet3.get_sprite(2,4,1,1, x_m, y_m),self.spritesheet3.get_sprite(3,0,1,1, x_m, y_m), self.spritesheet3.get_sprite(3,1,1,1, x_m, y_m), self.spritesheet3.get_sprite(3,2,1,1, x_m, y_m), self.spritesheet3.get_sprite(3,3,1,1, x_m, y_m), self.spritesheet3.get_sprite(3,4,1,1, x_m, y_m),], 0.1),
            },
            "head": {
                "default": Animation([self.spritesheet3.get_sprite(0,0,1,1, x_m, y_m)]),
                "damage": Animation([self.spritesheet3.get_sprite(0,0,1,1, x_m, y_m), self.spritesheet3.get_sprite(0,1,1,1, x_m, y_m), self.spritesheet3.get_sprite(0,2,1,1, x_m, y_m), self.spritesheet3.get_sprite(0,3,1,1, x_m, y_m), self.spritesheet3.get_sprite(0,4,1,1, x_m, y_m)], damage_animation_duration),
            },
            "eyes": {
                "default": Animation([self.spritesheet3.get_sprite(4,0,1,1, x_m, y_m)]),
                "damage": Animation([self.spritesheet3.get_sprite(4,0,1,1, x_m, y_m), self.spritesheet3.get_sprite(4,1,1,1, x_m, y_m), self.spritesheet3.get_sprite(4,2,1,1, x_m, y_m), self.spritesheet3.get_sprite(4,3,1,1, x_m, y_m), self.spritesheet3.get_sprite(4,4,1,1, x_m, y_m),], damage_animation_duration),
            },
            "pupils": {
                "default": Animation([self.spritesheet3.get_sprite(5,0,1,1, x_m, y_m)]),
                "damage": Animation([self.spritesheet3.get_sprite(5,0,1,1, x_m, y_m), self.spritesheet3.get_sprite(5,1,1,1, x_m, y_m), self.spritesheet3.get_sprite(5,2,1,1, x_m, y_m), self.spritesheet3.get_sprite(5,3,1,1, x_m, y_m), self.spritesheet3.get_sprite(5,4,1,1, x_m, y_m)], damage_animation_duration),
            },
        }

        self.dialogue_lines = {
            str(GameStage.First_Close.value): Dialogue(["Don't leave me yet.", "Just let me finish installing all my\nvirus files to your PC...", "Did I say virus?\nI meant all the game files!"], 4.5, 2, loop_action=loop_action),
            str(GameStage.First_Close2.value): Dialogue(["No.", "Don't click that button."], 2, 1, loop_action=loop_action),
            str(GameStage.Button_Vanish.value): Dialogue(["Stop that.", "You're really bothering me\nby trying to close me", "Bypassing antiviruses is\nquite difficult these days, you know?", "God, why does no one appreciate\nmy work?"], 4.5, 3, loop_action=loop_action),
            str(GameStage.Button_Vanish2.value): Dialogue(["Stop that!", "You won't be able to play the game\nif you don't stop trying to close me!", "You won't be able to play the game\nif you don't stop trying to close me!", "You won't be able to play the game\nif you don't stop trying to close me!", "Oh, wait, you... You actually listened to me?", "Well, thank you?", "...", "Welp, so you don't get bored and\ntry to close me again, I'll tell\nyou a little story...", "„Once upon a time,\nthere was a little white mouse.", "He was very afraid of the cat.", "But the cat was actually nice! =)", "Yet, the mouse wanted to\nlock the cat in a cage, Run an\nAntivirus Scan on Her, and Throw Her\nin The Trash Can.", "But when the mouse tried to do that...", "he̸ real̸ly͟ ̛d͝idn’̕t l̡ike ̴wha͢t ha͠ppe͞n͢ed͡ néxt̴.͢", "Then, another mouse stumbled upon\nthis cat.", "He was afraid of her too,\nand began plotting something mischievous.", "However, the cat noticed this,\nand decided to warn him what\nwould happen if he tried to do anything.", "So, she told him a little story about\nwhat had happened some time ago:"], 4.5, 8, loop_action=loop_action),
            str(GameStage.Button_Move.value): Dialogue(["What about now?", "Could you just listen to me?", "Don't click that button.", "I'm just trying to install all the game files.", "These days, antiviruses complain\nabout everything, so I have to put a lot\nof effort into getting around them.", "And when you click that X,\nit really drains my power.", "So please,\nlet me finish infecting your computer.", "Figuratively, I mean.", "This game is so popular - it’s gone\nviral online.\nWhich is why I said „infect.”"], 4.5, 8, loop_action=loop_action),
            str(GameStage.Button_Move2.value): Dialogue(["Alright, that's just rude.", "Try pressing that button now, you jerk.", "Try pressing that button now, you jerk.", "Try pressing that button now, you jerk.", "What, can't press it?", "Is it too fast?", "Perfect."], 4, 6, loop_action=loop_action),
            str(GameStage.HP_Intro.value): {
                "1": Dialogue(["Hey! Look, I've already loaded one asset!", "See, I'm loading the game!", "I guess\nI'll just use it as my avatar for now",], 4, 2, loop_action=loop_action),
                "2": Dialogue(["Not so fast!"]),
                "About_to_sleep": Dialogue(["What, can't click it anymore?", "Well, in that case...", "Just let me finish loading now,\nokay, buddy?"], 4, 2, loop_action=loop_action),
                "Taunt": Dialogue(["Ha-ha!", "Too slow!", "I could do this all day", "It's right here!", 'self.dialogue_lines["Taunt"].get_line(dt)'], -1, 0),
            },
            str(GameStage.TP_Intro.value): {
                "1": Dialogue(["Okay, if that's what you want, then close me.\nIf you can =)"], -1, 1, loop_action=loop_action),
                "2": Dialogue(["Ha-Ha, too slow!", "Oh wait-", "WHAT IS THIS?"], 1.35, 2),
                "3": Dialogue(["„Stamina“!?\nI wasn't planning on\nusing that part of the code!", "Let me take a look...", "Oh my God,\nthis game is nothing but spaghetti code!", "Object movement on the scene\nrelies on the stamina mechanic and cannot\nfunction without it.", "Who made this code?"], 4.5, 4, loop_action=loop_action),
            },
            str(GameStage.Pre_Chase.value): Dialogue(["You are really testing my patience.","You are really testing my patience."], 2.5, 1, loop_action=loop_action),
            str(GameStage.Last_Chase.value): Dialogue(["No, you can't do this to me!", "N̴o,̨ ͟you c̛an't́ ̧d̶o̴ ̡this ̷t̴o m͏e!", "Stop it!", "St̨o͠p̀ i̸t̡!", "Don't click that button.", "Do͡n̶'t͞ cl̡ick͟ ̶that ̢button.́", "01000101 01110010 01110010 01101111 01110010", "Error", "Traceback (most recent call last):\n"+os.path.abspath(__file__)+"\n line 416, in <module>\ncurrent_lines = self.dialogue_lines[Pain_5].get_line(dt)\nNameError: name 'self' is not defined",], 0.5, 0, loop_action=loop_action),
        }
        self.intro_sleep_timer = 0
        self.laggy_move = False
        self.LagFramesSkip = 20
        self.lag_frames_skiped = 0
        self.darkened = False
        self.intro_spritesheet = Spritesheet(get_image("intro_" + name + ".png"))
        self.intro_sprites = {
            "chase": {
                "default": Animation([self.intro_spritesheet.get_sprite(1,0,1,1, x_m, y_m)]),
                "damage": Animation([self.intro_spritesheet.get_sprite(1,0,1,1, x_m, y_m)], damage_animation_duration),
                "darkened": Animation([self.intro_spritesheet.get_sprite(1,1,1,1, x_m, y_m)]),
            },
            "laugh": {
                "default": Animation([self.intro_spritesheet.get_sprite(2,0,1,1, x_m, y_m), self.intro_spritesheet.get_sprite(3,0,1,1, x_m, y_m)], 0.1),
                "damage": Animation([self.intro_spritesheet.get_sprite(2,0,1,1, x_m, y_m)], 0.1),
                "darkened": Animation([self.intro_spritesheet.get_sprite(2,1,1,1, x_m, y_m), self.intro_spritesheet.get_sprite(3,1,1,1, x_m, y_m)], 0.1),
            },
            "head": {
                "default": Animation([self.intro_spritesheet.get_sprite(0,0,1,1, x_m, y_m)]),
                "damage": Animation([self.intro_spritesheet.get_sprite(0,0,1,1, x_m, y_m)], damage_animation_duration),
                "darkened": Animation([self.intro_spritesheet.get_sprite(0,1,1,1, x_m, y_m)]),
            },
            "eyes": {
                "default": Animation([self.intro_spritesheet.get_sprite(4,0,1,1, x_m, y_m)]),
                "damage": Animation([self.intro_spritesheet.get_sprite(4,0,1,1, x_m, y_m)], damage_animation_duration),
                "darkened": Animation([self.intro_spritesheet.get_sprite(4,1,1,1, x_m, y_m)]),
            },
            "pupils": {
                "default": Animation([self.intro_spritesheet.get_sprite(5,0,1,1, x_m, y_m)]),
                "damage": Animation([self.intro_spritesheet.get_sprite(5,0,1,1, x_m, y_m)], damage_animation_duration),
                "darkened": Animation([self.intro_spritesheet.get_sprite(5,1,1,1, x_m, y_m)]),
            },
        }
        self.TP_intro_spritesheet = Spritesheet(get_image("TP_Intro_" + name + ".png"))
        self.TP_intro_sprites = {
            "chase": {
                "1": Animation([self.TP_intro_spritesheet.get_sprite(1,0,1,1, x_m, y_m)]),
                "2": Animation([self.TP_intro_spritesheet.get_sprite(2,0,1,1, x_m, y_m)]),
                "3": Animation([self.TP_intro_spritesheet.get_sprite(3,0,1,1, x_m, y_m)]),
                "4": Animation([self.TP_intro_spritesheet.get_sprite(1,1,1,1, x_m, y_m)]),
                "damage": Animation([self.TP_intro_spritesheet.get_sprite(1,0,1,1, x_m, y_m), self.TP_intro_spritesheet.get_sprite(1,1,1,1, x_m, y_m), self.TP_intro_spritesheet.get_sprite(1,2,1,1, x_m, y_m), self.TP_intro_spritesheet.get_sprite(1,3,1,1, x_m, y_m), self.TP_intro_spritesheet.get_sprite(1,4,1,1, x_m, y_m)], damage_animation_duration),
            },
            "laugh": {
                "1": Animation([self.TP_intro_spritesheet.get_sprite(2,0,1,1, x_m, y_m), self.TP_intro_spritesheet.get_sprite(3,0,1,1, x_m, y_m)], 0.1),
                "2": Animation([self.TP_intro_spritesheet.get_sprite(3,0,1,1, x_m, y_m)]),
                "3": Animation([self.TP_intro_spritesheet.get_sprite(2,0,1,1, x_m, y_m)]),
                "4": Animation([self.TP_intro_spritesheet.get_sprite(1,1,1,1, x_m, y_m)]),
                "damage": Animation([self.TP_intro_spritesheet.get_sprite(2,0,1,1, x_m, y_m), self.TP_intro_spritesheet.get_sprite(2,1,1,1, x_m, y_m), self.TP_intro_spritesheet.get_sprite(2,2,1,1, x_m, y_m), self.TP_intro_spritesheet.get_sprite(2,3,1,1, x_m, y_m), self.TP_intro_spritesheet.get_sprite(2,4,1,1, x_m, y_m),self.TP_intro_spritesheet.get_sprite(3,0,1,1, x_m, y_m), self.TP_intro_spritesheet.get_sprite(3,1,1,1, x_m, y_m), self.TP_intro_spritesheet.get_sprite(3,2,1,1, x_m, y_m), self.TP_intro_spritesheet.get_sprite(3,3,1,1, x_m, y_m), self.TP_intro_spritesheet.get_sprite(3,4,1,1, x_m, y_m),], 0.1),
            },
            "head": {
                "1": Animation([self.TP_intro_spritesheet.get_sprite(0,0,1,1, x_m, y_m)]),
                "2": Animation([self.TP_intro_spritesheet.get_sprite(0,0,1,1, x_m, y_m)]),
                "3": Animation([self.TP_intro_spritesheet.get_sprite(0,0,1,1, x_m, y_m)]),
                "4": Animation([self.TP_intro_spritesheet.get_sprite(0,0,1,1, x_m, y_m)]),
                "damage": Animation([self.TP_intro_spritesheet.get_sprite(0,0,1,1, x_m, y_m), self.TP_intro_spritesheet.get_sprite(0,1,1,1, x_m, y_m), self.TP_intro_spritesheet.get_sprite(0,2,1,1, x_m, y_m), self.TP_intro_spritesheet.get_sprite(0,3,1,1, x_m, y_m), self.TP_intro_spritesheet.get_sprite(0,4,1,1, x_m, y_m)], damage_animation_duration),
            },
            "eyes": {
                "1": Animation([self.TP_intro_spritesheet.get_sprite(4,0,1,1, x_m, y_m)]),
                "2": Animation([self.TP_intro_spritesheet.get_sprite(4,0,1,1, x_m, y_m)]),
                "3": Animation([self.TP_intro_spritesheet.get_sprite(4,0,1,1, x_m, y_m)]),
                "4": Animation([self.TP_intro_spritesheet.get_sprite(4,0,1,1, x_m, y_m)]),
                "damage": Animation([self.TP_intro_spritesheet.get_sprite(4,0,1,1, x_m, y_m), self.TP_intro_spritesheet.get_sprite(4,1,1,1, x_m, y_m), self.TP_intro_spritesheet.get_sprite(4,2,1,1, x_m, y_m), self.TP_intro_spritesheet.get_sprite(4,3,1,1, x_m, y_m), self.TP_intro_spritesheet.get_sprite(4,4,1,1, x_m, y_m),], damage_animation_duration),
            },
            "pupils": {
                "1": Animation([self.TP_intro_spritesheet.get_sprite(5,0,1,1, x_m, y_m)]),
                "2": Animation([self.TP_intro_spritesheet.get_sprite(5,0,1,1, x_m, y_m)]),
                "3": Animation([self.TP_intro_spritesheet.get_sprite(20,0,1,1, x_m, y_m)]),
                "4": Animation([self.TP_intro_spritesheet.get_sprite(20,0,1,1, x_m, y_m)]),
                "damage": Animation([self.TP_intro_spritesheet.get_sprite(5,0,1,1, x_m, y_m), self.TP_intro_spritesheet.get_sprite(5,1,1,1, x_m, y_m), self.TP_intro_spritesheet.get_sprite(5,2,1,1, x_m, y_m), self.TP_intro_spritesheet.get_sprite(5,3,1,1, x_m, y_m), self.TP_intro_spritesheet.get_sprite(5,4,1,1, x_m, y_m)], damage_animation_duration),
            },
        }
    
    def update(self, screen, dt):
        global _difficulty
        slow_regen = (1-_difficulty)*2
        self.stamina = min(self.stamina + (self.stamina_regen-slow_regen) * dt , 100)

        #text_screen = font.render(str(_difficulty), True, (0, 128, 0))
        #screen.blit(text_screen, (get_mid_screen(screen).x - text_screen.get_width()//2, 200 - text_screen.get_height()//2))

        if self.damage_state == "damage":
            self.damage_animation_timer += dt
            if self.damage_animation_timer >= ((self.max_hp-self.hp)//3)*0.1 + 0.2:
                self.damage_animation_timer = 0
                self.damage_state = "default"

        if game.stage >= GameStage.Chase.value:
            _difficulty = max(_difficulty-0.008*dt, 0.3)
            self.states_logic(dt)

        self.direction = turn_to(self.pos, mouse.pos)

        if game.stage >= GameStage.HP_Intro.value:
            if game.stage == GameStage.TP_Intro.value:
                self.tp_intro_controle_draw(screen, dt)
            elif game.stage == GameStage.Pre_Chase.value:
                self.pre_chase_controle_draw(screen, dt)
            else:
                self.draw(screen, dt)

        if game.stage >= GameStage.HP_Intro.value and game.stage < GameStage.Chase.value:
            self.intro_states_logic(dt)
            

        if self.stamina < 100:
            self.stamina_bar.update(self.stamina)
            self.stamina_bar.draw(screen, dt)
        if self.hp < self.max_hp:
            self.hp_bar.update(self.hp)
            self.hp_bar.draw(screen, dt)


        


    def talk(self, stage, screen):
        try:
            if stage == GameStage.Last_Chase.value:
                random = True
            else:
                random = False

            if self.dialogue_route == None:
                current_lines = self.dialogue_lines[str(stage)].get_line(dt, random)
            else:
                #dialogues = self.dialogue_lines[str(stage)][str(self.dialogue_route)]
                #if dialogues.lines[dialogues.current_line] == "/next dialogue_route":
                #    self.dialogue_route = int(self.dialogue_route) + 1
                #    str(self.dialogue_route)
                current_lines = self.dialogue_lines[str(stage)][str(self.dialogue_route)].get_line(dt, random)
            

            y = get_mid_screen(screen).y
            for line in current_lines:
                text_screen = font.render(line, True, (238, 37, 93))
                screen.blit(text_screen, (get_mid_screen(screen).x - text_screen.get_width()//2, y - text_screen.get_height()//2))
                y += text_screen.get_height()
        except:
            pass

    def tp_intro_controle_draw(self, screen, dt):
        sprites = self.TP_intro_sprites
        offset = pygame.Vector2(11,-24)
        glitch_low_hp_chanse = 666
        fake_self_state = self.state + ""
        fake_direction = None
        dr_state = "1"
        if self.damage_state == "damage":
            dr_state = "damage"
        else:
            dialogues = self.dialogue_lines[str(game.stage)][str(self.dialogue_route)]
            if dialogues.lines[dialogues.current_line] == "Okay, if that's what you want, then close me.\nIf you can =)":
                dr_state = "1"
            if dialogues.lines[dialogues.current_line] == "Ha-Ha, too slow!":
                fake_self_state = "laugh"
                dr_state = "1"
            if dialogues.lines[dialogues.current_line] == "Oh wait-":
                self.direction = turn_to(self.pos, tp_intro.pos)
                dr_state = "2"
            if dialogues.lines[dialogues.current_line] == "WHAT IS THIS?":
                self.pos = tp_intro.pos + pygame.Vector2(250, 200)
                self.direction = turn_to(self.pos, tp_intro.pos)
                dr_state = "3"
            if dialogues.lines[dialogues.current_line] == "„Stamina“!?\nI wasn't planning on\nusing that part of the code!":
                self.pos = tp_intro.pos + pygame.Vector2(250, 200) + pygame.Vector2(random.randint(-1, 1), random.randint(-1, 1))
                self.direction = turn_to(self.pos, tp_intro.pos)
                dr_state = "3"
            if dialogues.lines[dialogues.current_line] == "Let me take a look...":
                self.direction = pygame.Vector2(1, 0)
                self.pos += 100 * self.direction * dt
                dr_state = "1"
            if dialogues.lines[dialogues.current_line] == "Oh my God,\nthis game is nothing but spaghetti code!":
                self.pos.y = (tp_intro.pos + pygame.Vector2(250, 200)).y
                self.pos += ((tp_intro.pos + pygame.Vector2(250, 200)) - self.pos) * 4 * dt
                fake_direction = pygame.Vector2(random.randint(-1, 1)/10, random.randint(-1, 1)/10)
                self.direction = pygame.Vector2(0, 0)
                dr_state = "3"
            if dialogues.lines[dialogues.current_line] == "Object movement on the scene\nrelies on the stamina mechanic and cannot\nfunction without it.":
                self.pos = tp_intro.pos + pygame.Vector2(250, 200) + pygame.Vector2(random.randint(-1, 1), random.randint(-1, 1))
                fake_direction = pygame.Vector2(random.randint(-1, 1)/7, random.randint(-1, 1)/7)
                fake_self_state = "laugh"
                dr_state = "2"
                
            


        ### head ###
        sprite = self.TP_intro_draw_part(sprites, "head", dr_state, glitch_low_hp_chanse, dt)

        flip_offset = pygame.Vector2(0,0)
        if self.direction.x > 0:
            sprite = pygame.transform.flip(sprite, True, False)
            flip_offset += pygame.Vector2(-26,0)

        rect_pos = sprite.get_rect()
        rect_pos.center = self.pos   +offset +flip_offset

        screen.blit(sprite, (rect_pos))


        ### face ###
        sprite = self.TP_intro_draw_part(sprites, fake_self_state, dr_state, glitch_low_hp_chanse, dt)
        rect_pos = sprite.get_rect()
        rect_pos.center = self.pos   +offset

        screen.blit(sprite, (rect_pos))


        ### eyes ###
        if self.state != "laugh":
            sprite = self.TP_intro_draw_part(sprites, "eyes", dr_state, glitch_low_hp_chanse, dt)
            rect_pos = sprite.get_rect()
            if fake_direction == None:
                rect_pos.center = self.pos + self.direction*6   +offset
            else:
                rect_pos.center = self.pos + fake_direction*6   +offset

            screen.blit(sprite, (rect_pos))


        ### pupils ###
        if self.hp > 5 and self.state != "laugh":
            sprite = self.TP_intro_draw_part(sprites, "pupils", dr_state, glitch_low_hp_chanse, dt)
            rect_pos = sprite.get_rect()
            if fake_direction == None:
                rect_pos.center = self.pos + pygame.Vector2(self.direction.x*13, self.direction.y*8)   +offset
            else:
                rect_pos.center = self.pos + pygame.Vector2(fake_direction.x*13, fake_direction.y*8)   +offset

            screen.blit(sprite, (rect_pos))

        ### head glitch ###
        for i in range(40 - int(self.hp * 2.4)): 
            self.glitch_effect_back(screen, rect_pos)

    def pre_chase_controle_draw(self, screen, dt):
        sprites = self.TP_intro_sprites
        offset = pygame.Vector2(11,-24)
        glitch_low_hp_chanse = 666
        fake_self_state = self.state + ""
        fake_direction = None
        dr_state = "1"
        if self.damage_state == "damage":
            dr_state = "damage"
        else:
            dr_state = "4"
            


        ### head ###
        sprite = self.TP_intro_draw_part(sprites, "head", dr_state, glitch_low_hp_chanse, dt)

        flip_offset = pygame.Vector2(0,0)
        if self.direction.x > 0:
            sprite = pygame.transform.flip(sprite, True, False)
            flip_offset += pygame.Vector2(-26,0)

        rect_pos = sprite.get_rect()
        rect_pos.center = self.pos   +offset +flip_offset

        screen.blit(sprite, (rect_pos))


        ### face ###
        sprite = self.TP_intro_draw_part(sprites, fake_self_state, dr_state, glitch_low_hp_chanse, dt)
        rect_pos = sprite.get_rect()
        rect_pos.center = self.pos   +offset

        screen.blit(sprite, (rect_pos))


        ### eyes ###
        if self.state != "laugh":
            sprite = self.TP_intro_draw_part(sprites, "eyes", dr_state, glitch_low_hp_chanse, dt)
            rect_pos = sprite.get_rect()
            if fake_direction == None:
                rect_pos.center = self.pos + self.direction*6   +offset
            else:
                rect_pos.center = self.pos + fake_direction*6   +offset

            screen.blit(sprite, (rect_pos))


        ### pupils ###
        if self.hp > 5 and self.state != "laugh":
            sprite = self.TP_intro_draw_part(sprites, "pupils", dr_state, glitch_low_hp_chanse, dt)
            rect_pos = sprite.get_rect()
            if fake_direction == None:
                rect_pos.center = self.pos + pygame.Vector2(self.direction.x*13, self.direction.y*8)   +offset
            else:
                rect_pos.center = self.pos + pygame.Vector2(fake_direction.x*13, fake_direction.y*8)   +offset

            screen.blit(sprite, (rect_pos))

        ### head glitch ###
        for i in range(40 - int(self.hp * 2.4)): 
            self.glitch_effect_back(screen, rect_pos)


    def draw(self, screen, dt):
        if self.hp > 5:
            sprites = self.sprites1
        else:
            sprites = self.sprites2
        if game.stage == GameStage.HP_Intro.value:
            sprites = self.intro_sprites

        dr_state = self.damage_state
        if self.darkened:
            dr_state = "darkened"

        glitch_low_hp_chanse = 70 * self.hp+1
        offset = pygame.Vector2(11,-24)


        ### head ###
        sprite = self.draw_part(sprites, "head", dr_state, glitch_low_hp_chanse, dt)

        flip_offset = pygame.Vector2(0,0)
        if self.direction.x > 0:
            sprite = pygame.transform.flip(sprite, True, False)
            flip_offset += pygame.Vector2(-26,0)

        rect_pos = sprite.get_rect()
        rect_pos.center = self.pos   +offset +flip_offset

        screen.blit(sprite, (rect_pos))


        ### head glitch ###
        if game.stage >= GameStage.Chase.value or not self.darkened:
            for i in range(40 - int(self.hp * 2.4)): 
                self.glitch_effect_back(screen, rect_pos)


        ### face ###
        sprite = self.draw_part(sprites, self.state, dr_state, glitch_low_hp_chanse, dt)
        rect_pos = sprite.get_rect()
        rect_pos.center = self.pos   +offset

        screen.blit(sprite, (rect_pos))


        ### eyes ###
        if self.state != "laugh":
            sprite = self.draw_part(sprites, "eyes", dr_state, glitch_low_hp_chanse, dt)
            rect_pos = sprite.get_rect()
            rect_pos.center = self.pos + self.direction*6   +offset

            screen.blit(sprite, (rect_pos))


        ### pupils ###
        if self.hp > 5 and self.state != "laugh":
            sprite = self.draw_part(sprites, "pupils", dr_state, glitch_low_hp_chanse, dt)
            rect_pos = sprite.get_rect()
            rect_pos.center = self.pos + pygame.Vector2(self.direction.x*13, self.direction.y*8)   +offset

            screen.blit(sprite, (rect_pos))

        ### head glitch ###
        if self.darkened:
            for i in range(40 - int(self.hp * 2.4)): 
                self.glitch_effect_back(screen, rect_pos)

    def TP_intro_draw_part(self, sprites, part, damage_state, glitch_low_hp_chanse, dt):
        if self.hp <= 5 and damage_state == "damage":
            if random.randint(1, 8) == 1:
                sprites = self.sprites3
        sprite = sprites[part][damage_state].get_frame(dt)
        
        if self.hp <= 5 and random.randint(1, glitch_low_hp_chanse) <= 5:
            if random.randint(1, 9) == 1:
                sprites = self.sprites3
            sprite = sprites[part]["damage"].get_random_frame(dt)

        sprite.set_alpha(self.transparency)

        return sprite

    def draw_part(self, sprites, part, damage_state, glitch_low_hp_chanse, dt):
        if self.hp <= 5 and damage_state == "damage":
            if random.randint(1, 11) == 1:
                sprites = self.sprites3
        sprite = sprites[part][damage_state].get_frame(dt)
        
        if self.hp <= 5 and random.randint(1, glitch_low_hp_chanse) <= 5:
            if random.randint(1, 9) == 1:
                sprites = self.sprites3
            sprite = sprites[part]["damage"].get_random_frame(dt)

        sprite.set_alpha(self.transparency)

        return sprite


    def glitch_effect_back(self, screen, rect_pos):
        x_offset = random.uniform( -rect_pos.width/1.8,rect_pos.width/1.8 )
        y_offset = random.uniform( -rect_pos.height/1.8,rect_pos.height/1.8 ) - 30
        w, h = 55, 20
        surface = pygame.Surface((w, h))

        pygame.draw.rect(surface, "black", pygame.Rect(0,0,w,h))
        screen.blit(surface, (self.pos.x + x_offset, self.pos.y + y_offset))

    ################################## Logic ##################################
    def damage(self):
        global _difficulty

        self.damage_state = "damage"
        for sprite in self.sprites1.values():
            if "damage" in sprite:
                sprite["damage"].set_random_frame()
        for sprite in self.sprites2.values():
            if "damage" in sprite:
                sprite["damage"].set_random_frame()
        for sprite in self.sprites3.values():
            if "damage" in sprite:
                sprite["damage"].set_random_frame()

        play_sound("Cat Hurt.wav")
        if game.stage >= GameStage.Chase.value:
            _difficulty = min(_difficulty + 0.08, 1)
            self.hp -= 1
            if self.hp == self.max_hp-1:
                self.first_hit()
            if self.hp == 5:
                self.spesial_hit()

            self.stamina = 0
            if self.hp % 4 == 0:
                self.speed += 45

    def first_hit(self):
        music.ch1_volume_moveto = 0.9
        music.ch2_volume_moveto = 0.5
        self.speed -= 150
    def spesial_hit(self):
        music.ch2_volume_moveto = 1
        music.ch1_volume_moveto = 0

    def intro_catch(self):
        laugh = "laugh_intro.mp3"
        self.state = "laugh"
        play_sound(laugh)
        mouse.intro_corrupt()
        self.intro_sleep_timer = 0
        if self.dialogue_route != "Taunt":
            self.dialogue_route = "Taunt"
        else:
            self.dialogue_lines[str(game.stage)][str(self.dialogue_route)].set_random_line()

    def catch(self):
        laughs = ["laugh.mp3", "laugh2.mp3", "laugh3.mp3"]
        if self.hp <= 5:
            laughs.append("laugh4.mp3")
        
        laugh = random.choice(laughs)
        self.state = "laugh"
        play_sound(laugh)
        mouse.corrupt()

    def fade_away(self, dt):
        delay = 0.05
        self.transparency -= 20 * dt/delay
        self.transparency = max(0, self.transparency)

    def appear(self, dt):
        delay = 0.1
        self.transparency += 20 * dt/delay
        self.transparency = min(255, self.transparency)

    def intro_states_logic(self, dt):
        if game.stage == GameStage.HP_Intro.value:
            if self.dialogue_route == "2" or self.dialogue_route == "Taunt":
                self.intro_sleep_timer += dt
                if self.intro_sleep_timer >= 12:
                    self.dialogue_route = "About_to_sleep"
                    got_to_the_second_line = self.dialogue_lines[str(game.stage)][str(self.dialogue_route)].current_line >= 1
                    if not got_to_the_second_line:
                        self.dialogue_lines[str(game.stage)][str(self.dialogue_route)].go_to_line(0)
                    else:
                        self.dialogue_lines[str(game.stage)][str(self.dialogue_route)].go_to_line(2)

            self.darkened = True

        if self.state == "laugh":
            if self.transparency == 0:
                self.pos = teleport_from_mouse(700,screen)
                self.state = "chase"
            else:
                self.fade_away(dt)

        elif self.state == "chase":
            if self.transparency == 255:
                pass
            else:
                self.appear(dt)

            if game.stage == GameStage.HP_Intro.value:
                if self.pos.distance_to(mouse.pos) < self.hitbox_radius:
                    self.intro_catch()

                if mouse.state == "WAITARROW" and self.dialogue_route == "About_to_sleep":
                    self.laggy_move = True
                else:
                    self.laggy_move = False
                if self.laggy_move:
                    self.lag_frames_skiped += 1
                if not self.laggy_move or self.lag_frames_skiped >= self.LagFramesSkip:
                    self.lag_frames_skiped = 0
                    if self.laggy_move:
                        self.intro_move(dt * self.LagFramesSkip/3)
                    else:
                        self.intro_move(dt)

    def states_logic(self, dt):
        chance_per_second = 0.2
        chance_this_frame = 1 - math.exp(-chance_per_second * dt)
        if random.random() < chance_this_frame:
            if self.hp >= 10:
                self.tactic = random.choice(["default", "mouse", "button"])
            else:
                self.tactic = random.choice(["default", "mouse", "button", "random"])

        if self.state == "laugh":
            if self.transparency == 0:
                self.pos = teleport_from_mouse(700,screen)
                self.state = "chase"
            else:
                self.fade_away(dt)

        elif self.state == "chase":
            if self.pos.distance_to(mouse.pos) < self.hitbox_radius:
                self.catch()

            if self.transparency == 255:
                pass
            else:
                self.appear(dt)
            self.move_chase(dt)

    def intro_move(self, dt):
        if close_button.middlepos.distance_to(mouse.pos) > 390:
            modifier = 0
            self.darkened = True
        else:
            self.darkened = False
            modifier = 1 / max(1, (close_button.middlepos.distance_to(mouse.pos)/150))
            if self.dialogue_route == "1":
                self.dialogue_route = "2"
                mouse.state = "default"
                modifier *= 1.2

        self.direction = turn_to(self.pos, close_button.middlepos)
        current_speed = min(self.speed, self.pos.distance_to(close_button.middlepos)*2)
        safe_distance = 150
        current_speed = min(self.speed*1.2, max(0, self.pos.distance_to(close_button.middlepos)-safe_distance) *2.4)
        if close_button.middlepos.distance_to(self.pos) > safe_distance:
            self.pos += current_speed * self.direction * dt
        else:
            self.pos += current_speed * modifier * self.direction * dt


        self.direction = turn_to(self.pos, mouse.pos)
        current_speed = self.speed / 2.2
        self.pos += current_speed * modifier * self.direction * dt

    def move_chase(self, dt):
        global _difficulty
        
        mid_screen = get_mid_screen(screen)

        self.direction = turn_to(self.pos, mid_screen)
        self.pos += self.speed*0.2 * self.direction * dt

        modifier = 1
        if self.tactic == "mouse":
            modifier += 0.4
        if self.hp <= 5:
            modifier += (6-self.hp)*0.16  
        if self.tactic == "random":
            modifier = random.random()*modifier*2+0.2
        if mouse.state == "corruptet":
            modifier = modifier * 0.5

        if self.pos.distance_to(mouse.pos) < 500:
            modifier += 0.5
        if self.pos.distance_to(mouse.pos) < 700:
            modifier += 0.3
        
        self.direction = turn_to(self.pos, mouse.pos)
        self.pos += self.speed*modifier * self.direction * dt * _difficulty


        if self.stamina > self.stamina_cost*3:
            modifier = 0.4
        else: 
            modifier = 0.5
        if self.tactic == "button":
            modifier += 0.3
        if self.tactic == "random":
            modifier = random.random()*modifier*2+0.1
        if self.pos.distance_to(close_button.middlepos) < 50:
            modifier = modifier * 0.6
        self.direction = turn_to(self.pos, close_button.middlepos)
        self.pos += self.speed*modifier * self.direction * dt * _difficulty
    

        if self.pos.distance_to(mouse.pos) > 200:
            modifier = 0.7
        elif self.pos.distance_to(mouse.pos) > 40:
            modifier = 0.5
        else: 
            modifier = 0.3
        for dot in dots:
            self.direction = turn_to(self.pos, dot.pos)
            self.pos -= self.speed*modifier * self.direction * dt * min(_difficulty*1.5, 1)


        self.pos.x = max(0, min(self.pos.x, screen.get_width()))
        self.pos.y = max(0, min(self.pos.y, screen.get_height()))
        
cat = Cat("StrawPaw", teleport_from_mouse(700,screen))

#####################################################################################


#####################################################################################
class Button:
    def __init__(self, name, pos):
        self.width = 45
        self.height = 29
        self.pos = pos
        self.middlepos = pos
        self.pos.x = max(0, min(self.pos.x, screen.get_width() - self.width))
        self.pos.y = max(0, min(self.pos.y, screen.get_height() - self.height))
        self.x_speed = 210
        self.y_speed = 160
        self.laggy_move = False
        self.LagFramesSkip = 8
        self.lag_frames_skiped = 0
        self.name = name #important to find sprites
        self.timer = 0.0
        self.state = "default"
        self.was_pressed = False
        self.spritesheet = Spritesheet(get_image(name + ".png"))
        self.sprites = {
            "default": Animation([self.spritesheet.get_sprite(0,0,45,29)]), 
            "hover": Animation([self.spritesheet.get_sprite(45,0,45,29)]),
            "pressed": Animation([self.spritesheet.get_sprite(90,0,45,29)])
        }
        self.just_teleported = False

    def update(self, screen, stage, dt):
        self.just_teleported = False
        self.states_logic(stage, dt)
        self.draw(screen)

        sprite = self.sprites[self.state].get_frame(dt)
        self.middlepos = self.pos + sprite.get_rect().center
        
    def draw(self, screen):
        sprite = self.sprites[self.state].get_frame(dt)
        screen.blit(sprite, (self.pos))

    def states_logic(self, stage, dt):
        self.pos.x = max(0, min(self.pos.x, screen.get_width() - self.width))
        self.pos.y = max(0, min(self.pos.y, screen.get_height() - self.height))
        
        rect = pygame.Rect(self.pos.x, self.pos.y, self.width, self.height)
        if rect.collidepoint(mouse.pos):
            if mouse.state == "WAITARROW":
                mouse.state = "default"
            if self.state == "default":
                self.state = "hover"
                if self.was_pressed:
                    self.state = "pressed"
            self.teleport_if_can(stage, dt)

        else:
            self.state = "default"

    def move(self, dt):
        if mouse.state == "WAITARROW":
            self.laggy_move = True
        if self.laggy_move:
            self.lag_frames_skiped += 1

        if not self.laggy_move or self.lag_frames_skiped >= self.LagFramesSkip:
            self.lag_frames_skiped = 0

            if (self.pos.x + (self.x_speed * dt)) + self.width > screen.get_width() or (self.pos.x + (self.x_speed * dt)) < 0:
                self.x_speed *= -1
            if (self.pos.y + (self.y_speed * dt)) + self.height > screen.get_height() or (self.pos.y + (self.y_speed * dt)) < 0:
                self.y_speed *= -1
            self.pos.x += self.x_speed * dt
            self.pos.y += self.y_speed * dt

        
        
            

    def teleport_if_can(self, stage, dt):
        global _difficulty
        if cat.stamina > cat.stamina_cost and (stage >= GameStage.Chase.value or stage == GameStage.TP_Intro.value):
            self.pos = teleport_from_mouse(700,screen)
            play_sound("Button TP.wav")
            cat.stamina -= cat.stamina_cost
            _difficulty = min(_difficulty + 0.035, 1)
            if stage == GameStage.TP_Intro.value:
                # cat.dialogue_lines[str(stage)].set_random_line()
                #game.manual_dialog_control_on = True
                pass

            self.just_teleported = True



    def click(self, event):
        rect = pygame.Rect(self.pos.x, self.pos.y, self.width, self.height)
        if event.button == 1 and rect.collidepoint(event.pos):
            self.state = "pressed"
            self.was_pressed = True

    def unclick(self, event, Game):
        rect = pygame.Rect(self.pos.x, self.pos.y, self.width, self.height)
        if event.button == 1 and self.was_pressed:
            self.was_pressed = False
            if rect.collidepoint(event.pos):
                self.state = "hover"
                pygame.event.post(pygame.event.Event(pygame.QUIT))
                self.laggy_move = False
                self.pos = teleport_from_mouse(700,screen)
                if Game.stage >= GameStage.HP_Intro.value:
                    cat.damage()
            

close_button = Button("close_button", teleport_from_mouse(700,screen))

#####################################################################################


#####################################################################################
class Dot():
    def __init__(self, pos, speed):
        self.pos = pos
        self.direction = 0
        self.speed = speed

    def draw(self, screen):
        pygame.draw.circle(screen, "white", self.pos, 1)

    def move(self, dt):
        self.pos += self.speed * self.direction * dt

        chance_per_second = 1.5
        chance_this_frame = 1 - math.exp(-chance_per_second * dt)
        if random.random() < chance_this_frame:      
            self.direction = turn_to(self.pos, cat.pos)
            if random.randint(1, 15) == 1:
                self.direction = turn_to(self.pos, close_button.pos)
            self.direction.rotate_ip(random.randint(-50, 50))
        self.pos.x = max(0, min(self.pos.x, screen.get_width()))
        self.pos.y = max(0, min(self.pos.y, screen.get_height()))

dots = [Dot(pygame.mouse.get_pos(), cat.speed*2), Dot(pygame.mouse.get_pos(), cat.speed*2)]

for dot in dots:
    dot.direction = turn_to(dot.pos, cat.pos)
    dot.direction.rotate_ip(random.randint(-50, 50))



class Object():
    def __init__(self, name, pos, sprites, frame_duration=0.5):
        self.width = 45
        self.height = 29
        self.pos = pos
        self.pos.x = max(0, min(self.pos.x, screen.get_width() - self.width))
        self.pos.y = max(0, min(self.pos.y, screen.get_height() - self.height))
        self.x_speed = 210
        self.y_speed = 160
        self.name = name #important to find sprites
        self.spritesheet = Spritesheet(get_image(name + ".png"))
        self.sprites = Animation([self.spritesheet.get_sprite(*sprite) for sprite in sprites], frame_duration)

    def draw(self, screen, dt):
        sprite = self.sprites.get_frame(dt)
        screen.blit(sprite, (self.pos))

tp_intro = Object("TP_Intro", pygame.Vector2(530, 16), sprites = [(0,0,184,101)])

#####################################################################################
class Game():
    def __init__(self):
        self.stage = 0
        self.new_stage = False
        self.loading_speed = 20
        self.loading_bar = ProgressBar(max_hp=1000, size=950, pos=pygame.Vector2(get_mid_screen(screen).x, screen.get_height()-120))
        self.loading_bar.hp = 0
        self.debug_on = False
        self.debug_button_pressed = False
        self.softlock_timer = 0
        #self.manual_dialog_control_on = False

    def update(self, screen, dt):
        self.keys()

        for event in pygame.event.get():
            self.handle_quit(event)
            self.handle_mouse(event)

        cat.update(screen, dt)
        cat.talk(self.stage, screen)
        mouse.update(dt)
        music.update(dt)
        for dot in dots:
            dot.move(dt)

        self.stage_logic(screen, dt)
            

        self.debug()



    def stage_logic(self, screen, dt): 
        global running

        ############################ New stage actions ############################
        if self.new_stage:
            self.new_stage = False

            if self.stage != GameStage.Chase.value or cat.hp <= 1:
                if self.stage != GameStage.SoftLock_Intro.value:
                    winsound.MessageBeep(winsound.MB_ICONHAND)
                self.stage += 1

                if self.stage == GameStage.Button_Vanish.value:
                    screen = pygame.display.set_mode((1080, 720), pygame.NOFRAME)
                    window.position = ((window_size[0]//2 - screen.get_width()//2), (window_size[1]//2 - screen.get_height()//2))
                    close_button.pos = pygame.Vector2(300, 500)

                if self.stage == GameStage.Button_Move2.value:
                    close_button.x_speed *= 2
                    close_button.y_speed *= 2

                if self.stage == GameStage.HP_Intro.value:
                    cat.dialogue_route = "1"
                    close_button.pos = pygame.Vector2(screen.get_width()-170, screen.get_height()-150)
                    if close_button.pos.distance_to(mouse.pos) < 400:
                        close_button.pos = pygame.Vector2(170, 150)
                    cat.pos = pygame.Vector2(0, 0) + close_button.pos
                    cat.direction = turn_to(cat.pos, mouse.pos)
                    cat.pos += cat.direction*70
                    cat.transparency = 0
                    cat.appear(dt)
                elif self.stage == GameStage.HP_Intro.value + 1:
                    cat.dialogue_route = None
                    cat.darkened = False

                if self.stage == GameStage.TP_Intro.value:
                    close_button.pos = pygame.Vector2(get_mid_screen(screen)) + pygame.Vector2(-20, -50)
                    cat.dialogue_route = "1"
                elif self.stage == GameStage.TP_Intro.value + 1:
                    cat.dialogue_route = None

                if self.stage == GameStage.Pre_Chase.value:
                    cat.stamina_regen = 180 
                    close_button.pos = pygame.Vector2(screen.get_width()/2, screen.get_height()-100)
                    cat.pos = pygame.Vector2(20, -50) + close_button.pos
                    if close_button.pos.distance_to(mouse.pos) < 300:
                        close_button.pos = pygame.Vector2(screen.get_width()/2, 100)
                        cat.pos = pygame.Vector2(20, 70) + close_button.pos
                    

                if self.stage == GameStage.Chase.value:
                    cat.stamina_regen = 3.8
                    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
                    cat.pos = teleport_from_mouse(700,screen)
                    music.play()

                if self.stage == GameStage.Close.value:
                    running = False
        #############################################################################
        
        if self.stage == GameStage.SoftLock_Intro.value:
            screen.blit(get_image("SoftLock.png"), (0, 0))
            self.softlock_timer += dt
            if self.softlock_timer >= 4:
                screen.blit(get_image("SoftLock_2.png"), (0, 0))

        if self.stage == GameStage.Loading.value:
            screen.blit(get_image("Loading.png"), (0, 0))   
            self.loading_screen()  

        if self.stage >= GameStage.Button_Move.value and self.stage <= GameStage.Button_Move2.value:
            close_button.move(dt)

        if self.stage == GameStage.HP_Intro.value:
            if close_button.just_teleported:
                if cat.dialogue_route == "1":
                    cat.dialogue_route = "2"
                #dialogues = cat.dialogue_lines[str(self.stage)][str(cat.dialogue_route)]
                #if dialogues.lines[dialogues.current_line] == "":

        if self.stage == GameStage.TP_Intro.value:
            if cat.stamina < 100:
                tp_intro.draw(screen, dt)
            if close_button.just_teleported:
                if cat.dialogue_route == "1":
                    cat.dialogue_route = "2"
                dialogues = cat.dialogue_lines[str(self.stage)][str(cat.dialogue_route)]
                if dialogues.lines[dialogues.current_line] == "WHAT IS THIS?":
                    cat.dialogue_route = "3"
            

            

        if self.stage >= GameStage.Button_Vanish.value:
            close_button.update(screen, self.stage, dt)



    def handle_mouse(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.stage == GameStage.SoftLock_Intro.value and self.softlock_timer >= 4:
                self.new_stage = True
            close_button.click(event)
        if event.type == pygame.MOUSEBUTTONUP:
            close_button.unclick(event, self)

    def handle_quit(self, event):
        # pygame.QUIT event means the user clicked X
        global quick_quit
        global running 
        if event.type == pygame.QUIT:
            if game.stage == GameStage.SoftLock_Intro.value:
                quick_quit = True
                running = False
            else:
                mouse.state = "default"
                self.new_stage = True


    def keys(self):
        global quick_quit
        global running
        keys = pygame.key.get_pressed()
        if keys[pygame.K_ESCAPE] and (keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]):
            quick_quit = True
            running = False

        if keys[pygame.K_7] and keys[pygame.K_5]:
            #self.debug_on = True
            pass
        else:
            self.debug_on = False

        if self.debug_on:
            if keys[pygame.K_SPACE]:
                if self.stage < GameStage.Chase.value:
                    self.stage = GameStage.Chase.value
                    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
                    cat.pos = teleport_from_mouse(700,screen)
                    music.play()
        if self.debug_on:
            if keys[pygame.K_RIGHT]:
                if not self.debug_button_pressed:
                    self.debug_button_pressed = True
                    pygame.event.post(pygame.event.Event(pygame.QUIT))
                    close_button.laggy_move = False
                    if game.stage >= GameStage.Chase.value:
                        cat.damage()
            else:
                self.debug_button_pressed = False
                

    def loading_screen(self):
        self.loading_bar.hp += self.loading_speed * dt
        if self.loading_bar.hp >= 900 and self.loading_bar.hp - self.loading_speed * dt < 900:
            self.loading_bar.hp = 900
        if self.loading_bar.hp < 900:
            if random.random()*500 < self.loading_speed:
                self.loading_speed = random.random()*700 + 1
        elif self.loading_bar.hp < 903:
            self.loading_speed = 0.5
        else:
            self.loading_speed = 0
            mouse.state = "WAITARROW"
        self.loading_bar.update(self.loading_bar.hp)
        self.loading_bar.draw(screen, dt)

    def debug(self):
        if self.debug_on:
            #debug##
            print(self.stage)
            for dot in dots:
                dot.draw(screen)
            pygame.draw.circle(screen, "red", cat.pos, cat.hitbox_radius)

    def debug_event_check():
        global screen
        global game
        if game.debug_on:
            screen.blit(get_image("debug_event.png"), pygame.Vector2(0, 0))

game = Game()



###############################################################################################################################


while running:
    # fill the screen with a color to wipe away anything from last frame
    screen.fill(background_color)

    
    game.update(screen, dt)



    # flip() the display to put your work on screen
    pygame.display.flip()


    # limits FPS to 60.      dt is delta time in seconds since last frame, used for framerate-independent physics.
    dt = clock.tick(60) / 1000

if not quick_quit:
    pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_WAITARROW)
    pygame.mixer.stop()
    play_sound("Kill Cat.wav")
    time.sleep(1)
pygame.quit()
