import pygame
import sys
import random
import json
import os

pygame.init()
pygame.font.init()

WIDTH, HEIGHT = 900, 650
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("2D RPG Game")

font_title = pygame.font.SysFont("arial", 44, bold=True)
font_btn = pygame.font.SysFont("arial", 26, bold=True)
font_large = pygame.font.SysFont("arial", 28, bold=True)
font_small = pygame.font.SysFont("arial", 18, bold=True)

def load_img(path, size):
    try:
        img = pygame.image.load(path).convert_alpha()
        return pygame.transform.scale(img, size)
    except Exception:
        surf = pygame.Surface(size)
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

# მენიუს ღილაკები (PLAY, SAVE, LOAD, QUIT)
btn_w, btn_h = 220, 52
btn_x = WIDTH // 2 - btn_w // 2

play_btn = pygame.Rect(btn_x, 210, btn_w, btn_h)
save_btn = pygame.Rect(btn_x, 280, btn_w, btn_h)
load_btn = pygame.Rect(btn_x, 350, btn_w, btn_h)
quit_btn = pygame.Rect(btn_x, 420, btn_w, btn_h)

restart_btn_ui = pygame.Rect(WIDTH - 130, 6, 120, 28)
restart_btn_screen = pygame.Rect(WIDTH // 2 - 100, 340, 200, 50)

menu_msg = ""
menu_msg_timer = 0

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
    global bullets, enemies, boss, boss_active, boss_hp, boss_max_hp, inventory, assistant_x, assistant_y
    player_x, player_y = 100, 300
    player_hp = 100
    max_hp = 100
    level = 1
    xp = 0
    xp_to_next = 50
    score = 0
    bullets = []
    enemies = []
    boss = None
    boss_active = False
    boss_hp = 300
    boss_max_hp = 300
    assistant_x, assistant_y = 420, 60
    inventory = {"Potion (HP)": 3, "Gold Coin": 0, "Boss Key": 1}

def save_game():
    data = {
        "player_x": player_x, "player_y": player_y,
        "player_hp": player_hp, "max_hp": max_hp,
        "level": level, "xp": xp, "xp_to_next": xp_to_next,
        "score": score, "inventory": inventory
    }
    with open("savegame.json", "w", encoding="utf-8") as f:
        json.dump(data, f)

def load_game():
    global player_x, player_y, player_hp, max_hp, level, xp, xp_to_next, score, inventory
    if os.path.exists("savegame.json"):
        with open("savegame.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            player_x = data.get("player_x", 100)
            player_y = data.get("player_y", 300)
            player_hp = data.get("player_hp", 100)
            max_hp = data.get("max_hp", 100)
            level = data.get("level", 1)
            xp = data.get("xp", 0)
            xp_to_next = data.get("xp_to_next", 50)
            score = data.get("score", 0)
            inventory = data.get("inventory", {})
            return True
    return False

reset_game()

clock = pygame.time.Clock()
speed = 5
bullet_speed = 12

def spawn_enemy():
    x = random.randint(WIDTH // 2, WIDTH - 60)
    y = random.randint(60, HEIGHT - 60)
    enemies.append({"rect": pygame.Rect(x, y, 45, 45), "hp": 20})

running = True
while running:
    clock.tick(60)
    mouse_pos = pygame.mouse.get_pos()

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

            if current_state == STATE_PLAYING and event.key == pygame.K_SPACE:
                bullets.append(pygame.Rect(player_x + 52, player_y + 23, 14, 6))

            if current_state in (STATE_GAMEOVER, STATE_VICTORY) and event.key == pygame.K_r:
                reset_game()
                current_state = STATE_PLAYING

    if current_state == STATE_PLAYING:
        keys = pygame.key.get_pressed()
        if (keys[pygame.K_LEFT] or keys[pygame.K_a]) and player_x > 0: player_x -= speed
        if (keys[pygame.K_RIGHT] or keys[pygame.K_d]) and player_x < WIDTH - 50: player_x += speed
        if (keys[pygame.K_UP] or keys[pygame.K_w]) and player_y > 40: player_y -= speed
        if (keys[pygame.K_DOWN] or keys[pygame.K_s]) and player_y < HEIGHT - 50: player_y += speed

        for bullet in bullets[:]:
            bullet.x += bullet_speed
            if bullet.x > WIDTH: bullets.remove(bullet)

        if not boss_active and len(enemies) < 3 + level:
            if random.randint(1, 40) == 1: spawn_enemy()

        player_rect = pygame.Rect(player_x, player_y, 50, 50)

        for enemy in enemies[:]:
            if enemy["rect"].x > player_x: enemy["rect"].x -= 2
            if enemy["rect"].y < player_y: enemy["rect"].y += 1
            elif enemy["rect"].y > player_y: enemy["rect"].y -= 1

            if player_rect.colliderect(enemy["rect"]):
                player_hp -= 1
                if player_hp <= 0: current_state = STATE_GAMEOVER

            for bullet in bullets[:]:
                if enemy["rect"].colliderect(bullet):
                    if bullet in bullets: bullets.remove(bullet)
                    enemy["hp"] -= 10
                    if enemy["hp"] <= 0:
                        enemies.remove(enemy)
                        score += 10
                        xp += 20
                        inventory["Gold Coin"] = inventory.get("Gold Coin", 0) + 1
                        break

        if xp >= xp_to_next and level == 1:
            level = 2
            boss_active = True
            boss = pygame.Rect(WIDTH - 150, HEIGHT // 2 - 50, 110, 110)
            enemies.clear()

        if boss_active and boss:
            if boss.y < player_y: boss.y += 1
            elif boss.y > player_y: boss.y -= 1

            if player_rect.colliderect(boss):
                player_hp -= 2
                if player_hp <= 0: current_state = STATE_GAMEOVER

            for bullet in bullets[:]:
                if boss.colliderect(bullet):
                    if bullet in bullets: bullets.remove(bullet)
                    boss_hp -= 10
                    if boss_hp <= 0: current_state = STATE_VICTORY

        assistant_rect = pygame.Rect(assistant_x, assistant_y, 50, 50)
        if player_rect.colliderect(assistant_rect):
            if player_hp < max_hp: player_hp = min(max_hp, player_hp + 20)

    # დახატვა
    screen.fill((20, 25, 45))

    if current_state == STATE_MENU:
        title_surf = font_title.render("2D RPG GAME", True, (255, 215, 0))
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
        screen.blit(assistant_img, (assistant_x, assistant_y))
        screen.blit(player_img, (player_x, player_y))

        weapon_rect = pygame.Rect(player_x + 38, player_y + 22, 20, 7)
        gun_handle = pygame.Rect(player_x + 40, player_y + 27, 6, 7)
        pygame.draw.rect(screen, (80, 80, 90), weapon_rect)
        pygame.draw.rect(screen, (130, 70, 30), gun_handle)

        for bullet in bullets:
            pygame.draw.rect(screen, (255, 220, 0), bullet)
            pygame.draw.rect(screen, (255, 80, 0), (bullet.x - 3, bullet.y + 1, 4, 4))

        for enemy in enemies:
            screen.blit(enemy_img, (enemy["rect"].x, enemy["rect"].y))

        if boss_active and boss:
            screen.blit(boss_img, (boss.x, boss.y))
            pygame.draw.rect(screen, (250, 0, 0), (boss.x, boss.y - 15, 110, 8))
            pygame.draw.rect(screen, (0, 255, 0), (boss.x, boss.y - 15, int(110 * (boss_hp / boss_max_hp)), 8))

        pygame.draw.rect(screen, (40, 40, 50), (0, 0, WIDTH, 40))
        pygame.draw.rect(screen, (200, 0, 0), (10, 10, 130, 20))
        pygame.draw.rect(screen, (0, 220, 0), (10, 10, max(0, int(130 * (player_hp / max_hp))), 20))
        hp_text = font_small.render(f"HP: {player_hp}/{max_hp}", True, (255, 255, 255))
        screen.blit(hp_text, (15, 10))

        info_txt = font_small.render(f"LVL: {level} | XP: {xp}/{xp_to_next} | SCORE: {score} | [I] Inventory | [SPACE] Shoot", True, (220, 220, 220))
        screen.blit(info_txt, (150, 10))

        pygame.draw.rect(screen, (180, 40, 40), restart_btn_ui, border_radius=5)
        pygame.draw.rect(screen, (255, 255, 255), restart_btn_ui, 2, border_radius=5)
        restart_txt = font_small.render("RESTART", True, (255, 255, 255))
        screen.blit(restart_txt, (WIDTH - 110, 10))

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
        screen.blit(btn_txt, (WIDTH // 2 - btn_txt.get_width() // 2, 350))

    pygame.display.flip()

pygame.quit()
sys.exit()
