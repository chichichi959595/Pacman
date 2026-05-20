import pygame
import sys
import random
from pathlib import Path

# --- 顏色設定 ---
black = (0,0,0)
white = (255,255,255)
blue = (0,0,255)
green = (0,255,0)
red = (255,0,0)
purple = (255,0,255)
yellow = (255, 255, 0)
orange = (255, 165, 0)
cyan = (0, 255, 255)

MAX_GHOSTS = 8
POWER_DURATION = 50 # 50 frames at 10 FPS, about 5 seconds
ROOT = Path(__file__).resolve().parent

# --- 基礎初始化 ---
pygame.init()
try:
    pygame.mixer.init()
except pygame.error as exc:
    print(f"Audio disabled: {exc}")
screen = pygame.display.set_mode([606, 606])
pygame.display.set_caption('Pacman - Bomb & Powerups')
clock = pygame.time.Clock()

def asset_path(*parts):
    return str(ROOT.joinpath(*parts))

def load_sound(*parts):
    if not pygame.mixer.get_init():
        return None
    path = asset_path(*parts)
    try:
        return pygame.mixer.Sound(path)
    except (pygame.error, FileNotFoundError) as exc:
        print(f"Could not load sound {path}: {exc}")
        return None

# --- 資源載入 (包含原始炸彈音效) ---
bomb_sound = load_sound('sounds', 'bomb_sound.mp3')
sfx_powerup = load_sound('sounds', 'powerup.wav')
sfx_freeze = load_sound('sounds', 'freeze.wav')
sfx_eat = load_sound('sounds', 'eat_ghost.wav')
if pygame.mixer.get_init():
    music_path = asset_path('sounds', 'pacman.mp3')
    try:
        pygame.mixer.music.load(music_path)
        pygame.mixer.music.play(-1, 0.0)
    except (pygame.error, FileNotFoundError) as exc:
        print(f"Could not load music {music_path}: {exc}")

# --- 爆炸視覺素材 ---
try:
    _expl_center = pygame.transform.scale(pygame.image.load(asset_path('images', 'explosion_center.png')).convert_alpha(), (30, 30))
    _expl_mid    = pygame.transform.scale(pygame.image.load(asset_path('images', 'explosion_mid.png')).convert_alpha(), (30, 30))
    _expl_end    = pygame.transform.scale(pygame.image.load(asset_path('images', 'explosion_end.png')).convert_alpha(), (30, 30))
except (pygame.error, FileNotFoundError) as exc:
    print(f"Could not load explosion images: {exc}")
    _expl_center = _expl_mid = _expl_end = None

# --- 類別定義 ---

class Bomb(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.timer = 50 
        self.exploded = False
        try:
            self._img_normal = pygame.transform.scale(pygame.image.load(asset_path('images', 'bomb.png')).convert_alpha(), (30, 30))
            self._img_flash  = pygame.transform.scale(pygame.image.load(asset_path('images', 'bomb_flash.png')).convert_alpha(), (30, 30))
        except (pygame.error, FileNotFoundError) as exc:
            print(f"Could not load bomb images: {exc}")
            self._img_normal = pygame.Surface([30, 30]); self._img_normal.fill((80,80,80))
            self._img_flash = pygame.Surface([30, 30]); self._img_flash.fill(red)
        self.image = self._img_normal
        self.rect = self.image.get_rect(topleft=(x, y))

    def update(self, wall_list):
        if self.timer > 0:
            self.timer -= 1
            if self.timer < 10:
                self.image = self._img_flash if (self.timer // 3) % 2 == 0 else self._img_normal
        else:
            self.exploded = True

    def get_explosion_cells(self, wall_list):
        cells = []
        cx, cy, cell = self.rect.left, self.rect.top, 30
        cells.append((pygame.Rect(cx, cy, cell, cell), 'center', 0))
        for rot, dx, dy in [(0, 1, 0), (180, -1, 0), (-90, 0, 1), (90, 0, -1)]:
            for step in range(1, 21):
                r = pygame.Rect(cx + dx*cell*step, cy + dy*cell*step, cell, cell)
                if not screen.get_rect().contains(r) or any(r.colliderect(w.rect) for w in wall_list):
                    break
                cells.append((r, 'mid', rot))
        return cells

class PowerUp(pygame.sprite.Sprite):
    def __init__(self, x, y, p_type):
        super().__init__()
        self.type = p_type
        try:
            img_file = asset_path('images', 'star.png') if p_type == 'star' else asset_path('images', 'ice.png')
            self.image = pygame.transform.scale(pygame.image.load(img_file).convert_alpha(), (25, 25))
        except (pygame.error, FileNotFoundError) as exc:
            print(f"Could not load power-up image: {exc}")
            self.image = pygame.Surface([20, 20])
            self.image.fill(orange if p_type == 'star' else cyan)
        self.rect = self.image.get_rect(center=(x, y))

class Wall(pygame.sprite.Sprite):
    def __init__(self,x,y,width,height, color):
        super().__init__()
        self.image = pygame.Surface([width, height]); self.image.fill(color)
        self.rect = self.image.get_rect(topleft=(x, y))

class Block(pygame.sprite.Sprite):
    def __init__(self, color, width, height):
        super().__init__() 
        self.image = pygame.Surface([width, height], pygame.SRCALPHA)
        pygame.draw.ellipse(self.image, color, [0,0,width,height])
        self.rect = self.image.get_rect()

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, filename):
        super().__init__()
        self.bomb_count = 3
        try:
            self.image_normal = pygame.image.load(asset_path(filename)).convert_alpha()
            self.image_normal = pygame.transform.scale(self.image_normal, (30, 30))
        except (pygame.error, FileNotFoundError) as exc:
            print(f"Could not load player image {filename}: {exc}")
            self.image_normal = pygame.Surface([30, 30]); self.image_normal.fill(yellow)
        self.image = self.image_normal
        self.rect = self.image.get_rect(topleft=(x, y))
        self.change_x = self.change_y = 0

    def changespeed(self, x, y):
        self.change_x += x; self.change_y += y

    def update(self, walls, gate, invincible=False):
        if invincible and (pygame.time.get_ticks() // 200) % 2 == 0:
            self.image = pygame.Surface([30, 30]); self.image.fill(orange)
        else:
            self.image = self.image_normal
        
        old_x, old_y = self.rect.topleft
        self.rect.left += self.change_x
        if pygame.sprite.spritecollide(self, walls, False) or (gate and pygame.sprite.spritecollide(self, gate, False)):
            self.rect.left = old_x
        self.rect.top += self.change_y
        if pygame.sprite.spritecollide(self, walls, False) or (gate and pygame.sprite.spritecollide(self, gate, False)):
            self.rect.top = old_y

class Ghost(Player):
    def __init__(self, x, y, filename):
        super().__init__(x, y, filename)
        self.change_x, self.change_y = 15, 0
        self.steps = 0

    def update(self, walls, gate, frozen=False):
        if frozen: return 
        old_x, old_y = self.rect.topleft
        self.rect.left += self.change_x; self.rect.top += self.change_y
        self.steps += 1
        hit_wall = pygame.sprite.spritecollide(self, walls, False)
        hit_gate = gate and pygame.sprite.spritecollide(self, gate, False)
        if hit_wall or hit_gate or self.steps > random.randint(15, 60):
            self.rect.topleft = (old_x, old_y)
            dirs = [(15,0), (-15,0), (0,15), (0,-15)]
            random.shuffle(dirs)
            for dx, dy in dirs:
                self.rect.left, self.rect.top = old_x + dx, old_y + dy
                blocked = pygame.sprite.spritecollide(self, walls, False) or (gate and pygame.sprite.spritecollide(self, gate, False))
                if not blocked:
                    self.change_x, self.change_y, self.steps = dx, dy, 0
                    self.rect.topleft = (old_x, old_y)
                    break
            else:
                self.rect.topleft = (old_x, old_y)

# --- 地圖建置 ---
def setupRoomOne(all_sprites):
    wall_list = pygame.sprite.Group()
    walls = [[0,0,6,600],[0,0,600,6],[0,600,606,6],[600,0,6,606],[300,0,6,66],[60,60,186,6],[360,60,186,6],[60,120,66,6],[60,120,6,126],[180,120,246,6],[300,120,6,66],[480,120,66,6],[540,120,6,126],[120,180,126,6],[120,180,6,126],[360,180,126,6],[480,180,6,126],[180,240,6,126],[180,360,246,6],[420,240,6,126],[240,240,42,6],[324,240,42,6],[240,240,6,66],[240,300,126,6],[360,240,6,66],[0,300,66,6],[540,300,66,6],[60,360,66,6],[60,360,6,186],[480,360,66,6],[540,360,6,186],[120,420,366,6],[120,420,6,66],[480,420,6,66],[180,480,246,6],[300,480,6,66],[120,540,126,6],[360,540,126,6]]
    for i in walls:
        w = Wall(i[0],i[1],i[2],i[3],blue)
        wall_list.add(w); all_sprites.add(w)
    return wall_list

def doNext(message, left, all_sprites_list, block_list, monsta_list, wall_list, gate, total_blocks, score):
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
                    return True

        # Grey background
        w = pygame.Surface((400, 200))
        w.set_alpha(10)
        w.fill((128, 128, 128))
        screen.blit(w, (100, 200))

        # Won or lost
        font_big = pygame.font.Font(None, 36)
        text1 = font_big.render(message, True, white)
        text1_rect = text1.get_rect(center=(300, 245))
        screen.blit(text1, text1_rect)

        text2 = font_big.render("To play again, press ENTER.", True, white)
        text2_rect = text2.get_rect(center=(300, 290))
        screen.blit(text2, text2_rect)
        text3 = font_big.render("To quit, press ESCAPE.", True, white)
        text3_rect = text3.get_rect(center=(300, 335))
        screen.blit(text3, text3_rect)

        pygame.display.flip()
        clock.tick(10)

def startGame():
    all_sprites = pygame.sprite.Group()
    block_list = pygame.sprite.Group()
    monsta_list = pygame.sprite.Group()
    bomb_list = pygame.sprite.Group()
    power_list = pygame.sprite.Group()
    
    wall_list = setupRoomOne(all_sprites)
    gate = pygame.sprite.Group()
    gate.add(Wall(282,242,42,2,white))
    all_sprites.add(gate)
    Pacman = Player(287, 439, "images/Trollman.png"); all_sprites.add(Pacman)
    
    valid_points = []
    for r in range(19):
        for c in range(19):
            if (r == 7 or r == 8) and (8 <= c <= 10): continue
            b = Block(yellow, 4, 4); b.rect.x = (30*c+32); b.rect.y = (30*r+32)
            if not pygame.sprite.spritecollide(b, wall_list, False):
                block_list.add(b); all_sprites.add(b)
                valid_points.append(b.rect.center)

    ghost_imgs = ["images/Blinky.png", "images/Pinky.png", "images/Inky.png", "images/Clyde.png"]
    def point_is_far_from_player(point, distance=100):
        return abs(point[0] - Pacman.rect.centerx) > distance or abs(point[1] - Pacman.rect.centery) > distance

    ghost_points = [pt for pt in valid_points if point_is_far_from_player(pt)] or valid_points[:]
    random.shuffle(ghost_points)
    for i in range(min(4, len(ghost_points))):
        pt = ghost_points[i]
        # 调整初始位置计算，避免偏差
        ghost_x = pt[0] - 15
        ghost_y = pt[1] - 15
        g = Ghost(int(ghost_x), int(ghost_y), ghost_imgs[i]); monsta_list.add(g); all_sprites.add(g)

    ADD_GHOST = pygame.USEREVENT + 1; pygame.time.set_timer(ADD_GHOST, 15000)
    ADD_POWER = pygame.USEREVENT + 2; pygame.time.set_timer(ADD_POWER, 8000)

    total_blocks = len(block_list)
    score = 0; inv_timer = 0; froz_timer = 0
    active_explosions = []; space_held = False
    font = pygame.font.Font(None, 32)

    def finish_game(message):
        pygame.time.set_timer(ADD_GHOST, 0)
        pygame.time.set_timer(ADD_POWER, 0)
        return doNext(message, 0, all_sprites, block_list, monsta_list, wall_list, gate, total_blocks, score)

    def choose_power_block():
        candidates = []
        for block in block_list:
            if block.rect.colliderect(Pacman.rect):
                continue
            if any(block.rect.colliderect(ghost.rect) for ghost in monsta_list):
                continue
            candidates.append(block)
        return random.choice(candidates) if candidates else None

    def choose_ghost_point():
        candidates = []
        for point in valid_points:
            ghost_rect = pygame.Rect(point[0] - 15, point[1] - 15, 30, 30)
            if not point_is_far_from_player(point):
                continue
            if any(ghost_rect.colliderect(ghost.rect) for ghost in monsta_list):
                continue
            if any(ghost_rect.colliderect(power.rect) for power in power_list):
                continue
            candidates.append(point)
        return random.choice(candidates) if candidates else None

    while True:
        is_inv = inv_timer > 0; is_froz = froz_timer > 0
        if inv_timer > 0: inv_timer -= 1
        if froz_timer > 0: froz_timer -= 1

        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            if event.type == ADD_POWER and len(power_list) < 3:
                target_block = choose_power_block()
                if target_block:
                    pt = target_block.rect.center
                    target_block.kill()
                    p = PowerUp(pt[0], pt[1], random.choice(['star', 'ice']))
                    power_list.add(p); all_sprites.add(p)
            if event.type == ADD_GHOST and len(monsta_list) < MAX_GHOSTS:
                pt = choose_ghost_point()
                if pt:
                    g = Ghost(pt[0]-15, pt[1]-15, random.choice(ghost_imgs)); monsta_list.add(g); all_sprites.add(g)
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT: Pacman.changespeed(-30,0)
                if event.key == pygame.K_RIGHT: Pacman.changespeed(30,0)
                if event.key == pygame.K_UP: Pacman.changespeed(0,-30)
                if event.key == pygame.K_DOWN: Pacman.changespeed(0,30)
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT: Pacman.changespeed(30,0)
                if event.key == pygame.K_RIGHT: Pacman.changespeed(-30,0)
                if event.key == pygame.K_UP: Pacman.changespeed(0,30)
                if event.key == pygame.K_DOWN: Pacman.changespeed(0,-30)

        # 炸彈邏輯 (左 Ctrl)
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LCTRL] and not space_held and Pacman.bomb_count > 0:
            b = Bomb(Pacman.rect.left, Pacman.rect.top); bomb_list.add(b); all_sprites.add(b)
            Pacman.bomb_count -= 1; space_held = True
        if not keys[pygame.K_LCTRL]: space_held = False

        Pacman.update(wall_list, gate, is_inv)
        for g in monsta_list: g.update(wall_list, gate, is_froz)
        
        # 炸彈爆炸判定與音效
        for b in list(bomb_list):
            b.update(wall_list)
            if b.exploded:
                if bomb_sound: bomb_sound.play() # 炸彈音效在此播放
                cells = b.get_explosion_cells(wall_list)
                active_explosions.append((cells, 5))
                for r, _, _ in cells:
                    for g in list(monsta_list):
                        if g.rect.colliderect(r): g.kill(); score += 50
                    if Pacman.rect.colliderect(r) and not is_inv:
                        return finish_game("Game Over")
                b.kill()

        # 道具碰撞與音效
        p_hits = pygame.sprite.spritecollide(Pacman, power_list, True)
        score += len(p_hits)
        for p in p_hits:
            if sfx_powerup: sfx_powerup.play()
            if p.type == 'star': inv_timer = POWER_DURATION
            if p.type == 'ice': 
                froz_timer = POWER_DURATION
                if sfx_freeze: sfx_freeze.play()

        score += len(pygame.sprite.spritecollide(Pacman, block_list, True))
        
        # 鬼魂碰撞
        m_hits = pygame.sprite.spritecollide(Pacman, monsta_list, False)
        if m_hits:
            if is_inv:
                for m in m_hits: 
                    m.kill(); score += 100
                    if sfx_eat: sfx_eat.play()
            else:
                return finish_game("Game Over")

        if len(block_list) == 0 and len(power_list) == 0:
            return finish_game("Congratulations, you won!")

        # 繪製
        screen.fill(black)
        all_sprites.draw(screen)
        
        # DEBUG: 顯示碰撞框 (可視化調試)
        # pygame.draw.rect(screen, green, Pacman.rect, 2)  # Pacman碰撞框
        # for g in monsta_list: pygame.draw.rect(screen, red, g.rect, 2)  # Ghost碰撞框
        
        # 繪製爆炸效果
        for cells, frames in list(active_explosions):
            for r, ct, rot in cells:
                if ct == 'center' and _expl_center: screen.blit(_expl_center, r)
                elif ct == 'mid' and _expl_mid: screen.blit(pygame.transform.rotate(_expl_mid, rot), r)
                else: pygame.draw.rect(screen, (255, 200, 0), r)
            idx = active_explosions.index((cells, frames))
            if frames > 1: active_explosions[idx] = (cells, frames - 1)
            else: active_explosions.pop(idx)

        # 顯示文字
        pellets_left = len(block_list) + len(power_list)
        pellets_eaten = total_blocks - pellets_left
        s_text = font.render(f"Score: {score}  Pellets: {pellets_eaten}/{total_blocks}  Bombs: {Pacman.bomb_count}", True, red)
        screen.blit(s_text, [10, 10])
        if is_inv: screen.blit(font.render("INVINCIBLE!", True, orange), [250, 10])
        if is_froz: screen.blit(font.render("GHOSTS FROZEN!", True, cyan), [400, 10])
        
        pygame.display.flip()
        clock.tick(10)

if __name__ == "__main__":
    while True: startGame()
