#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat May  9 10:30:25 2026

@author: linhengan
"""

import pygame
import sys
import random

black = (0, 0, 0)
white = (255, 255, 255)
blue = (0, 0, 255)
green = (0, 255, 0)
red = (255, 0, 0)
purple = (255, 0, 255)
yellow = (255, 255, 0)
orange = (255, 165, 0) # 橘色給無敵星星
cyan = (0, 255, 255)   # 青色給冰凍道具

# 設定鬼魂數量上限
MAX_GHOSTS = 8

try:
    Trollicon = pygame.image.load('images/Trollman.png')
    pygame.display.set_icon(Trollicon)
except pygame.error:
    pass 

# Add music
pygame.mixer.init()
try:
    pygame.mixer.music.load('pacman.mp3')
    pygame.mixer.music.play(-1, 0.0)
except pygame.error:
    pass 

class Wall(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, color):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface([width, height])
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.top = y
        self.rect.left = x

def setupRoomOne(all_sprites_list):
    wall_list = pygame.sprite.Group()
    walls = [
        [0, 0, 6, 600],
        [0, 0, 600, 6],
        [0, 600, 606, 6],
        [600, 0, 6, 606],
        [300, 0, 6, 66],
        [60, 60, 186, 6],
        [360, 60, 186, 6],
        [60, 120, 66, 6],
        [60, 120, 6, 126],
        [180, 120, 246, 6],
        [300, 120, 6, 66],
        [480, 120, 66, 6],
        [540, 120, 6, 126],
        [120, 180, 126, 6],
        [120, 180, 6, 126],
        [360, 180, 126, 6],
        [480, 180, 6, 126],
        [180, 240, 6, 126],
        [180, 360, 246, 6],
        [420, 240, 6, 126],
        [240, 240, 42, 6],
        [324, 240, 42, 6],
        [240, 240, 6, 66],
        [240, 300, 126, 6],
        [360, 240, 6, 66],
        [0, 300, 66, 6],
        [540, 300, 66, 6],
        [60, 360, 66, 6],
        [60, 360, 6, 186],
        [480, 360, 66, 6],
        [540, 360, 6, 186],
        [120, 420, 366, 6],
        [120, 420, 6, 66],
        [480, 420, 6, 66],
        [180, 480, 246, 6],
        [300, 480, 6, 66],
        [120, 540, 126, 6],
        [360, 540, 126, 6]
    ]
    for item in walls:
        wall = Wall(item[0], item[1], item[2], item[3], blue)
        wall_list.add(wall)
        all_sprites_list.add(wall)
    return wall_list

def setupGate(all_sprites_list):
    gate = pygame.sprite.Group()
    gate.add(Wall(282, 242, 42, 2, white))
    all_sprites_list.add(gate)
    return gate

class Block(pygame.sprite.Sprite):
    def __init__(self, color, width, height):
        pygame.sprite.Sprite.__init__(self) 
        self.image = pygame.Surface([width, height])
        self.image.fill(white)
        self.image.set_colorkey(white)
        pygame.draw.ellipse(self.image, color, [0, 0, width, height])
        self.rect = self.image.get_rect()

class PowerUp(pygame.sprite.Sprite):
    def __init__(self, color, width, height, power_type):
        pygame.sprite.Sprite.__init__(self) 
        self.image = pygame.Surface([width, height])
        self.image.fill(white)
        self.image.set_colorkey(white)
        pygame.draw.ellipse(self.image, color, [0, 0, width, height])
        self.rect = self.image.get_rect() 
        self.type = power_type 

class Player(pygame.sprite.Sprite):
    change_x = 0
    change_y = 0
    def __init__(self, x, y, filename):
        pygame.sprite.Sprite.__init__(self)
        try:
            self.image = pygame.image.load(filename).convert()
        except pygame.error:
            self.image = pygame.Surface([30, 30])
            self.image.fill(yellow)
        self.rect = self.image.get_rect()
        self.rect.top = y
        self.rect.left = x
        self.prev_x = x
        self.prev_y = y

    def prevdirection(self):
        self.prev_x = self.change_x
        self.prev_y = self.change_y

    def changespeed(self, x, y):
        self.change_x += x
        self.change_y += y
          
    def update(self, walls, gate):
        old_x = self.rect.left
        new_x = old_x + self.change_x
        self.rect.left = new_x
        
        old_y = self.rect.top
        new_y = old_y + self.change_y

        x_collide = pygame.sprite.spritecollide(self, walls, False)
        if x_collide:
            self.rect.left = old_x
        else:
            self.rect.top = new_y
            y_collide = pygame.sprite.spritecollide(self, walls, False)
            if y_collide:
                self.rect.top = old_y

        if gate != False:
            gate_hit = pygame.sprite.spritecollide(self, gate, False)
            if gate_hit:
                self.rect.left = old_x
                self.rect.top = old_y

class Ghost(Player):
    def __init__(self, x, y, filename):
        super().__init__(x, y, filename)
        self.steps_taken = 0
        dirs = [(15, 0), (-15, 0), (0, 15), (0, -15)]
        self.change_x, self.change_y = random.choice(dirs)

    def update(self, walls, gate=False, is_frozen=False):
        if is_frozen:
            return 
        old_x = self.rect.left
        old_y = self.rect.top
        self.rect.left += self.change_x
        self.rect.top += self.change_y

        collide = pygame.sprite.spritecollide(self, walls, False)
        if gate:
            collide_gate = pygame.sprite.spritecollide(self, gate, False)
            if collide_gate:
                collide.extend(collide_gate)

        self.steps_taken += 1

        if collide or self.steps_taken > random.randint(15, 60):
            if collide:
                self.rect.left = old_x
                self.rect.top = old_y

            dirs = [(15, 0), (-15, 0), (0, 15), (0, -15)]
            random.shuffle(dirs) 
            
            for dx, dy in dirs:
                self.rect.left = old_x + dx
                self.rect.top = old_y + dy
                if not pygame.sprite.spritecollide(self, walls, False) and not (gate and pygame.sprite.spritecollide(self, gate, False)):
                    self.change_x = dx
                    self.change_y = dy
                    self.steps_taken = 0
                    self.rect.left = old_x
                    self.rect.top = old_y
                    break
            else:
                self.rect.left = old_x
                self.rect.top = old_y

pygame.init()
screen = pygame.display.set_mode([606, 606])
pygame.display.set_caption('Pacman')
background = pygame.Surface(screen.get_size()).convert()
background.fill(black)
clock = pygame.time.Clock()

pygame.font.init()
try:
    font = pygame.font.Font("freesansbold.ttf", 24)
except OSError:
    font = pygame.font.Font(None, 24)

w = 303 - 16 
p_h = (7 * 60) + 19 

def startGame():
    all_sprites_list = pygame.sprite.Group()
    block_list = pygame.sprite.Group()
    powerup_list = pygame.sprite.Group()
    monsta_list = pygame.sprite.Group()
    pacman_collide = pygame.sprite.Group()

    wall_list = setupRoomOne(all_sprites_list)
    gate = setupGate(all_sprites_list)

    Pacman = Player(w, p_h, "images/Trollman.png")
    all_sprites_list.add(Pacman)
    pacman_collide.add(Pacman)

    valid_spawn_points = []

    for row in range(19):
        for column in range(19):
            if (row == 7 or row == 8) and (column == 8 or column == 9 or column == 10):
                continue
            else:
                block = Block(yellow, 4, 4)
                block.rect.x = (30 * column + 6) + 26
                block.rect.y = (30 * row + 6) + 26

                b_collide = pygame.sprite.spritecollide(block, wall_list, False)
                p_collide = pygame.sprite.spritecollide(block, pacman_collide, False)
                if b_collide or p_collide:
                    continue
                else:
                    block_list.add(block)
                    all_sprites_list.add(block)
                    
                    ghost_x = block.rect.x - 13
                    ghost_y = block.rect.y - 13
                    if abs(ghost_x - w) > 100 or abs(ghost_y - p_h) > 100:
                        valid_spawn_points.append((ghost_x, ghost_y))

    # 開局預設先生成 2 個道具，讓玩家一開始有目標
    if len(block_list) >= 2:
        blocks_to_replace = random.sample(list(block_list), 2)
        for i, b in enumerate(blocks_to_replace):
            block_list.remove(b)      
            all_sprites_list.remove(b)
            ptype = 'star' if i == 0 else 'ice'
            pcolor = orange if ptype == 'star' else cyan
            powerup = PowerUp(pcolor, 14, 14, ptype)
            powerup.rect.center = b.rect.center      
            powerup_list.add(powerup)
            all_sprites_list.add(powerup)

    random.shuffle(valid_spawn_points)
    spawns = valid_spawn_points[:4]
     
    Blinky = Ghost(spawns[0][0], spawns[0][1], "images/Blinky.png")
    Pinky = Ghost(spawns[1][0], spawns[1][1], "images/Pinky.png")
    Inky = Ghost(spawns[2][0], spawns[2][1], "images/Inky.png")
    Clyde = Ghost(spawns[3][0], spawns[3][1], "images/Clyde.png")
    
    for ghost in [Blinky, Pinky, Inky, Clyde]:
        monsta_list.add(ghost)
        all_sprites_list.add(ghost)

    score = 0
    done = False
    
    # 定義事件與計時器
    ADD_GHOST_EVENT = pygame.USEREVENT + 1
    pygame.time.set_timer(ADD_GHOST_EVENT, 15000) # 每 15 秒增加一隻鬼魂
    
    ADD_POWERUP_EVENT = pygame.USEREVENT + 2
    pygame.time.set_timer(ADD_POWERUP_EVENT, 8000) # 每 8 秒嘗試生成一個新道具
    
    ghost_images = ["images/Blinky.png", "images/Pinky.png", "images/Inky.png", "images/Clyde.png"]

    is_invincible = False
    invincible_timer = 0
    is_frozen = False
    frozen_timer = 0
    POWER_DURATION = 5000 

    while not done:
        current_time = pygame.time.get_ticks()

        if is_invincible and (current_time - invincible_timer > POWER_DURATION):
            is_invincible = False
        if is_frozen and (current_time - frozen_timer > POWER_DURATION):
            is_frozen = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
                
            if event.type == ADD_GHOST_EVENT:
                if len(monsta_list) < MAX_GHOSTS:
                    safe_points = []
                    for pt in valid_spawn_points:
                        dist_x = abs(pt[0] - Pacman.rect.left)
                        dist_y = abs(pt[1] - Pacman.rect.top)
                        if dist_x > 100 or dist_y > 100:
                            safe_points.append(pt)
                    
                    if safe_points:
                        spawn_pt = random.choice(safe_points)
                        img = random.choice(ghost_images)
                        new_ghost = Ghost(spawn_pt[0], spawn_pt[1], img)
                        monsta_list.add(new_ghost)
                        all_sprites_list.add(new_ghost)

            # 新增：動態生成道具邏輯
            if event.type == ADD_POWERUP_EVENT:
                # 確保畫面上道具不超過 5 個，且還有普通豆子可以替換
                if len(powerup_list) < 5 and len(block_list) > 0:
                    target_block = random.choice(block_list.sprites())
                    
                    # 隨機決定道具種類
                    ptype = random.choice(['star', 'ice'])
                    pcolor = orange if ptype == 'star' else cyan
                    
                    new_powerup = PowerUp(pcolor, 14, 14, ptype)
                    new_powerup.rect.center = target_block.rect.center
                    
                    # 進行替換
                    block_list.remove(target_block)
                    all_sprites_list.remove(target_block)
                    powerup_list.add(new_powerup)
                    all_sprites_list.add(new_powerup)

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    Pacman.changespeed(-30, 0)
                if event.key == pygame.K_RIGHT:
                    Pacman.changespeed(30, 0)
                if event.key == pygame.K_UP:
                    Pacman.changespeed(0, -30)
                if event.key == pygame.K_DOWN:
                    Pacman.changespeed(0, 30)

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT:
                    Pacman.changespeed(30, 0)
                if event.key == pygame.K_RIGHT:
                    Pacman.changespeed(-30, 0)
                if event.key == pygame.K_UP:
                    Pacman.changespeed(0, 30)
                if event.key == pygame.K_DOWN:
                    Pacman.changespeed(0, -30)
            
        Pacman.update(wall_list, gate)

        for monsta in monsta_list:
            monsta.update(wall_list, False, is_frozen)

        blocks_hit_list = pygame.sprite.spritecollide(Pacman, block_list, True)
        if len(blocks_hit_list) > 0:
            score += len(blocks_hit_list)

        powerups_hit_list = pygame.sprite.spritecollide(Pacman, powerup_list, True)
        for powerup in powerups_hit_list:
            if powerup.type == 'star':
                is_invincible = True
                invincible_timer = pygame.time.get_ticks() 
            elif powerup.type == 'ice':
                is_frozen = True
                frozen_timer = pygame.time.get_ticks() 

        screen.fill(black)
          
        wall_list.draw(screen)
        gate.draw(screen)
        all_sprites_list.draw(screen)
        monsta_list.draw(screen)

        text = font.render("Score: " + str(score), True, red)
        screen.blit(text, [10, 10])

        status_msg = ""
        if is_invincible:
            status_msg += "INVINCIBLE! "
        if is_frozen:
            status_msg += "FROZEN! "
        if status_msg:
            status_text = font.render(status_msg, True, yellow)
            screen.blit(status_text, [300, 10])

        if len(block_list) == 0 and len(powerup_list) == 0:
            pygame.time.set_timer(ADD_GHOST_EVENT, 0)
            pygame.time.set_timer(ADD_POWERUP_EVENT, 0)
            doNext("Congratulations, you won!", 145, all_sprites_list, block_list, monsta_list, pacman_collide, wall_list, gate)

        monsta_hit_list = pygame.sprite.spritecollide(Pacman, monsta_list, False)
        if monsta_hit_list:
            if is_invincible:
                for m in monsta_hit_list:
                    m.kill()
                    score += 50
            else:
                pygame.time.set_timer(ADD_GHOST_EVENT, 0) 
                pygame.time.set_timer(ADD_POWERUP_EVENT, 0)
                doNext("Game Over", 235, all_sprites_list, block_list, monsta_list, pacman_collide, wall_list, gate)

        pygame.display.flip()
        clock.tick(10)

def doNext(message, left, all_sprites_list, block_list, monsta_list, pacman_collide, wall_list, gate):
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                if event.key == pygame.K_RETURN:
                    startGame()
                    return 

        w = pygame.Surface((400, 200)) 
        w.set_alpha(10)                
        w.fill((128, 128, 128))           
        screen.blit(w, (100, 200))    

        text1 = font.render(message, True, white)
        screen.blit(text1, [left, 233])

        text2 = font.render("To play again, press ENTER.", True, white)
        screen.blit(text2, [135, 303])
        text3 = font.render("To quit, press ESCAPE.", True, white)
        screen.blit(text3, [165, 333])

        pygame.display.flip()
        clock.tick(10)

startGame()
pygame.quit()