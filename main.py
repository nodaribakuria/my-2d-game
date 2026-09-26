import pygame
import sys

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("ჩემი 2D თამაში")

# სურათის ჩატვირთვის ფუნქცია (თუ ვერ იპოვა, შექმნის ფერად კვადრატს)
def load_image(filename, color):
    try:
        return pygame.image.load(filename)
    except Exception:
        surf = pygame.Surface((50, 50))
        surf.fill(color)
        return surf

player_img = load_image("player.png", (0, 255, 0))        # მწვანე
enemy_img = load_image("enemy.png", (255, 0, 0))          # წითელი
boss_img = load_image("boss.png", (128, 0, 128))        # იისფერი
assistant_img = load_image("asistent.png", (0, 255, 255)) # ცისფერი

player_x, player_y = 100, 400
speed = 5
clock = pygame.time.Clock()

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        player_x -= speed
    if keys[pygame.K_RIGHT]:
        player_x += speed
    if keys[pygame.K_UP]:
        player_y -= speed
    if keys[pygame.K_DOWN]:
        player_y += speed

    screen.fill((30, 30, 30))

    screen.blit(player_img, (player_x, player_y))
    screen.blit(enemy_img, (500, 200))
    screen.blit(boss_img, (600, 100))
    screen.blit(assistant_img, (50, 100))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
