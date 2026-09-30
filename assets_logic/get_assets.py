import sys
import os
import pygame
#################################### Get assets ####################################
def _resource_path(relative_path):
    try:
        base_path = sys._MEIPASS  # папка PyInstaller
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

_image_library = {}
def get_image(path):
    global _image_library
    path = "Assets/" + path
    image = _image_library.get(path)
    if image == None:
        canonicalized_path = path.replace('/', os.sep)
        try:
            image = pygame.image.load(_resource_path(canonicalized_path))
        except:
            print("image", path, "not found")
            placeholder_path = "Assets/Missing_texture.png"
            canonicalized_path = placeholder_path.replace('/', os.sep)
            image = pygame.image.load(_resource_path(canonicalized_path))
        _image_library[path] = image


    return image
        

_sound_library = {}
def play_sound(path, volume=1.0, loops=0):
    try:
        global _sound_library
        path = "Assets/" + path
        sound = _sound_library.get(path)

        if sound == None:
        
            canonicalized_path = path.replace('/', os.sep)
            sound = pygame.mixer.Sound(_resource_path(canonicalized_path))
            sound.set_volume(volume/5)
            _sound_library[path] = sound
        channel = sound.play(loops)
        return channel
    except:
        print("sound", path, "not found")