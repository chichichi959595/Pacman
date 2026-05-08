#Pacman in Python with PyGame
#https://github.com/hbokmann/Pacman
  
import pygame
import sys
import random
  
black = (0,0,0)
white = (255,255,255)
blue = (0,0,255)
green = (0,255,0)
red = (255,0,0)
purple = (255,0,255)
yellow   = ( 255, 255,   0)

# 設定鬼魂數量上限
MAX_GHOSTS = 8

try:
    Trollicon=pygame.image.load('images/Trollman.png')
    pygame.display.set_icon(Trollicon)
except pygame.error:
    pass # 忽略找不到圖標的錯誤

#Add music
pygame.mixer.init()
try:
    pygame.mixer.music.load('sounds/pacman.mp3')
    pygame.mixer.music.play(-1, 0.0)
except pygame.error:
    pass # 忽略找不到音樂的錯誤

try:
    bomb_sound = pygame.mixer.Sound('sounds/bomb_sound.mp3')
except pygame.error:
    bomb_sound = None

class Bomb(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.timer = 50  # 倒數 50 幀（約 5 秒，FPS=10）
        self.exploded = False

        try:
            self._img_normal = pygame.transform.scale(pygame.image.load('images/bomb.png').convert_alpha(), (30, 30))
            self._img_flash  = pygame.transform.scale(pygame.image.load('images/bomb_flash.png').convert_alpha(), (30, 30))
        except pygame.error:
            self._img_normal = pygame.Surface([30, 30], pygame.SRCALPHA)
            pygame.draw.circle(self._img_normal, (80, 80, 80), (15, 15), 12)
            self._img_flash = pygame.Surface([30, 30], pygame.SRCALPHA)
            pygame.draw.circle(self._img_flash, red, (15, 15), 12)

        self.image = self._img_normal
        self.rect = self.image.get_rect()
        self.rect.left = x
        self.rect.top = y

    def update(self, wall_list):
        if self.timer > 0:
            self.timer -= 1
            if self.timer < 10:
                # 每 3 幀交替一次，產生閃爍效果
                self.image = self._img_flash if (self.timer // 3) % 2 == 0 else self._img_normal
        else:
            self.exploded = True

    def get_explosion_cells(self, wall_list):
        """回傳 [(rect, cell_type, rotation), ...]，供繪圖與碰撞判定共用。
        cell_type: 'center' | 'mid' | 'end'
        rotation: pygame.transform.rotate 的角度（以向右為 0°，逆時針為正）
        """
        cells = []
        cx, cy, cell = self.rect.left, self.rect.top, 30
        cells.append((pygame.Rect(cx, cy, cell, cell), 'center', 0))
        # (旋轉角度, dx, dy) — 向右=0°, 向左=180°, 向下=-90°, 向上=90°
        for rot, dx, dy in [(0, 1, 0), (180, -1, 0), (-90, 0, 1), (90, 0, -1)]:
            row = []
            for step in range(1, 21):  # 最多 20 格，足以橫跨整張地圖
                r = pygame.Rect(cx + dx*cell*step, cy + dy*cell*step, cell, cell)
                if not screen.get_rect().contains(r):
                    break
                if any(r.colliderect(w.rect) for w in wall_list):
                    break
                row.append(r)
            for i, r in enumerate(row):
                cells.append((r, 'end' if i == len(row) - 1 else 'mid', rot))
        return cells

# This class represents the bar at the bottom that the player controls
class Wall(pygame.sprite.Sprite):
    # Constructor function
    def __init__(self,x,y,width,height, color):
        # Call the parent's constructor
        pygame.sprite.Sprite.__init__(self)
  
        # Make a blue wall, of the size specified in the parameters
        self.image = pygame.Surface([width, height])
        self.image.fill(color)
  
        # Make our top-left corner the passed-in location.
        self.rect = self.image.get_rect()
        self.rect.top = y
        self.rect.left = x

# This creates all the walls in room 1
def setupRoomOne(all_sprites_list):
    # Make the walls. (x_pos, y_pos, width, height)
    wall_list=pygame.sprite.Group()
     
    # This is a list of walls. Each is in the form [x, y, width, height]
    walls = [ [0,0,6,600],
              [0,0,600,6],
              [0,600,606,6],
              [600,0,6,606],
              [300,0,6,66],
              [60,60,186,6],
              [360,60,186,6],
              [60,120,66,6],
              [60,120,6,126],
              [180,120,246,6],
              [300,120,6,66],
              [480,120,66,6],
              [540,120,6,126],
              [120,180,126,6],
              [120,180,6,126],
              [360,180,126,6],
              [480,180,6,126],
              [180,240,6,126],
              [180,360,246,6],
              [420,240,6,126],
              [240,240,42,6],
              [324,240,42,6],
              [240,240,6,66],
              [240,300,126,6],
              [360,240,6,66],
              [0,300,66,6],
              [540,300,66,6],
              [60,360,66,6],
              [60,360,6,186],
              [480,360,66,6],
              [540,360,6,186],
              [120,420,366,6],
              [120,420,6,66],
              [480,420,6,66],
              [180,480,246,6],
              [300,480,6,66],
              [120,540,126,6],
              [360,540,126,6]
            ]
     
    # Loop through the list. Create the wall, add it to the list
    for item in walls:
        wall=Wall(item[0],item[1],item[2],item[3],blue)
        wall_list.add(wall)
        all_sprites_list.add(wall)
         
    # return our new list
    return wall_list

def setupGate(all_sprites_list):
      gate = pygame.sprite.Group()
      gate.add(Wall(282,242,42,2,white))
      all_sprites_list.add(gate)
      return gate

# This class represents the ball        
# It derives from the "Sprite" class in Pygame
class Block(pygame.sprite.Sprite):
     
    # Constructor. Pass in the color of the block, 
    # and its x and y position
    def __init__(self, color, width, height):
        # Call the parent class (Sprite) constructor
        pygame.sprite.Sprite.__init__(self) 
 
        # Create an image of the block, and fill it with a color.
        # This could also be an image loaded from the disk.
        self.image = pygame.Surface([width, height])
        self.image.fill(white)
        self.image.set_colorkey(white)
        pygame.draw.ellipse(self.image,color,[0,0,width,height])
 
        # Fetch the rectangle object that has the dimensions of the image
        # image.
        # Update the position of this object by setting the values 
        # of rect.x and rect.y
        self.rect = self.image.get_rect() 

# This class represents the bar at the bottom that the player controls
class Player(pygame.sprite.Sprite):
  
    # Set speed vector
    change_x=0
    change_y=0
  
    # Constructor function
    def __init__(self,x,y, filename):
        # Call the parent's constructor
        pygame.sprite.Sprite.__init__(self)
        self.bomb_count = 3
   
        # Set height, width
        try:
            self.image = pygame.image.load(filename).convert()
        except pygame.error:
            # 支援現代化環境：若無圖片素材，改用黃色方塊代替
            self.image = pygame.Surface([30, 30])
            self.image.fill(yellow)
  
        # Make our top-left corner the passed-in location.
        self.rect = self.image.get_rect()
        self.rect.top = y
        self.rect.left = x
        self.prev_x = x
        self.prev_y = y

    # Clear the speed of the player
    def prevdirection(self):
        self.prev_x = self.change_x
        self.prev_y = self.change_y

    # Change the speed of the player
    def changespeed(self,x,y):
        self.change_x+=x
        self.change_y+=y
          
    # Find a new position for the player
    def update(self,walls,gate):
        # Get the old position, in case we need to go back to it
        
        old_x=self.rect.left
        new_x=old_x+self.change_x
        prev_x=old_x+self.prev_x
        self.rect.left = new_x
        
        old_y=self.rect.top
        new_y=old_y+self.change_y
        prev_y=old_y+self.prev_y

        # Did this update cause us to hit a wall?
        x_collide = pygame.sprite.spritecollide(self, walls, False)
        if x_collide:
            # Whoops, hit a wall. Go back to the old position
            self.rect.left=old_x
            # self.rect.top=prev_y
            # y_collide = pygame.sprite.spritecollide(self, walls, False)
            # if y_collide:
            #     # Whoops, hit a wall. Go back to the old position
            #     self.rect.top=old_y
            #     print('a')
        else:

            self.rect.top = new_y

            # Did this update cause us to hit a wall?
            y_collide = pygame.sprite.spritecollide(self, walls, False)
            if y_collide:
                # Whoops, hit a wall. Go back to the old position
                self.rect.top=old_y
                # self.rect.left=prev_x
                # x_collide = pygame.sprite.spritecollide(self, walls, False)
                # if x_collide:
                #     # Whoops, hit a wall. Go back to the old position
                #     self.rect.left=old_x
                #     print('b')

        if gate != False:
          gate_hit = pygame.sprite.spritecollide(self, gate, False)
          if gate_hit:
            self.rect.left=old_x
            self.rect.top=old_y

#Inheritime Player klassist
class Ghost(Player):
    def __init__(self, x, y, filename):
        super().__init__(x, y, filename)
        # 初始化時給予隨機初始方向與計步器
        self.steps_taken = 0
        dirs = [(15,0), (-15,0), (0,15), (0,-15)]
        self.change_x, self.change_y = random.choice(dirs)

    def update(self, walls, gate=False):
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

        # AI 隨機漫步邏輯：當碰到牆壁，或是走了一段距離後隨機轉彎，增加多變性
        if collide or self.steps_taken > random.randint(15, 60):
            if collide:
                # 碰到牆壁先復原位置
                self.rect.left = old_x
                self.rect.top = old_y

            # 尋找新的可走方向
            dirs = [(15,0), (-15,0), (0,15), (0,-15)]
            random.shuffle(dirs) # 隨機打亂方向測試順序
            
            for dx, dy in dirs:
                # 模擬移動一步來測試是否會撞牆
                self.rect.left = old_x + dx
                self.rect.top = old_y + dy
                if not pygame.sprite.spritecollide(self, walls, False) and not (gate and pygame.sprite.spritecollide(self, gate, False)):
                    # 找到可以走的路，更新方向
                    self.change_x = dx
                    self.change_y = dy
                    self.steps_taken = 0
                    self.rect.left = old_x
                    self.rect.top = old_y
                    break
            else:
                # 萬一四面楚歌卡死 (通常不會發生)，退回原位等下一幀
                self.rect.left = old_x
                self.rect.top = old_y

# Call this function so the Pygame library can initialize itself
pygame.init()
  
# Create an 606x606 sized screen
screen = pygame.display.set_mode([606, 606])

try:
    _expl_center = pygame.transform.scale(pygame.image.load('images/explosion_center.png').convert_alpha(), (30, 30))
    _expl_mid    = pygame.transform.scale(pygame.image.load('images/explosion_mid.png').convert_alpha(), (30, 30))
    _expl_end    = pygame.transform.scale(pygame.image.load('images/explosion_end.png').convert_alpha(), (30, 30))
except pygame.error:
    _expl_center = _expl_mid = _expl_end = None

# This is a list of 'sprites.' Each block in the program is
# added to this list. The list is managed by a class called 'RenderPlain.'


# Set the title of the window
pygame.display.set_caption('Pacman')

# Create a surface we can draw on
background = pygame.Surface(screen.get_size())

# Used for converting color maps and such
background = background.convert()
  
# Fill the screen with a black background
background.fill(black)

clock = pygame.time.Clock()

pygame.font.init()
try:
    font = pygame.font.Font("freesansbold.ttf", 24)
except OSError:
    # 如果找不到 freesansbold.ttf，自動退回使用系統預設字體
    font = pygame.font.Font(None, 24)

#default locations for Pacman and monstas
w = 303-16 #Width
p_h = (7*60)+19 #Pacman height

def startGame():

  all_sprites_list = pygame.sprite.Group()

  block_list = pygame.sprite.Group()

  monsta_list = pygame.sprite.Group()

  bomb_list = pygame.sprite.Group()

  pacman_collide = pygame.sprite.Group()

  wall_list = setupRoomOne(all_sprites_list)

  gate = setupGate(all_sprites_list)

  # Create the player paddle object
  Pacman = Player( w, p_h, "images/Trollman.png" )
  all_sprites_list.add(Pacman)
  pacman_collide.add(Pacman)

  # 準備存放鬼魂可以隨機生成的合法座標
  valid_spawn_points = []

  # Draw the grid
  for row in range(19):
      for column in range(19):
          if (row == 7 or row == 8) and (column == 8 or column == 9 or column == 10):
              continue
          else:
            block = Block(yellow, 4, 4)

            # Set a random location for the block
            block.rect.x = (30*column+6)+26
            block.rect.y = (30*row+6)+26

            b_collide = pygame.sprite.spritecollide(block, wall_list, False)
            p_collide = pygame.sprite.spritecollide(block, pacman_collide, False)
            if b_collide:
              continue
            elif p_collide:
              continue
            else:
              # Add the block to the list of objects
              block_list.add(block)
              all_sprites_list.add(block)
              
              # 收集鬼魂合法的生成座標 (將豆子座標微調到置中)
              ghost_x = block.rect.x - 13
              ghost_y = block.rect.y - 13
              # 確保首波鬼魂的生成位置不要離玩家太近 (安全距離大於100像素)
              if abs(ghost_x - w) > 100 or abs(ghost_y - p_h) > 100:
                  valid_spawn_points.append((ghost_x, ghost_y))

  bll = len(block_list)

  # 隨機打亂並挑選 4 個生成位置給初始的 4 隻鬼魂
  random.shuffle(valid_spawn_points)
  spawns = valid_spawn_points[:4]
   
  Blinky=Ghost( spawns[0][0], spawns[0][1], "images/Blinky.png" )
  monsta_list.add(Blinky)
  all_sprites_list.add(Blinky)

  Pinky=Ghost( spawns[1][0], spawns[1][1], "images/Pinky.png" )
  monsta_list.add(Pinky)
  all_sprites_list.add(Pinky)
   
  Inky=Ghost( spawns[2][0], spawns[2][1], "images/Inky.png" )
  monsta_list.add(Inky)
  all_sprites_list.add(Inky)
   
  Clyde=Ghost( spawns[3][0], spawns[3][1], "images/Clyde.png" )
  monsta_list.add(Clyde)
  all_sprites_list.add(Clyde)

  score = 0
  done = False
  
  # 設定定時器：每 15 秒 (15000 毫秒) 觸發一次新增鬼魂事件
  ADD_GHOST_EVENT = pygame.USEREVENT + 1
  pygame.time.set_timer(ADD_GHOST_EVENT, 15000)
  
  # 提供給隨機生成的鬼魂外觀選項
  ghost_images = ["images/Blinky.png", "images/Pinky.png", "images/Inky.png", "images/Clyde.png"]

  active_explosions = []  # [(rects, frames_remaining)]
  space_held = False

  while done == False:
      # ALL EVENT PROCESSING SHOULD GO BELOW THIS COMMENT
      for event in pygame.event.get():
          if event.type == pygame.QUIT:
              done=True
              
          # 檢查是否觸發了增加鬼魂事件
          if event.type == ADD_GHOST_EVENT:
              if len(monsta_list) < MAX_GHOSTS:
                  # 嘗試找一個遠離「當前」小精靈位置的安全生成點
                  safe_points = []
                  for pt in valid_spawn_points:
                      dist_x = abs(pt[0] - Pacman.rect.left)
                      dist_y = abs(pt[1] - Pacman.rect.top)
                      if dist_x > 100 or dist_y > 100:
                          safe_points.append(pt)
                  
                  # 如果有安全的生成點，就誕生一隻新鬼魂
                  if safe_points:
                      spawn_pt = random.choice(safe_points)
                      img = random.choice(ghost_images)
                      new_ghost = Ghost(spawn_pt[0], spawn_pt[1], img)
                      monsta_list.add(new_ghost)
                      all_sprites_list.add(new_ghost)

          if event.type == pygame.KEYDOWN:
              if event.key == pygame.K_LEFT:
                  Pacman.changespeed(-30,0)
              if event.key == pygame.K_RIGHT:
                  Pacman.changespeed(30,0)
              if event.key == pygame.K_UP:
                  Pacman.changespeed(0,-30)
              if event.key == pygame.K_DOWN:
                  Pacman.changespeed(0,30)

          if event.type == pygame.KEYUP:
              if event.key == pygame.K_LEFT:
                  Pacman.changespeed(30,0)
              if event.key == pygame.K_RIGHT:
                  Pacman.changespeed(-30,0)
              if event.key == pygame.K_UP:
                  Pacman.changespeed(0,30)
              if event.key == pygame.K_DOWN:
                  Pacman.changespeed(0,-30)
          
      # ALL EVENT PROCESSING SHOULD GO ABOVE THIS COMMENT
   
      # ALL GAME LOGIC SHOULD GO BELOW THIS COMMENT
      Pacman.update(wall_list,gate)

      # 炸彈邏輯判定
      for b in list(bomb_list):
          b.update(wall_list)
          if b.exploded:
              cells = b.get_explosion_cells(wall_list)
              active_explosions.append((cells, 5))
              if bomb_sound:
                  bomb_sound.play()
              rects = [r for r, _, _ in cells]
              for m in list(monsta_list):
                  if any(m.rect.colliderect(r) for r in rects):
                      m.kill()
              pacman_hit = any(Pacman.rect.colliderect(r) for r in rects)
              b.kill()
              if pacman_hit:
                  pygame.time.set_timer(ADD_GHOST_EVENT, 0)
                  # 顯示爆炸畫面約 1 秒，讓玩家看到被炸到的瞬間
                  for _ in range(10):
                      screen.fill(black)
                      wall_list.draw(screen)
                      gate.draw(screen)
                      all_sprites_list.draw(screen)
                      for r2, ct, rot2 in cells:
                          if ct == 'center' and _expl_center:
                              screen.blit(_expl_center, r2)
                          elif ct == 'mid' and _expl_mid:
                              screen.blit(pygame.transform.rotate(_expl_mid, rot2), r2)
                          elif ct == 'end' and _expl_end:
                              screen.blit(pygame.transform.rotate(_expl_end, rot2), r2)
                          else:
                              pygame.draw.rect(screen, (255, 200, 0), r2)
                      pygame.display.flip()
                      clock.tick(10)
                  doNext("Game Over", 235, all_sprites_list, block_list, monsta_list, pacman_collide, wall_list, gate)
                  return

      # 左 Ctrl 放炸彈（不受中文輸入法攔截，Windows/Mac 皆適用）
      keys = pygame.key.get_pressed()
      if keys[pygame.K_LCTRL] and not space_held:
          if Pacman.bomb_count > 0:
              new_bomb = Bomb(Pacman.rect.left, Pacman.rect.top)
              bomb_list.add(new_bomb)
              all_sprites_list.add(new_bomb)
              Pacman.bomb_count -= 1
          space_held = True
      elif not keys[pygame.K_LCTRL]:
          space_held = False

      # 更新所有在列表裡的鬼魂 (不管是初始的還是後來生成的)
      for monsta in monsta_list:
          monsta.update(wall_list, False)

      # See if the Pacman block has collided with anything.
      blocks_hit_list = pygame.sprite.spritecollide(Pacman, block_list, True)
       
      # Check the list of collisions.
      if len(blocks_hit_list) > 0:
          score +=len(blocks_hit_list)
      
      # ALL GAME LOGIC SHOULD GO ABOVE THIS COMMENT
   
      # ALL CODE TO DRAW SHOULD GO BELOW THIS COMMENT
      screen.fill(black)
      wall_list.draw(screen)
      gate.draw(screen)
      all_sprites_list.draw(screen)
      monsta_list.draw(screen)

      # 繪製爆炸效果（持續 5 幀）
      next_active = []
      for cells, frames in active_explosions:
          for r, cell_type, rot in cells:
              if cell_type == 'center' and _expl_center:
                  screen.blit(_expl_center, r)
              elif cell_type == 'mid' and _expl_mid:
                  screen.blit(pygame.transform.rotate(_expl_mid, rot), r)
              elif cell_type == 'end' and _expl_end:
                  screen.blit(pygame.transform.rotate(_expl_end, rot), r)
              else:
                  pygame.draw.rect(screen, (255, 200, 0), r)
          if frames > 1:
              next_active.append((cells, frames - 1))
      active_explosions = next_active

      stats_text = "Score: " + str(score) + "/" + str(bll) + "  Bombs: " + str(Pacman.bomb_count)
      text = font.render(stats_text, True, red)
      screen.blit(text, [10, 10])

      if score == bll:
        pygame.time.set_timer(ADD_GHOST_EVENT, 0) # 遊戲結束時停止計時器
        doNext("Congratulations, you won!",145,all_sprites_list,block_list,monsta_list,pacman_collide,wall_list,gate)

      monsta_hit_list = pygame.sprite.spritecollide(Pacman, monsta_list, False)

      if monsta_hit_list:
        pygame.time.set_timer(ADD_GHOST_EVENT, 0) # 遊戲結束時停止計時器
        doNext("Game Over",235,all_sprites_list,block_list,monsta_list,pacman_collide,wall_list,gate)

      # ALL CODE TO DRAW SHOULD GO ABOVE THIS COMMENT
      
      pygame.display.flip()
    
      clock.tick(10)

def doNext(message,left,all_sprites_list,block_list,monsta_list,pacman_collide,wall_list,gate):
  while True:
      # ALL EVENT PROCESSING SHOULD GO BELOW THIS COMMENT
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
            return # 離開這個迴圈，避免堆疊過深

      #Grey background
      w = pygame.Surface((400,200))  # the size of your rect
      w.set_alpha(10)                # alpha level
      w.fill((128,128,128))           # this fills the entire surface
      screen.blit(w, (100,200))    # (0,0) are the top-left coordinates

      #Won or lost
      text1=font.render(message, True, white)
      screen.blit(text1, [left, 233])

      text2=font.render("To play again, press ENTER.", True, white)
      screen.blit(text2, [135, 303])
      text3=font.render("To quit, press ESCAPE.", True, white)
      screen.blit(text3, [165, 333])

      pygame.display.flip()

      clock.tick(10)

startGame()

pygame.quit()
