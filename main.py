import pygame
import sys
import random
import json
import os
import math

pygame.init()
pygame.font.init()

WIDTH, HEIGHT = 900, 650
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("2D Sci-Fi RPG Game")

font_title = pygame.font.SysFont("arial", 44, bold=True)
font_btn = pygame.font.SysFont("arial", 26, bold=True)
font_large = pygame.font.SysFont("arial", 28, bold=True)
font_small = pygame.font.SysFont("arial", 16, bold=True)
font_hud = pygame.font.SysFont("arial", 14, bold=True)

def load_img(path, size):
    try:
        img = pygame.image.load(path).convert_alpha()
        return pygame.transform.scale(img, size)
    except Exception:
        surf = pygame.Surface(size, pygame.SRCALPHA)
        surf.fill((180, 180, 180))
        return surf

player_img = load_img("player.png", (50, 50))
enemy_img = load_img("enemy.png", (45, 45))
boss_img = load_img("boss.png", (110, 110))
assistant_img = load_img("asistent.png", (50, 50))

STATE_MENU = "MENU"
STATE_PLAYING = "PLAYING"
STATE_INVENTORY = "INVENTORY"
STATE_GAMEOVER = "GAMEOVER"
STATE_VICTORY = "VICTORY"

current_state = STATE_MENU

btn_w, btn_h = 220, 52
btn_x = WIDTH // 2 - btn_w // 2

play_btn = pygame.Rect(btn_x, 210, btn_w, btn_h)
save_btn = pygame.Rect(btn_x, 280, btn_w, btn_h)
load_btn = pygame.Rect(btn_x, 350, btn_w, btn_h)
quit_btn = pygame.Rect(btn_x, 420, btn_w, btn_h)

restart_btn_ui = pygame.Rect(WIDTH - 120, 10, 110, 30)
restart_btn_screen = pygame.Rect(WIDTH // 2 - 100, 360, 200, 50)

menu_msg = ""
menu_msg_timer = 0

embers = []
for _ in range(50):
    embers.append({
        "x": random.randint(0, WIDTH),
        "y": random.randint(0, HEIGHT),
        "vx": random.uniform(-0.8, 0.8),
        "vy": random.uniform(-1.8, -0.4),
        "radius": random.randint(1, 3),
        "color": random.choice([(255, 120, 20), (255, 180, 40), (255, 60, 10)])
    })

def draw_styled_button(surface, rect, text, is_hovered):
    bg_color = (230, 80, 60) if is_hovered else (190, 60, 45)
    border_color = (255, 210, 160) if is_hovered else (120, 30, 20)
    shadow_color = (90, 20, 15)

    pygame.draw.rect(surface, shadow_color, (rect.x, rect.y + 4, rect.width, rect.height), border_radius=10)
    pygame.draw.rect(surface, bg_color, rect, border_radius=10)
    pygame.draw.rect(surface, border_color, rect, 3, border_radius=10)

    txt_surf = font_btn.render(text, True, (255, 255, 255))
    txt_rect = txt_surf.get_rect(center=rect.center)
    surface.blit(txt_surf, txt_rect)

def reset_game():
    global player_x, player_y, player_hp, max_hp, level, xp, xp_to_next, score
    global bullets, enemy_bullets, boss_bullets, enemies, boss, boss_active, boss_hp, boss_max_hp
    global inventory, assistant_x, assistant_y, assistant_dir
    global current_ammo, max_ammo, is_reloading, reload_start_time
    global boss_special_charging, boss_special_charge_start, boss_special_target, boss_special_timer

    player_x, player_y = 80, 460
    player_hp = 100
    max_hp = 100
    level = 1
    xp = 0
    xp_to_next = 50
    score = 0
    bullets = []
    enemy_bullets = []
    boss_bullets = []
    enemies = []
    boss = None
    boss_active = False
    boss_hp = 300
    boss_max_hp = 300
    
    assistant_x, assistant_y = 350, 460
    assistant_dir = 1

    inventory = {"Potion (HP)": 3, "Gold Coin": 0, "Boss Key": 1}

    max_ammo = 10
    current_ammo = 10
    is_reloading = False
    reload_start_time = 0

    boss_special_charging = False
    boss_special_charge_start = 0
    boss_special_target = (0, 0)
    boss_special_timer = 0

def save_game():
    data = {
        "player_x": player_x, "player_y": player_y,
        "player_hp": player_hp, "max_hp": max_hp,
        "level": level, "xp": xp, "xp_to_next": xp_to_next,
        "score": score, "inventory": inventory,
        "current_ammo": current_ammo
    }
    with open("savegame.json", "w", encoding="utf-8") as f:
        json.dump(data, f)

def load_game():
    global player_x, player_y, player_hp, max_hp, level, xp, xp_to_next, score, inventory, current_ammo
    if os.path.exists("savegame.json"):
        with open("savegame.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            player_x = data.get("player_x", 80)
            player_y = data.get("player_y", 460)
            player_hp = data.get("player_hp", 100)
            max_hp = data.get("max_hp", 100)
            level = data.get("level", 1)
            xp = data.get("xp", 0)
            xp_to_next = data.get("xp_to_next", 50)
            score = data.get("score", 0)
            inventory = data.get("inventory", {})
            current_ammo = data.get("current_ammo", 10)
            return True
    return False

reset_game()

clock = pygame.time.Clock()
speed = 5
bullet_speed = 13
RELOAD_TIME = 3000

boss_shoot_timer = 0

def spawn_enemy():
    x = random.randint(WIDTH // 2, WIDTH - 60)
    y = random.randint(120, HEIGHT - 150)
    enemies.append({"rect": pygame.Rect(x, y, 45, 45), "hp": 20, "shoot_cooldown": random.randint(30, 90)})

running = True
while running:
    current_time = pygame.time.get_ticks()
    clock.tick(60)
    mouse_pos = pygame.mouse.get_pos()

    for ember in embers:
        ember["x"] += ember["vx"]
        ember["y"] += ember["vy"]
        if ember["y"] < 0 or ember["x"] < 0 or ember["x"] > WIDTH:
            ember["x"] = random.randint(0, WIDTH)
            ember["y"] = HEIGHT + random.randint(5, 20)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            if current_state == STATE_MENU:
                if play_btn.collidepoint(mouse_pos):
                    current_state = STATE_PLAYING
                elif save_btn.collidepoint(mouse_pos):
                    save_game()
                    menu_msg = "Game Saved!"
                    menu_msg_timer = 120
                elif load_btn.collidepoint(mouse_pos):
                    if load_game():
                        menu_msg = "Game Loaded!"
                        current_state = STATE_PLAYING
                    else:
                        menu_msg = "No Save Found!"
                    menu_msg_timer = 120
                elif quit_btn.collidepoint(mouse_pos):
                    running = False

            elif current_state in (STATE_PLAYING, STATE_INVENTORY) and restart_btn_ui.collidepoint(mouse_pos):
                reset_game()
                current_state = STATE_PLAYING
            elif current_state in (STATE_GAMEOVER, STATE_VICTORY) and restart_btn_screen.collidepoint(mouse_pos):
                reset_game()
                current_state = STATE_PLAYING

        if event.type == pygame.KEYDOWN:
            if current_state == STATE_MENU and event.key == pygame.K_RETURN:
                current_state = STATE_PLAYING

            elif current_state in (STATE_PLAYING, STATE_INVENTORY):
                if event.key == pygame.K_i:
                    current_state = STATE_INVENTORY if current_state == STATE_PLAYING else STATE_PLAYING
                if event.key == pygame.K_h and inventory.get("Potion (HP)", 0) > 0:
                    inventory["Potion (HP)"] -= 1
                    player_hp = min(max_hp, player_hp + 40)
                
                if event.key == pygame.K_r and not is_reloading and current_ammo < max_ammo:
                    is_reloading = True
                    reload_start_time = current_time

            if current_state == STATE_PLAYING and event.key == pygame.K_SPACE:
                if not is_reloading and current_ammo > 0:
                    current_ammo -= 1
                    if current_ammo == 0:
                        is_reloading = True
                        reload_start_time = current_time

                    px, py = player_x + 25, player_y + 25
                    target_pos = None
                    min_dist = float('inf')

                    for enemy in enemies:
                        dist = math.hypot(enemy["rect"].centerx - px, enemy["rect"].centery - py)
                        if dist < min_dist:
                            min_dist = dist
                            target_pos = enemy["rect"].center

                    if boss_active and boss:
                        dist = math.hypot(boss.centerx - px, boss.centery - py)
                        if dist < min_dist:
                            min_dist = dist
                            target_pos = boss.center

                    if target_pos:
                        dx = target_pos[0] - px
                        dy = target_pos[1] - py
                        dist = math.hypot(dx, dy)
                        if dist > 0:
                            vx = (dx / dist) * bullet_speed
                            vy = (dy / dist) * bullet_speed
                        else:
                            vx, vy = bullet_speed, 0
                    else:
                        vx, vy = bullet_speed, 0

                    bullets.append({
                        "x": float(player_x + 40),
                        "y": float(player_y + 25),
                        "vx": vx,
                        "vy": vy,
                        "rect": pygame.Rect(player_x + 40, player_y + 22, 10, 10)
                    })

            if current_state in (STATE_GAMEOVER, STATE_VICTORY) and event.key == pygame.K_r:
                reset_game()
                current_state = STATE_PLAYING

    if is_reloading:
        if current_time - reload_start_time >= RELOAD_TIME:
            current_ammo = max_ammo
            is_reloading = False

    if current_state == STATE_PLAYING:
        keys = pygame.key.get_pressed()
        if (keys[pygame.K_LEFT] or keys[pygame.K_a]) and player_x > 0: player_x -= speed
        if (keys[pygame.K_RIGHT] or keys[pygame.K_d]) and player_x < WIDTH - 50: player_x += speed
        if (keys[pygame.K_UP] or keys[pygame.K_w]) and player_y > 60: player_y -= speed
        if (keys[pygame.K_DOWN] or keys[pygame.K_s]) and player_y < HEIGHT - 110: player_y += speed

        assistant_x += assistant_dir * 1.5
        if assistant_x < 280 or assistant_x > 480:
            assistant_dir *= -1

        for bullet in bullets[:]:
            bullet["x"] += bullet["vx"]
            bullet["y"] += bullet["vy"]
            bullet["rect"].x = int(bullet["x"])
            bullet["rect"].y = int(bullet["y"])

            if bullet["x"] < 0 or bullet["x"] > WIDTH or bullet["y"] < 0 or bullet["y"] > HEIGHT:
                bullets.remove(bullet)

        if not boss_active and len(enemies) < 3 + level:
            if random.randint(1, 40) == 1: spawn_enemy()

        player_rect = pygame.Rect(player_x, player_y, 50, 50)
        assistant_rect = pygame.Rect(assistant_x, assistant_y, 50, 50)

        near_assistant = player_rect.colliderect(assistant_rect.inflate(30, 30))
        if near_assistant:
            if player_hp < max_hp:
                player_hp = min(max_hp, player_hp + 0.4)
            if current_ammo < max_ammo and not is_reloading:
                current_ammo = max_ammo

        for enemy in enemies[:]:
            if enemy["rect"].x > player_x: enemy["rect"].x -= 2
            if enemy["rect"].y < player_y: enemy["rect"].y += 1
            elif enemy["rect"].y > player_y: enemy["rect"].y -= 1

            enemy["shoot_cooldown"] -= 1
            if enemy["shoot_cooldown"] <= 0:
                enemy["shoot_cooldown"] = random.randint(70, 120)
                ex, ey = enemy["rect"].centerx, enemy["rect"].centery
                dx = player_rect.centerx - ex
                dy = player_rect.centery - ey
                dist = math.hypot(dx, dy)
                if dist > 0:
                    vx = (dx / dist) * 5
                    vy = (dy / dist) * 5
                    enemy_bullets.append({"rect": pygame.Rect(ex, ey, 8, 8), "vx": vx, "vy": vy})

            if player_rect.colliderect(enemy["rect"]):
                player_hp -= 1
                if player_hp <= 0: current_state = STATE_GAMEOVER

            for bullet in bullets[:]:
                if enemy["rect"].colliderect(bullet["rect"]):
                    if bullet in bullets: bullets.remove(bullet)
                    enemy["hp"] -= 10
                    if enemy["hp"] <= 0:
                        enemies.remove(enemy)
                        score += 10
                        xp += 20
                        inventory["Gold Coin"] = inventory.get("Gold Coin", 0) + 1
                        break

        for eb in enemy_bullets[:]:
            eb["rect"].x += eb["vx"]
            eb["rect"].y += eb["vy"]
            if eb["rect"].x < 0 or eb["rect"].x > WIDTH or eb["rect"].y < 0 or eb["rect"].y > HEIGHT:
                enemy_bullets.remove(eb)
            elif player_rect.colliderect(eb["rect"]):
                enemy_bullets.remove(eb)
                player_hp -= 8
                if player_hp <= 0: current_state = STATE_GAMEOVER

        if xp >= xp_to_next and level == 1:
            level = 2
            boss_active = True
            boss = pygame.Rect(WIDTH - 160, HEIGHT // 2 - 55, 110, 110)
            enemies.clear()
            enemy_bullets.clear()

        if boss_active and boss:
            if boss.y < player_y: boss.y += 1
            elif boss.y > player_y: boss.y -= 1

            if player_rect.colliderect(boss):
                player_hp -= 2
                if player_hp <= 0: current_state = STATE_GAMEOVER

            boss_shoot_timer += 1
            if boss_shoot_timer >= 50:
                boss_shoot_timer = 0
                bx, by = boss.centerx, boss.centery
                dx = player_rect.centerx - bx
                dy = player_rect.centery - by
                dist = math.hypot(dx, dy)
                if dist > 0:
                    vx = (dx / dist) * 7
                    vy = (dy / dist) * 7
                    boss_bullets.append({"rect": pygame.Rect(bx, by, 14, 14), "vx": vx, "vy": vy, "type": "normal"})

            if boss_hp <= 90:
                if not boss_special_charging and current_time - boss_special_timer > 3500:
                    boss_special_charging = True
                    boss_special_charge_start = current_time
                    boss_special_target = (player_rect.centerx, player_rect.centery)
                    boss_special_timer = current_time

                if boss_special_charging:
                    if current_time - boss_special_charge_start >= 1000:
                        boss_special_charging = False
                        bx, by = boss.centerx, boss.centery
                        dx = boss_special_target[0] - bx
                        dy = boss_special_target[1] - by
                        dist = math.hypot(dx, dy)
                        if dist > 0:
                            vx = (dx / dist) * 11
                            vy = (dy / dist) * 11
                            boss_bullets.append({"rect": pygame.Rect(bx - 15, by - 15, 32, 32), "vx": vx, "vy": vy, "type": "special"})

            for bb in boss_bullets[:]:
                bb["rect"].x += bb["vx"]
                bb["rect"].y += bb["vy"]
                if bb["rect"].x < 0 or bb["rect"].x > WIDTH or bb["rect"].y < 0 or bb["rect"].y > HEIGHT:
                    boss_bullets.remove(bb)
                elif player_rect.colliderect(bb["rect"]):
                    damage = 30 if bb["type"] == "special" else 10
                    player_hp -= damage
                    boss_bullets.remove(bb)
                    if player_hp <= 0: current_state = STATE_GAMEOVER

            for bullet in bullets[:]:
                if boss.colliderect(bullet["rect"]):
                    if bullet in bullets: bullets.remove(bullet)
                    boss_hp -= 10
                    if boss_hp <= 0: current_state = STATE_VICTORY

    if boss_active:
        screen.fill((25, 10, 20))
    else:
        screen.fill((18, 22, 35))

    for x in range(0, WIDTH, 80):
        pygame.draw.line(screen, (30, 38, 55), (x, 0), (x, HEIGHT), 2)
    for y in range(0, HEIGHT, 80):
        pygame.draw.line(screen, (30, 38, 55), (0, y), (WIDTH, y), 2)

    pygame.draw.rect(screen, (0, 180, 220), (180, 0, 12, HEIGHT))
    pygame.draw.rect(screen, (255, 50, 100), (WIDTH - 220, 0, 12, HEIGHT))

    pygame.draw.rect(screen, (40, 48, 65), (0, HEIGHT - 60, WIDTH, 60))
    pygame.draw.rect(screen, (80, 95, 125), (0, HEIGHT - 60, WIDTH, 6))
    for px in range(0, WIDTH, 40):
        pygame.draw.rect(screen, (25, 30, 45), (px, HEIGHT - 54, 38, 54))

    for ember in embers:
        pygame.draw.circle(screen, ember["color"], (int(ember["x"]), int(ember["y"])), ember["radius"])

    if current_state == STATE_MENU:
        title_surf = font_title.render("2D SCI-FI RPG GAME", True, (255, 215, 0))
        screen.blit(title_surf, (WIDTH // 2 - title_surf.get_width() // 2, 110))

        draw_styled_button(screen, play_btn, "PLAY", play_btn.collidepoint(mouse_pos))
        draw_styled_button(screen, save_btn, "SAVE", save_btn.collidepoint(mouse_pos))
        draw_styled_button(screen, load_btn, "LOAD", load_btn.collidepoint(mouse_pos))
        draw_styled_button(screen, quit_btn, "QUIT", quit_btn.collidepoint(mouse_pos))

        if menu_msg_timer > 0:
            msg_surf = font_small.render(menu_msg, True, (100, 255, 100))
            screen.blit(msg_surf, (WIDTH // 2 - msg_surf.get_width() // 2, 490))
            menu_msg_timer -= 1

    elif current_state in (STATE_PLAYING, STATE_INVENTORY):
        pygame.draw.ellipse(screen, (0, 150, 255, 80), (assistant_x - 15, assistant_y + 35, 80, 20))
        screen.blit(assistant_img, (assistant_x, assistant_y))

        st_txt = font_hud.render("REST & REFILL STATION", True, (0, 220, 255))
        screen.blit(st_txt, (assistant_x - 30, assistant_y - 20))

        if near_assistant:
            glow_txt = font_small.render("⚡ HP & AMMO REFILLING! ⚡", True, (50, 255, 120))
            screen.blit(glow_txt, (player_x - 30, player_y - 35))

        screen.blit(player_img, (player_x, player_y))
        pygame.draw.rect(screen, (90, 95, 110), (player_x + 38, player_y + 22, 20, 7))
        pygame.draw.rect(screen, (140, 75, 35), (player_x + 40, player_y + 27, 6, 7))

        if is_reloading:
            elapsed = current_time - reload_start_time
            remaining = max(0.0, (RELOAD_TIME - elapsed) / 1000)
            rel_txt = font_small.render(f"RELOADING ({remaining:.1f}s)", True, (255, 200, 50))
            screen.blit(rel_txt, (player_x - 20, player_y - 22))
            pygame.draw.rect(screen, (100, 100, 100), (player_x, player_y - 8, 50, 5))
            pygame.draw.rect(screen, (255, 200, 0), (player_x, player_y - 8, int(50 * (elapsed / RELOAD_TIME)), 5))

        for bullet in bullets:
            pygame.draw.circle(screen, (255, 230, 0), bullet["rect"].center, 5)
            pygame.draw.circle(screen, (255, 100, 0), bullet["rect"].center, 3)

        for enemy in enemies:
            screen.blit(enemy_img, (enemy["rect"].x, enemy["rect"].y))

        for eb in enemy_bullets:
            pygame.draw.circle(screen, (255, 80, 80), eb["rect"].center, 5)

        if boss_active and boss:
            screen.blit(boss_img, (boss.x, boss.y))
            pygame.draw.rect(screen, (150, 0, 0), (boss.x, boss.y - 15, 110, 10))
            pygame.draw.rect(screen, (255, 50, 50) if boss_hp <= 90 else (0, 255, 100), (boss.x, boss.y - 15, int(110 * max(0, boss_hp) / boss_max_hp), 10))

            if boss_special_charging:
                pygame.draw.line(screen, (255, 0, 0), boss.center, boss_special_target, 2)
                warn_txt = font_btn.render("⚠️ SPECIAL ATTACK CHARGING!", True, (255, 50, 50))
                screen.blit(warn_txt, (WIDTH // 2 - warn_txt.get_width() // 2, 50))

            for bb in boss_bullets:
                if bb["type"] == "special":
                    pygame.draw.circle(screen, (255, 0, 120), bb["rect"].center, 16)
                    pygame.draw.circle(screen, (255, 255, 200), bb["rect"].center, 10)
                else:
                    pygame.draw.circle(screen, (255, 140, 0), bb["rect"].center, 7)

        hud_bg = pygame.Rect(12, 12, 230, 75)
        pygame.draw.rect(screen, (20, 25, 38), hud_bg, border_radius=8)
        pygame.draw.rect(screen, (60, 75, 100), hud_bg, 2, border_radius=8)

        pygame.draw.rect(screen, (40, 45, 55), (22, 22, 150, 16), border_radius=4)
        hp_ratio = max(0, player_hp / max_hp)
        pygame.draw.rect(screen, (0, 220, 120), (22, 22, int(150 * hp_ratio), 16), border_radius=4)
        hp_lbl = font_hud.render(f"HP {int(player_hp)}/{max_hp}", True, (255, 255, 255))
        screen.blit(hp_lbl, (180, 22))

        pygame.draw.rect(screen, (40, 45, 55), (22, 48, 150, 16), border_radius=4)
        ammo_ratio = max(0, current_ammo / max_ammo)
        pygame.draw.rect(screen, (255, 160, 30), (22, 48, int(150 * ammo_ratio), 16), border_radius=4)
        ammo_lbl = font_hud.render(f"AMMO {current_ammo}/{max_ammo}", True, (255, 255, 255))
        screen.blit(ammo_lbl, (180, 48))

        info_txt = font_small.render(f"LVL: {level} | XP: {xp}/{xp_to_next} | SCORE: {score} | [I] Inventory", True, (220, 220, 220))
        screen.blit(info_txt, (260, 18))

        pygame.draw.rect(screen, (180, 40, 40), restart_btn_ui, border_radius=5)
        pygame.draw.rect(screen, (255, 255, 255), restart_btn_ui, 2, border_radius=5)
        restart_txt = font_small.render("RESTART", True, (255, 255, 255))
        screen.blit(restart_txt, (WIDTH - 105, 15))

        if current_state == STATE_INVENTORY:
            inv_surf = pygame.Surface((400, 300))
            inv_surf.fill((15, 15, 25))
            inv_surf.set_alpha(230)
            screen.blit(inv_surf, (WIDTH // 2 - 200, HEIGHT // 2 - 150))
            pygame.draw.rect(screen, (255, 215, 0), (WIDTH // 2 - 200, HEIGHT // 2 - 150, 400, 300), 3)

            inv_title = font_large.render("INVENTORY", True, (255, 215, 0))
            screen.blit(inv_title, (WIDTH // 2 - 70, HEIGHT // 2 - 130))

            y_off = HEIGHT // 2 - 70
            for item, qty in inventory.items():
                item_txt = font_small.render(f"* {item}: {qty}", True, (255, 255, 255))
                screen.blit(item_txt, (WIDTH // 2 - 160, y_off))
                y_off += 35

            use_txt = font_small.render("Press [H] for Potion (+40 HP)", True, (100, 255, 100))
            close_txt = font_small.render("Press [I] to Close", True, (200, 200, 200))
            screen.blit(use_txt, (WIDTH // 2 - 140, HEIGHT // 2 + 70))
            screen.blit(close_txt, (WIDTH // 2 - 100, HEIGHT // 2 + 100))

    elif current_state in (STATE_GAMEOVER, STATE_VICTORY):
        title_txt = font_title.render("GAME OVER" if current_state == STATE_GAMEOVER else "VICTORY!", True, (255, 50, 50) if current_state == STATE_GAMEOVER else (50, 255, 50))
        screen.blit(title_txt, (WIDTH // 2 - title_txt.get_width() // 2, 200))

        pygame.draw.rect(screen, (200, 50, 50), restart_btn_screen, border_radius=8)
        pygame.draw.rect(screen, (255, 255, 255), restart_btn_screen, 3, border_radius=8)
        btn_txt = font_large.render("RESTART", True, (255, 255, 255))
        screen.blit(btn_txt, (WIDTH // 2 - btn_txt.get_width() // 2, 360))

    pygame.display.flip()

pygame.quit()
sys.exit()
