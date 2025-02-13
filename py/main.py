import pygame
import sys
import random
import json

pygame.init()

SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 700
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
sound_played = False
SPAWN_OFFSET = 50
SPAWN_ROTATION = 180
pygame.display.set_caption("Танки")
RED_TANK_IMAGE = pygame.image.load('images/redtank.png').convert_alpha()
RED_TANK_IMAGE = pygame.transform.scale(RED_TANK_IMAGE, (50, 50))
BLUE_TANK_IMAGE = pygame.image.load('images/bluetank.png').convert_alpha()
BLUE_TANK_IMAGE = pygame.transform.scale(BLUE_TANK_IMAGE, (50, 50))
BULLET_IMAGE = pygame.image.load('images/bullet.png').convert_alpha()
OBSTACLE_IMAGE = pygame.image.load('images/obstacle.png').convert_alpha()
OBSTACLE_IMAGE = pygame.transform.scale(OBSTACLE_IMAGE, (75, 75))
BULLET_IMAGE = pygame.transform.scale(BULLET_IMAGE, (15, 15))
MENU_BACKGROUND_IMAGE = pygame.image.load('images/background.png')
GAME_BACKGROUND_IMAGE = pygame.image.load('images/desert_bg.png')
RED_HEART_IMAGE = pygame.image.load('images/redhp.png').convert_alpha()
BLUE_HEART_IMAGE = pygame.image.load('images/bluehp.png').convert_alpha()

BORDER_LEFT = 20
BORDER_RIGHT = SCREEN_WIDTH - 20
BORDER_TOP = 20
BORDER_BOTTOM = SCREEN_HEIGHT - 80

TILE_WIDTH = GAME_BACKGROUND_IMAGE.get_width()
TILE_HEIGHT = GAME_BACKGROUND_IMAGE.get_height()

MAPS_FILE = "maps.json"
CURRENT_MAP_KEY = "last_selected_map"


class MapManager:
    def __init__(self):
        self.maps = self.load_maps()
        self.current_map_index = 0

    def load_maps(self):
        try:
            with open(MAPS_FILE, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            default_maps = [
                {
                    "name": "Пустыня",
                    "background": "images/desert_bg.png",
                    "obstacles": []
                },
                {
                    "name": "Город",
                    "background": "images/city_bg.png",
                    "obstacles": []
                },
                {
                    "name": "Лес",
                    "background": "images/forest_bg.png",
                    "obstacles": []
                }
            ]
            with open(MAPS_FILE, 'w') as f:
                json.dump(default_maps, f)
            return default_maps

    def get_current_map(self):
        return self.maps[self.current_map_index]

    def next_map(self):
        self.current_map_index = (self.current_map_index + 1) % len(self.maps)

    def prev_map(self):
        self.current_map_index = (self.current_map_index - 1) % len(self.maps)

    def save_current_map(self):
        settings = {CURRENT_MAP_KEY: self.get_current_map()["name"]}
        with open('settings.json', 'w') as f:
            json.dump(settings, f)


def generate_background(surface, map_manager):
    try:
        tile_image = pygame.image.load(map_manager.get_current_map()["background"]).convert()
        width, height = surface.get_size()
        num_tiles_x = (width // tile_image.get_width()) + 1
        num_tiles_y = (height // tile_image.get_height()) + 1

        for i in range(num_tiles_x):
            for j in range(num_tiles_y):
                surface.blit(tile_image, (i * tile_image.get_width(), j * tile_image.get_height()))
    except Exception as e:
        print(f"ошибка загрузки фона: {e}")


def draw_world_borders():
    border_color = (100, 100, 100)
    pygame.draw.rect(screen, border_color, (0, 0, SCREEN_WIDTH, BORDER_TOP))
    pygame.draw.rect(screen, border_color, (0, BORDER_BOTTOM, SCREEN_WIDTH, SCREEN_HEIGHT - BORDER_BOTTOM))
    pygame.draw.rect(screen, border_color, (0, 0, BORDER_LEFT, SCREEN_HEIGHT))
    pygame.draw.rect(screen, border_color, (BORDER_RIGHT, 0, SCREEN_WIDTH - BORDER_RIGHT, SCREEN_HEIGHT))


def get_random_spawn_positions():#подправить
    if random.random() < 0.5:
        red_pos = (BORDER_RIGHT - SPAWN_OFFSET, BORDER_TOP + SPAWN_OFFSET)
        blue_pos = (BORDER_LEFT + SPAWN_OFFSET, BORDER_BOTTOM - SPAWN_OFFSET)
        red_angle = 225
        blue_angle = 45
    else:
        red_pos = (BORDER_LEFT + SPAWN_OFFSET, BORDER_TOP + SPAWN_OFFSET)
        blue_pos = (BORDER_RIGHT - SPAWN_OFFSET, BORDER_BOTTOM - SPAWN_OFFSET)
        red_angle = 315
        blue_angle = 135

    return red_pos, blue_pos, red_angle, blue_angle

def draw_hud():
    hud_height = 80
    pygame.draw.rect(screen, (40, 40, 40), (0, SCREEN_HEIGHT - hud_height, SCREEN_WIDTH, hud_height))

    heart_size = RED_HEART_IMAGE.get_size()

    spacing = 5
    start_y = SCREEN_HEIGHT - 60

    start_x_tank1 = SCREEN_WIDTH // 2 + 200
    for i in range(Tank1.health):
        screen.blit(RED_HEART_IMAGE, (start_x_tank1 + i * (heart_size[0] + spacing) - 150, start_y))

    start_x_tank2 = SCREEN_WIDTH // 2 - 300
    for i in range(Tank2.health):
        screen.blit(BLUE_HEART_IMAGE, (start_x_tank2 + i * (heart_size[0] + spacing) + 150, start_y))

    bullet_x_tank1 = 20
    bullet_y_tank1 = SCREEN_HEIGHT - 30
    for _ in range(Tank1.bullets_in_magazine):
        pygame.draw.rect(screen, (255, 223, 0), (bullet_x_tank1, bullet_y_tank1, 15, 25))
        bullet_x_tank1 += 25

    bullet_x_tank2 = SCREEN_WIDTH - 20 - 15
    bullet_y_tank2 = SCREEN_HEIGHT - 30
    for _ in range(Tank2.bullets_in_magazine):
        pygame.draw.rect(screen, (255, 223, 0), (bullet_x_tank2, bullet_y_tank2, 15, 25))
        bullet_x_tank2 -= 25

    if Tank1.is_reloading:
        reload_progress_tank1 = Tank1.get_reload_progress()
        pygame.draw.rect(screen, (80, 80, 80), (20, SCREEN_HEIGHT - 75, 200, 10))
        pygame.draw.rect(screen, (0, 255, 0), (20, SCREEN_HEIGHT - 75, int(200 * reload_progress_tank1), 10))

    if Tank2.is_reloading:
        reload_progress_tank2 = Tank2.get_reload_progress()
        pygame.draw.rect(screen, (80, 80, 80), (SCREEN_WIDTH - 220, SCREEN_HEIGHT - 75, 200, 10))
        pygame.draw.rect(screen, (0, 255, 0), (SCREEN_WIDTH - 220, SCREEN_HEIGHT - 75, int(200 * reload_progress_tank2), 10))

class Tank(pygame.sprite.Sprite):
    def __init__(self, color, start_pos, start_angle=0, speed=2):
        super().__init__()
        self.original_image = RED_TANK_IMAGE if color == 'red' else BLUE_TANK_IMAGE
        self.image = pygame.transform.rotate(self.original_image, start_angle)
        self.rect = self.image.get_rect(center=start_pos)
        self.pos = pygame.math.Vector2(start_pos)
        self.angle = start_angle
        self.speed = speed
        self.bullets = pygame.sprite.Group()
        self.health = 3
        self.shots_fired = 0
        self.hits = 0
        self.reloading_bullet_index = 0
        self.moving = False
        self.magazine_size = 5
        self.bullets_in_magazine = 5
        self.last_shot_time = 0
        self.reload_start_time = 0
        self.is_reloading = False
        self.reload_per_bullet = 3000
        self.shot_cooldown = 500

    def rotate(self, delta_angle):
        self.angle = (self.angle + delta_angle) % 360
        self.image = pygame.transform.rotozoom(self.original_image, self.angle, 1)
        old_center = self.rect.center
        self.rect = self.image.get_rect()
        self.rect.center = old_center

    def draw(self, surface):
        surface.blit(self.image, self.rect)

    def get_reload_progress(self):
        if not self.is_reloading:
            return 0.0
        current_time = pygame.time.get_ticks()
        time_since_last = current_time - self.reload_start_time
        return min(time_since_last / self.reload_per_bullet, 1.0)

    def move_forward(self):
        move_direction = pygame.math.Vector2(1, 0).rotate(-self.angle)
        new_pos = self.pos + move_direction * self.speed

        if (BORDER_LEFT < new_pos.x < BORDER_RIGHT and
                BORDER_TOP < new_pos.y < BORDER_BOTTOM):
            old_pos = self.pos

            self.pos = new_pos
            self.rect.center = self.pos

            for obstacle in obstacles:
                if pygame.sprite.collide_rect(self, obstacle):
                    adjust_position_on_collision(self, obstacle)
                    break

    def move_backward(self):
        move_direction = pygame.math.Vector2(1, 0).rotate(-self.angle)
        new_pos = self.pos - move_direction * self.speed

        if (BORDER_LEFT < new_pos.x < BORDER_RIGHT and
                BORDER_TOP < new_pos.y < BORDER_BOTTOM):
            old_pos = self.pos

            self.pos = new_pos
            self.rect.center = self.pos
            for obstacle in obstacles:
                if pygame.sprite.collide_rect(self, obstacle):
                    adjust_position_on_collision(self, obstacle)
                    break

    def stop_moving(self):
        moving = False

    def shoot(self):
        current_time = pygame.time.get_ticks()

        if self.is_reloading:
            return

        if current_time - self.last_shot_time < self.shot_cooldown:
            return

        if self.bullets_in_magazine > 0:
            self.bullets.add(Bullet(self.pos, self.angle))
            self.bullets_in_magazine -= 1
            self.shots_fired += 1
            self.last_shot_time = current_time

            if self.bullets_in_magazine == 0:
                self.start_reload()
            else:
                self.is_reloading = False

    def start_reload(self):
        if not self.is_reloading and self.bullets_in_magazine < self.magazine_size:
            self.is_reloading = True
            self.reload_start_time = pygame.time.get_ticks()

    def update_reload(self):
        if self.is_reloading:
            current_time = pygame.time.get_ticks()
            time_since_reload = current_time - self.reload_start_time

            time_per_bullet = self.reload_per_bullet
            bullets_reloaded = min(
                self.magazine_size - self.bullets_in_magazine,
                time_since_reload // time_per_bullet
            )

            self.reloading_bullet_index = bullets_reloaded

            if bullets_reloaded > 0:
                self.bullets_in_magazine += bullets_reloaded
                self.reload_start_time += bullets_reloaded * time_per_bullet

                if self.bullets_in_magazine == self.magazine_size:
                    self.is_reloading = False


    def update_bullets(self, surface):
        self.bullets.update()
        self.bullets.draw(surface)


class Bullet(pygame.sprite.Sprite):
    def __init__(self, position, tank_angle, speed=10):
        super().__init__()
        self.image = BULLET_IMAGE
        self.rect = self.image.get_rect(center=position)
        self.position = pygame.math.Vector2(position)
        self.direction = pygame.math.Vector2(1, 0).rotate(-tank_angle)
        self.speed = speed

    def update(self):
        self.position += self.direction * self.speed
        self.rect.center = self.position

        if not screen.get_rect().contains(self.rect):
            self.kill()


class Obstacle(pygame.sprite.Sprite):
    def __init__(self, size, image):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect()

    def set_position(self, pos):
        self.rect.topleft = pos

    def draw(self, surface):
        surface.blit(self.image, self.rect)
        pygame.draw.rect(screen, self.color, self.body_rect)

def load_last_selected_map(map_manager):
    try:
        with open('settings.json', 'r') as f:
            settings = json.load(f)
            if isinstance(settings, dict):
                current_map_name = settings.get(CURRENT_MAP_KEY)
                if current_map_name:
                    for i, map_data in enumerate(map_manager.maps):
                        if map_data["name"] == current_map_name:
                            map_manager.current_map_index = i
                            break
            else:
                raise ValueError
    except (FileNotFoundError, json.JSONDecodeError, ValueError):
        map_manager.current_map_index = 0
        save_last_selected_map(map_manager.get_current_map()["name"])


def save_last_selected_map(map_name):
    with open('settings.json', 'w') as file:
        json.dump({CURRENT_MAP_KEY: map_name}, file)

def adjust_position_on_collision(tank, obstacle):
    move_direction = pygame.math.Vector2(1, 0).rotate(-tank.angle)
    delta_x = obstacle.rect.centerx - tank.rect.centerx
    delta_y = obstacle.rect.centery - tank.rect.centery

    distance = pygame.math.Vector2(delta_x, delta_y).length()

    if distance < (tank.rect.width / 2 + obstacle.rect.width / 2):
        normal_x = delta_x / distance
        normal_y = delta_y / distance

        overlap = (tank.rect.width / 2 + obstacle.rect.width / 2) - distance

        tank.pos.x -= overlap * normal_x
        tank.pos.y -= overlap * normal_y
        tank.rect.center = tank.pos

def adjust_positions_on_collision(tank1, tank2):
    delta_x = tank2.pos.x - tank1.pos.x
    delta_y = tank2.pos.y - tank1.pos.y

    distance = pygame.math.Vector2(delta_x, delta_y).length()

    if distance < (tank1.rect.width / 2 + tank2.rect.width / 2):
        normal_x = delta_x / distance
        normal_y = delta_y / distance
        overlap = (tank1.rect.width / 2 + tank2.rect.width / 2) - distance

        tank1.pos.x -= overlap * normal_x / 2
        tank1.pos.y -= overlap * normal_y / 2
        tank2.pos.x += overlap * normal_x / 2
        tank2.pos.y += overlap * normal_y / 2

        tank1.rect.center = tank1.pos
        tank2.rect.center = tank2.pos


def show_end_screen(tank1, tank2):
    global game_over, sound_played, Tank1, Tank2, obstacles, OBSTACLE_COORDINATES

    screen.fill((255, 255, 255))
    if tank1.health > 0:
        winner_text = "Первый танк победил!"
    else:
        winner_text = "Второй танк победил!"

    lines = [
        f"{winner_text}",
        "",
        f"Первый танк:",
        f"Выстрелы: {tank1.shots_fired}",
        f"Попадания: {tank1.hits}",
        f"HP: {tank1.health}",
        "",
        f"Второй танк:",
        f"Выстрелы: {tank2.shots_fired}",
        f"Попадания: {tank2.hits}",
        f"HP: {tank2.health}"
    ]

    y_offset = SCREEN_HEIGHT // 4
    for line in lines:
        text_surface = font.render(line, True, (0, 0, 0))
        x_pos = (SCREEN_WIDTH - text_surface.get_width()) // 2
        screen.blit(text_surface, (x_pos, y_offset))
        y_offset += 40

    restart_button = pygame.Rect(SCREEN_WIDTH // 2 - 100, y_offset + 20, 200, 50)
    pygame.draw.rect(screen, (0, 255, 0), restart_button)
    restart_text = font.render("Рестарт", True, (0, 0, 0))
    text_rect = restart_text.get_rect(center=restart_button.center)
    screen.blit(restart_text, text_rect)

    mouse_pos = pygame.mouse.get_pos()
    mouse_click = pygame.mouse.get_pressed()

    if restart_button.collidepoint(mouse_pos) and mouse_click[0]:
        game_over = False
        sound_played = False

        red_pos, blue_pos, red_angle, blue_angle = get_random_spawn_positions()
        Tank1 = Tank(color='red', start_pos=red_pos, start_angle=red_angle)
        Tank2 = Tank(color='blue', start_pos=blue_pos, start_angle=blue_angle)

        OBSTACLE_COORDINATES = generate_random_barricade(7)
        obstacles = pygame.sprite.Group()
        for coord in OBSTACLE_COORDINATES:
            obstacle = Obstacle(obstacle_size, OBSTACLE_IMAGE)
            obstacle.set_position(coord)
            obstacles.add(obstacle)

        return

    pygame.display.flip()


def main_menu(map_manager):
    global start_button, exit_button, map_left_button, map_right_button

    custom_font = pygame.font.Font("shcrift/Tank.otf", 36)


    start_button = pygame.Rect(500, 400, 200, 50)
    exit_button = pygame.Rect(500, 470, 200, 50)
    map_left_button = pygame.Rect(20, 20, 50, 50)
    map_right_button = pygame.Rect(80, 20, 50, 50)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = event.pos
                if start_button.collidepoint(mouse_pos):
                    map_manager.save_current_map()
                    start_sound.play()
                    return
                if exit_button.collidepoint(mouse_pos):
                    pygame.quit()
                    sys.exit()
                if map_left_button.collidepoint(mouse_pos):
                    map_manager.prev_map()
                if map_right_button.collidepoint(mouse_pos):
                    map_manager.next_map()


        screen.fill((0, 0, 0))
        screen.blit(MENU_BACKGROUND_IMAGE, (0, 0))


        current_map = map_manager.get_current_map()
        map_text = custom_font.render(f"Карта: {current_map['name']}", True, (255, 255, 255))
        screen.blit(map_text, (20, 80))

        pygame.draw.rect(screen, (100, 100, 100), start_button)
        pygame.draw.rect(screen, (50, 50, 50), exit_button)
        pygame.draw.rect(screen, (150, 150, 150), map_left_button)
        pygame.draw.rect(screen, (150, 150, 150), map_right_button)

        def draw_centered_text(button, text, font, text_color):
            text_surface = font.render(text, True, text_color)
            text_rect = text_surface.get_rect(center=button.center)
            screen.blit(text_surface, text_rect)


        draw_centered_text(start_button, "Начать игру", custom_font, (255, 255, 255))
        draw_centered_text(exit_button, "Выход", custom_font, (255, 255, 255))
        draw_centered_text(map_left_button, "<", custom_font, (0, 0, 0))
        draw_centered_text(map_right_button, ">", custom_font, (0, 0, 0))

        # Обновление экрана
        pygame.display.flip()
        clock.tick(60)

map_manager = MapManager()
load_last_selected_map(map_manager)
red_pos, blue_pos, red_angle, blue_angle = get_random_spawn_positions()

Tank1 = Tank(color='red',start_pos=red_pos,start_angle=red_angle)
Tank2 = Tank(color='blue',start_pos=blue_pos,start_angle=blue_angle)

obstacle = pygame.sprite.Group()
obstacle_size = 50
def generate_random_barricade(num_obstacles):
    obstacles = []
    obstacle_size = 75

    for _ in range(num_obstacles):
        while True:
            x = random.randint(BORDER_LEFT, BORDER_RIGHT - obstacle_size)
            y = random.randint(BORDER_TOP, BORDER_BOTTOM - obstacle_size)

            if (abs(x - red_pos[0]) < 100 and abs(y - red_pos[1]) < 100) or \
               (abs(x - blue_pos[0]) < 100 and abs(y - blue_pos[1]) < 100):
                continue
            collision = False
            for (ox, oy) in obstacles:
                if (x < ox + obstacle_size and x + obstacle_size > ox and
                    y < oy + obstacle_size and y + obstacle_size > oy):
                    collision = True
                    break

            if not collision:
                obstacles.append((x, y))
                break
    return obstacles

OBSTACLE_COORDINATES = generate_random_barricade(7)

obstacles = pygame.sprite.Group()
for coord in OBSTACLE_COORDINATES:
    obstacle = Obstacle(obstacle_size, OBSTACLE_IMAGE)
    obstacle.set_position(coord)
    obstacles.add(obstacle)



clock = pygame.time.Clock()
running = True
game_over = False

font = pygame.font.Font(None, 32)

start_button = pygame.Rect(350, 250, 100, 50)
exit_button = pygame.Rect(350, 320, 100, 50)

pygame.mixer.init()
hit_sound = pygame.mixer.Sound('music/hit.wav')
start_sound = pygame.mixer.Sound('music/start.wav')
end_sound = pygame.mixer.Sound('music/end.wav')
ricochet_sound = pygame.mixer.Sound('music/ricochet.wav')

selected_map = map_manager.get_current_map()["name"]

main_menu(map_manager)

while running:
    pygame.event.pump()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if not game_over:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    Tank1.shoot()
                if event.key == pygame.K_RETURN:
                    Tank2.shoot()

    if not game_over:
        for bullet in Tank1.bullets.sprites() + Tank2.bullets.sprites():
            if pygame.sprite.spritecollide(bullet, obstacles, False):
                bullet.kill()

        keys = pygame.key.get_pressed()
        if keys[pygame.K_a]:
            Tank1.rotate(3)
        if keys[pygame.K_d]:
            Tank1.rotate(-3)
        if keys[pygame.K_w]:
            Tank1.move_forward()
        if keys[pygame.K_s]:
            Tank1.move_backward()

        if keys[pygame.K_LEFT]:
            Tank2.rotate(3)
        if keys[pygame.K_RIGHT]:
            Tank2.rotate(-3)
        if keys[pygame.K_UP]:
            Tank2.move_forward()
        if keys[pygame.K_DOWN]:
            Tank2.move_backward()

        if pygame.sprite.collide_rect(Tank1, obstacle):
            Tank1.stop_moving()
        if pygame.sprite.collide_rect(Tank2, obstacle):
            Tank2.stop_moving()

        Hit_tan1 = pygame.sprite.spritecollide(Tank1, Tank2.bullets, True)
        Hit_tank2 = pygame.sprite.spritecollide(Tank2, Tank1.bullets, True)

        if Hit_tan1:
            for bullet in Hit_tan1:
                if random.random() < 0.1:
                    bullet.kill()
                    ricochet_sound.play()
                else:
                    Tank1.health -= 1
                    Tank2.hits += 1
                    hit_sound.play()

        if Hit_tank2:
            for bullet in Hit_tank2:
                if random.random() < 0.1:
                    bullet.kill()
                    ricochet_sound.play()
                else:
                    Tank2.health -= 1
                    Tank1.hits += 1
                    hit_sound.play()

        if Tank1.rect.colliderect(Tank2.rect):
            adjust_positions_on_collision(Tank1, Tank2)
            Tank1.stop_moving()
            Tank2.stop_moving()

        for bullet in Tank1.bullets.sprites() + Tank2.bullets.sprites():
            if pygame.sprite.collide_rect(bullet, obstacle):
                bullet.kill()

        if pygame.sprite.collide_rect(Tank1, obstacle):
            Tank1.stop_moving()
        if pygame.sprite.collide_rect(Tank2, obstacle):
            Tank2.stop_moving()

        if Tank1.health <= 0 or Tank2.health <= 0:
            game_over = True
            if not sound_played:
                end_sound.play()
                sound_played = True

    if not game_over:
        generate_background(screen, map_manager)
        draw_world_borders()

        Tank1.draw(screen)
        Tank2.draw(screen)

        Tank1.update_bullets(screen)
        Tank2.update_bullets(screen)
        obstacles.draw(screen)
        draw_hud()

        if Tank1.health <= 0:
            Tank1.kill()
        if Tank2.health <= 0:
            Tank2.kill()

        Tank1.update_reload()
        Tank2.update_reload()
    else:
        show_end_screen(Tank1, Tank2)

    pygame.display.flip()
    clock.tick(60)

save_last_selected_map(selected_map)
pygame.quit()
sys.exit()