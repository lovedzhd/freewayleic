import pygame
import os
import random
import math
pygame.font.init()
pygame.mixer.init()

WIDTH, HEIGHT = 768, 512
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Freeway")

WHITE = (255, 255, 255)

POINT_FONT = pygame.font.SysFont('comicsans', 64)
TIMER_FONT = pygame.font.SysFont('comicsans', 32)
FINAL_FONT = pygame.font.SysFont('comicsans', 16)

TRAFFIC_SOUND = pygame.mixer.Sound("material/traffic_sound.wav")
POINT_SOUND = pygame.mixer.Sound("material/point.wav")

FPS = 60
PLAYER_VEL = 2
HIT_VEL = 5
REDTRUCK_VEL = 3

hit1_event = pygame.USEREVENT + 1
hit2_event = pygame.USEREVENT + 2
point1_event = pygame.USEREVENT + 3
point2_event = pygame.USEREVENT + 4
walk1_event = pygame.USEREVENT + 5
walk2_event = pygame.USEREVENT + 6

#(skin, vel, length)
vehicle_types = (
    ("blue_truck.png", 1, 64),
    ("green_truck.png", 2, 64),
    ("red_truck.png", 3, 64),
    ("yellow_truck.png", 4, 64),
    ("grey_car.png", 4, 32),
    ("pink_car.png", 2, 32),
    ("yellow_car.png", 5, 32),
    ("white_car.png", 6, 32),
)

START_SOLO_WIDTH, START_MULTI1_WIDTH, START_MULTI2_WIDTH, START_HEIGHT, POINT_HEIGHT = WIDTH//2 - 12, WIDTH// 4 - 12, WIDTH*3//4 - 12, HEIGHT - 60, 32*3 + 4
lanelist = [32*13, 32*12, 32*11, 32*10, 32*9, 32*8, 32*7, 32*6, 32*5, 32*4]

for i in range(0, 10):
    lanelist[i] += 4

PLAYER_SPRITES = []
for i in range(0, 4):
    PLAYER_SPRITES.append(pygame.image.load(os.path.join('material', 'main_char' + str(i) + ".png")))
TEST_TRUCK = pygame.image.load(os.path.join('material', 'red_truck.png'))
MAPA = pygame.image.load(os.path.join('material', 'mapa teste.png'))


def draw_window(player1, player2, trucks, point1, point2, countdown, currentsprite1, currentsprite2):
    WIN.fill(WHITE)
    WIN.blit(MAPA, (0, 0))

    point1_text = POINT_FONT.render(str(point1), True, WHITE)
    point2_text = POINT_FONT.render(str(point2), True, WHITE)
    timer_text = TIMER_FONT.render(str(math.ceil(countdown/60)), True, WHITE)

    WIN.blit(point1_text, (WIDTH//4 - point1_text.get_width() // 2, 0))
    WIN.blit(point2_text, (WIDTH*3 // 4 - point2_text.get_width() // 2, 0))
    WIN.blit(timer_text, (WIDTH // 2 - timer_text.get_width() // 2, 0))

    WIN.blit(PLAYER_SPRITES[math.floor(currentsprite1/10)], (player1.x-4, player1.y-4))
    WIN.blit(PLAYER_SPRITES[math.floor(currentsprite2/10)], (player2.x-4, player2.y-4))
    for truck, trucktype, direction in trucks:
        if direction == 1:
            WIN.blit(pygame.image.load(os.path.join('material', trucktype[0])), (truck.x, truck.y))
        else:
            WIN.blit(pygame.transform.flip(pygame.image.load(os.path.join('material', trucktype[0])), True, False), (truck.x, truck.y))
    pygame.display.update()


def player1_movement(keys_pressed, player1, trucks):
    for truck, trucktype, direction in trucks:
        if player1.colliderect(truck):
            pygame.event.post(pygame.event.Event(hit1_event))
    if player1.y <= POINT_HEIGHT:
        player1.y = START_HEIGHT
        pygame.event.post(pygame.event.Event(point1_event))
    if keys_pressed[pygame.K_w]:
        player1.y -= PLAYER_VEL
        pygame.event.post(pygame.event.Event(walk1_event))
    if keys_pressed[pygame.K_s] and player1.y < HEIGHT - 60:
        player1.y += PLAYER_VEL
        pygame.event.post(pygame.event.Event(walk1_event))


def player1_hit(player1, fallheight1):
    if player1.y > HEIGHT - 60:
        player1.y = START_HEIGHT
        pygame.event.post(pygame.event.Event(hit1_event))
    elif player1.y >= fallheight1 + HIT_VEL:
        player1.y = fallheight1
        pygame.event.post(pygame.event.Event(hit1_event))
    else:
        player1.y += HIT_VEL


def player2_movement(keys_pressed, player2, trucks):
    for truck, trucktype, direction in trucks:
        if player2.colliderect(truck):
            pygame.event.post(pygame.event.Event(hit2_event))
    if player2.y <= POINT_HEIGHT:
        player2.y = START_HEIGHT
        pygame.event.post(pygame.event.Event(point2_event))
    if keys_pressed[pygame.K_UP]:
        player2.y -= PLAYER_VEL
        pygame.event.post(pygame.event.Event(walk2_event))
    if keys_pressed[pygame.K_DOWN] and player2.y < HEIGHT - 60:
        player2.y += PLAYER_VEL
        pygame.event.post(pygame.event.Event(walk2_event))


def player2_hit(player2, fallheight2):
    if player2.y > HEIGHT - 60:
        player2.y = START_HEIGHT
        pygame.event.post(pygame.event.Event(hit2_event))
    elif player2.y >= fallheight2 + HIT_VEL:
        player2.y = fallheight2
        pygame.event.post(pygame.event.Event(hit2_event))
    else:
        player2.y += HIT_VEL


def truck_movement(trucks):
    for truck, trucktype, direction in trucks:
        if direction == 1:
            if truck.x <= -truck.width:
                truck.x = WIDTH
            else:
                truck.x -= trucktype[1]
        else:
            if truck.x >= WIDTH + truck.width:
                truck.x = -truck.width
            else:
                truck.x += trucktype[1]


def main():
    player1 = pygame.Rect(START_MULTI1_WIDTH, START_HEIGHT, 24, 24)
    currentsprite1 = 0
    player2 = pygame.Rect(START_MULTI2_WIDTH, START_HEIGHT, 24, 24)
    currentsprite2 = 0

    trucks = []

    selected_types = random.sample(vehicle_types, 5) + random.sample(vehicle_types, 5)
    for i in range(0, 5):
        number_of_trucks = random.randint(1, 2)
        trucktype = selected_types[i]
        place = random.randint(0, WIDTH)
        truck = (pygame.Rect(place, lanelist[i], trucktype[2], 24))
        direction = 1
        trucks.append((truck, trucktype, direction))
        if number_of_trucks == 2:
            truck = (pygame.Rect(place + direction * trucktype[2] * 3, lanelist[i], trucktype[2], 24))
            trucks.append((truck, trucktype, direction))

    for i in range(5, 10):
        number_of_trucks = random.randint(1, 2)
        trucktype = selected_types[i]
        place = random.randint(0, WIDTH)
        truck = (pygame.Rect(place, lanelist[i], trucktype[2], 24))
        direction = -1
        trucks.append((truck, trucktype, direction))
        if number_of_trucks == 2:
            truck = (pygame.Rect(place + direction*trucktype[2]*3, lanelist[i], trucktype[2], 24))
            trucks.append((truck, trucktype, direction))

    hit1, hit2 = False, False

    point1, point2 = 0, 0

    fallheight1, fallheight2 = 0, 0

    countdown = 60*60

    TRAFFIC_SOUND.play()

    clock = pygame.time.Clock()
    run = True
    while run:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()

            if event.type == hit1_event:
                fallheight1 = player1.y + 96
                hit1 = not hit1
            if event.type == hit2_event:
                fallheight2 = player2.y + 96
                hit2 = not hit2

            if event.type == point1_event:
                POINT_SOUND.play()
                point1 += 1
            if event.type == point2_event:
                POINT_SOUND.play()
                point2 += 1

            if event.type == walk1_event:
                currentsprite1 += 1
                if currentsprite1 == 40:
                    currentsprite1 = 0
            if event.type == walk2_event:
                currentsprite2 += 1
                if currentsprite2 == 40:
                    currentsprite2 = 0

        countdown -= 1

        keys_pressed = pygame.key.get_pressed()

        if hit1:
            player1_hit(player1, fallheight1)
        else:
            player1_movement(keys_pressed, player1, trucks)
        if hit2:
            player2_hit(player2, fallheight2)
        else:
            player2_movement(keys_pressed, player2, trucks)

        truck_movement(trucks)

        draw_window(player1, player2, trucks, point1, point2, countdown, currentsprite1, currentsprite2)

        if countdown == 0:
            if point1 > point2:
                final_msg = "Jogador 1 ganhou!"
            elif point2 > point1:
                final_msg = "Jogador 2 ganhou!"
            else:
                final_msg = "Empate."

            final_text = FINAL_FONT.render(final_msg, True, WHITE)
            WIN.blit(final_text, (WIDTH // 2 - final_text.get_width() // 2, 48))
            pygame.display.update()
            pygame.time.delay(5000)
            run = False
    main()


if __name__ == "__main__":
    main()