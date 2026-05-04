# 炸彈功能技術規格文件

## 分工概覽

| 同學 | 負責檔案 | 負責範圍 |
|------|----------|----------|
| A 同學 | `bomb_logic.py`（新建） | 炸彈核心邏輯：計時、爆炸範圍計算、牆壁阻擋 |
| B 同學 | `pacman.py`（已修改） | 玩家操控炸彈、炸彈歸還、UI 顯示、傷害判定呼叫 |

---

## A 同學：`bomb_logic.py` 規格

### 必須建立的檔案

新建 `bomb_logic.py`，放在與 `pacman.py` 相同的目錄下。

### 必須滿足的介面（B 同學的程式碼依賴這些）

#### `Bomb` 類別

```python
import pygame

class Bomb(pygame.sprite.Sprite):
    def __init__(self, x, y):
        """
        參數：
            x, y — 放置炸彈時 Pacman 的 rect.left 與 rect.top
        必須設定的屬性：
            self.exploded  (bool)  — 初始為 False，倒數結束後設為 True
            self.timer     (float) — 倒數秒數，初始為 5.0
            self.image     — pygame.Surface，讓炸彈能被畫在畫面上
            self.rect      — pygame.Rect，位置需對應傳入的 x, y
        """
        pass

    def update(self, wall_list):
        """
        每幀由主迴圈呼叫。
        負責：
          1. 根據經過的時間遞減 self.timer
          2. self.timer <= 0 時，將 self.exploded 設為 True
        注意：不需要在這裡呼叫 kill()，B 同學的程式碼會處理。
        """
        pass

    def get_explosion_rects(self, wall_list):
        """
        回傳爆炸範圍的 pygame.Rect list。
        規則：
          - 從炸彈中心向上、下、左、右四個方向延伸
          - 每個方向最多延伸 3 格（每格 30px）
          - 遇到 wall_list 中的牆壁時，該方向停止延伸（牆壁本身不納入）
          - 炸彈所在格也算在範圍內
        回傳：
          list[pygame.Rect] — 每個 Rect 代表一個爆炸格
        """
        pass
```

### 實作提示

**計時方式（使用 `pygame.time.get_ticks()`）**

```python
def __init__(self, x, y):
    super().__init__()
    self.timer = 5.0
    self.exploded = False
    self._start_time = pygame.time.get_ticks()  # 記錄放置時間（毫秒）
    # ... 設定 image 與 rect

def update(self, wall_list):
    elapsed = (pygame.time.get_ticks() - self._start_time) / 1000.0  # 轉換為秒
    self.timer = max(0.0, 5.0 - elapsed)
    if self.timer == 0.0:
        self.exploded = True
```

**十字爆炸範圍計算（含牆壁阻擋）**

```python
def get_explosion_rects(self, wall_list):
    rects = []
    cx = self.rect.left
    cy = self.rect.top
    cell = 30  # 每格像素大小
    blast_range = 3  # 爆炸延伸格數

    rects.append(pygame.Rect(cx, cy, cell, cell))  # 炸彈本身所在格

    for dx, dy in [(1,0), (-1,0), (0,1), (0,-1)]:  # 右、左、下、上
        for step in range(1, blast_range + 1):
            r = pygame.Rect(cx + dx*cell*step, cy + dy*cell*step, cell, cell)
            # 偵測是否碰到牆壁
            if pygame.sprite.spritecollideany(
                    type('_', (pygame.sprite.Sprite,), {'rect': r})(), wall_list):
                break  # 該方向被牆擋住，停止延伸
            rects.append(r)

    return rects
```

> 注意：上方的牆壁碰撞偵測寫法只是示意，A 同學可自行選擇合適的實作方式（例如直接用 `rect.colliderect` 對每面牆逐一比對）。

**炸彈外觀建議（無圖片素材時的備案）**

```python
self.image = pygame.Surface([30, 30])
self.image.fill((0, 0, 0))
self.image.set_colorkey((0, 0, 0))
pygame.draw.circle(self.image, (200, 100, 0), (15, 15), 10)  # 橘色圓形
self.rect = self.image.get_rect()
self.rect.left = x
self.rect.top = y
```

---

## B 同學：已完成的修改（`pacman.py`）

### 修改清單

| 行號 | 修改內容 |
|------|----------|
| 第 7 行 | `from bomb_logic import Bomb` — 匯入 A 同學的炸彈類別 |
| 第 139 行 | `Player` 類別新增 `bomb_count = 3` — 玩家初始持有 3 顆炸彈 |
| 第 320 行 | `startGame()` 初始化 `bomb_list = pygame.sprite.Group()` |
| 第 424–431 行 | 偵測 `K_SPACE`，`bomb_count > 0` 時放置炸彈並 `-1` |
| 第 452–467 行 | 每幀更新炸彈；爆炸後消滅範圍內鬼魂、判斷 Pacman 是否被炸、炸彈用完後 `bomb_count +1` |
| 第 488–489 行 | 畫面左上角（Score 下方）顯示 `Bombs: N`（黃色文字） |

### B 同學的核心邏輯（供 A 同學對照）

```python
# 放置炸彈（SPACE 鍵）
if event.key == pygame.K_SPACE:
    if Pacman.bomb_count > 0:
        bomb = Bomb(Pacman.rect.left, Pacman.rect.top)  # 呼叫 A 同學的 class
        bomb_list.add(bomb)
        all_sprites_list.add(bomb)
        Pacman.bomb_count -= 1

# 每幀更新炸彈
for bomb in list(bomb_list):
    bomb.update(wall_list)           # 呼叫 A 同學的 update()
    if bomb.exploded:                # 讀取 A 同學的 exploded 旗標
        explosion_rects = bomb.get_explosion_rects(wall_list)  # 呼叫 A 同學的方法
        for ghost in list(monsta_list):
            for rect in explosion_rects:
                if ghost.rect.colliderect(rect):
                    ghost.kill()
                    break
        pacman_hit = any(Pacman.rect.colliderect(rect) for rect in explosion_rects)
        bomb.kill()
        Pacman.bomb_count += 1       # 炸彈用完後歸還一顆
        if pacman_hit:
            pygame.time.set_timer(ADD_GHOST_EVENT, 0)
            doNext("Game Over", 235, ...)
```

---

## 整合後應出現的功能（驗收清單）

整合完成、執行 `pacman.py` 後，請雙方依照以下清單逐一確認：

### 基本功能

- [ ] 遊戲啟動後，畫面左上角顯示 `Score: 0/XX` 及 `Bombs: 3`
- [ ] 按下 `SPACE` 鍵，畫面上出現一顆炸彈（橘色圓形或自訂圖示）
- [ ] 放置炸彈後，`Bombs: 3` 變為 `Bombs: 2`
- [ ] 最多同時放置 3 顆，炸彈數為 0 時按 `SPACE` 無反應

### 計時與爆炸

- [ ] 炸彈放置後約 5 秒發生爆炸
- [ ] 爆炸後炸彈圖示從畫面上消失
- [ ] 爆炸後 `Bombs` 數量 +1（歸還一顆）

### 爆炸範圍與傷害

- [ ] 爆炸範圍為十字形（中心格 + 四方向各最多 3 格）
- [ ] 牆壁能擋住爆炸延伸（牆壁後方的鬼魂不受傷害）
- [ ] 爆炸範圍內的鬼魂被消滅，從畫面上移除
- [ ] Pacman 在爆炸範圍內時觸發 Game Over 畫面

### 邊界情況

- [ ] Pacman 放下炸彈後立刻離開，不在爆炸範圍內 → 遊戲繼續正常進行
- [ ] 同時放置多顆炸彈，各自獨立倒數與爆炸
- [ ] 鬼魂被炸彈消滅後，遊戲繼續（不觸發 Game Over）

---

## 檔案結構

```
Pacman/
├── pacman.py          ← B 同學已修改完畢
├── bomb_logic.py      ← A 同學需新建
├── images/
│   ├── Trollman.png
│   ├── Blinky.png
│   ├── Pinky.png
│   ├── Inky.png
│   └── Clyde.png
└── pacman.mp3
```
