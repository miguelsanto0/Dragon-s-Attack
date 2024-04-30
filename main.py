import pygame
import sys
import random
import math

# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

# Colors
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
WHITE = (255, 255, 255)


def draw_text(text, font, color, surface, x, y):
    textobj = font.render(text, True, color)
    textrect = textobj.get_rect()
    textrect.topleft = (x, y)
    surface.blit(textobj, textrect)


pygame.display.set_caption("Dragon's Attack")

clock = pygame.time.Clock()

font = pygame.font.Font(None, 36)

global_score = 0
player_speed_boost = 1
player_health_boost = 1
player_jump_boost = 1

GAME_STATE = "MAIN_MENU"


def main_menu():
    global GAME_STATE
    global player_speed_boost
    global player_jump_boost
    global player_health_boost
    click = False
    while True:
        Menu_image = pygame.image.load('Title.jpg')
        Menu_image = pygame.transform.scale(Menu_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
        screen.blit(Menu_image, (0, 0))

        mx, my = pygame.mouse.get_pos()

        button_start = pygame.Rect(SCREEN_WIDTH // 2 - 50, SCREEN_HEIGHT // 2, 100, 50)
        if button_start.collidepoint((mx, my)):
            if click:
                GAME_STATE = "PLAYING"
                return  # Exit the main_menu function to start playing

        pygame.draw.rect(screen, WHITE, button_start)
        draw_text('Start', font, BLACK, screen, SCREEN_WIDTH // 2 - 30, SCREEN_HEIGHT // 2 + 10)

        click = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    click = True

        pygame.display.update()


def game():
    # Load the sprite sheet
    background_image = pygame.image.load('Pixilated_village_background.png')
    sprite_sheet = pygame.image.load('dragon_sprite.png')
    player_old_man_sprite = pygame.image.load('Old_man_walk.png')
    player_old_man_idle_sprite = pygame.image.load('Old_man_idle.png')
    fireball_image = pygame.image.load('Fireball.png')
    fireball_image = pygame.transform.scale(fireball_image, (30, 30))

    background_image = pygame.transform.scale(background_image, (SCREEN_WIDTH, SCREEN_HEIGHT))

    sheet_width, sheet_height = player_old_man_sprite.get_size()

    # idle for old man
    old_idle_width, old_idle_height = player_old_man_idle_sprite.get_size()

    running_sprite_width = sheet_width // 6
    running_sprite_height = sheet_height

    idle_old_man_sprite_width = old_idle_width // 4
    idle_old_man_sprite_height = old_idle_height

    idle_frames = [player_old_man_idle_sprite.subsurface(
        pygame.Rect(i * idle_old_man_sprite_width, 0, idle_old_man_sprite_width, idle_old_man_sprite_height)) for i in
        range(4)
    ]

    running_frames = [
        player_old_man_sprite.subsurface(
            pygame.Rect(i * running_sprite_width, 0, running_sprite_height, running_sprite_height))
        for i in range(6)
    ]

    sheet_width, sheet_height = sprite_sheet.get_size()

    DRAGON_SPRITE_WIDTH = sheet_width // 3
    DRAGON_SPRITE_HEIGHT = sheet_height

    dragon_frames = [
        sprite_sheet.subsurface(pygame.Rect(i * DRAGON_SPRITE_WIDTH, 0, DRAGON_SPRITE_WIDTH, DRAGON_SPRITE_HEIGHT))
        for i in range(3)
    ]

    # Animation variables
    current_frame = 0
    frame_counter = 0

    # Player animation variables
    player_current_frame = 0
    player_frame_counter = 0
    last_direction = 'right'

    # Dragon properties
    HALF_HEIGHT = SCREEN_HEIGHT // 2
    dragon_pos = [SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4]  # Initial position for the dragon
    dragon_speed = 2
    wave_amplitude = 20
    wave_frequency = 0.05
    dragon_direction = 1

    # Player properties
    player_pos = [SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50]
    player_speed = 5 * player_speed_boost
    player_health = 3 * player_health_boost  # New health variable

    # Fireballs
    fireballs = []
    fireball_speed = 7

    is_jumping = False
    jump_speed = 7
    gravity = 1 / player_jump_boost
    vertical_speed = jump_speed

    running = True

    num_idle_frames = len(idle_frames)
    num_running_frames = len(running_frames)
    # Game loop
    global GAME_STATE
    global global_score
    while running and GAME_STATE == "PLAYING":
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.blit(background_image, (0, 0))

        # Movement controls
        is_running = False
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and player_pos[0] > 0:
            player_pos[0] -= player_speed
            is_running = True
            last_direction = 'left'

        elif keys[pygame.K_RIGHT] and player_pos[0] < SCREEN_WIDTH - 20:
            player_pos[0] += player_speed
            is_running = True
            last_direction = 'right'

        if not is_jumping:
            if keys[pygame.K_UP]:
                is_jumping = True

        if is_running:
            player_frame_counter += 1
            if player_frame_counter >= 5:
                player_frame_counter = 0
                player_current_frame = (player_current_frame + 1) % num_running_frames
        elif not is_jumping:
            player_frame_counter += 1
            if player_frame_counter >= 15:
                player_frame_counter = 0
                player_current_frame = (player_current_frame + 1) % num_idle_frames

        if not is_running and not is_jumping:
            player_current_frame = 0

        # Handle jumping
        if is_jumping:
            player_pos[1] -= vertical_speed  # Move player up
            vertical_speed -= gravity  # Decrease vertical speed due to gravity
            if vertical_speed < -jump_speed:  # Player has reached the peak of the jump
                is_jumping = False  # Reset jumping state
                vertical_speed = jump_speed  # Reset vertical speed

        if player_pos[1] > SCREEN_HEIGHT - 50:
            player_pos[1] = SCREEN_HEIGHT - 50

        dragon_pos[0] += dragon_speed * dragon_direction

        # Reverse direction at screen edges
        if dragon_pos[0] >= SCREEN_WIDTH or dragon_pos[0] <= 0:
            dragon_direction *= -1
            current_frame = 0

        dragon_pos[1] = HALF_HEIGHT // 2 + wave_amplitude * math.sin(wave_frequency * dragon_pos[0])

        if random.randint(1, 30) == 1:
            fireballs.append([dragon_pos[0], dragon_pos[1]])

        frame_counter += 1
        if frame_counter >= 5:
            frame_counter = 0
            current_frame = (current_frame + 1) % 3

        # Moving fireballs
        for fireball in fireballs:
            fireball[1] += fireball_speed
            if fireball[1] >= SCREEN_HEIGHT:
                global_score += 10
                fireballs.remove(fireball)

        fireballs = [fireball for fireball in fireballs if fireball[1] < SCREEN_HEIGHT]

        # Collision detection
        player_rect = pygame.Rect(player_pos[0], player_pos[1], 20, 20)
        for fireball in fireballs:
            fireball_rect = pygame.Rect(fireball[0], fireball[1], 30, 30)
            if player_rect.colliderect(fireball_rect):
                player_health -= 1
                fireballs.remove(fireball)

                if player_health <= 0:
                    GAME_STATE = "GAME_OVER"
                    return

                    # Draw dragon
        dragon_rect = dragon_frames[current_frame].get_rect(center=dragon_pos)
        screen.blit(dragon_frames[current_frame], dragon_rect)

        # Drawing player based on current action
        if is_running:
            player_image = running_frames[player_current_frame]
        elif is_jumping:

            player_image = running_frames[player_current_frame % num_running_frames]
        else:
            player_image = idle_frames[player_current_frame % num_idle_frames]

        if last_direction == 'left':
            player_image = pygame.transform.flip(player_image, True, False)

        player_rect = player_image.get_rect(bottomleft=player_pos)
        screen.blit(player_image, player_rect)

        # Display health
        health_text = font.render(f'Health: {player_health}', True, GREEN)
        screen.blit(health_text, (10, 10))

        # Display score
        score_text = f'Score: {global_score}'
        draw_text(score_text, font, WHITE, screen, 10, 40)

        # Draw fireballs
        for fireball in fireballs:
            screen.blit(fireball_image, (fireball[0], fireball[1]))

        # Update the display
        pygame.display.flip()


        clock.tick(30)
    if GAME_STATE == "GAME_OVER":
        game_over()


def game_over():
    global GAME_STATE
    GameOver_image = pygame.image.load('GameOver.jpg')
    GameOver_image = pygame.transform.scale(GameOver_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
    screen.blit(GameOver_image, (0, 0))

    while True:
        draw_text('Game Over', font, WHITE, screen, SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 4)

        mx, my = pygame.mouse.get_pos()

        button_retry = pygame.Rect(SCREEN_WIDTH // 2 - 50, SCREEN_HEIGHT // 2, 100, 50)
        button_store = pygame.Rect(SCREEN_WIDTH // 2 - 50, SCREEN_HEIGHT // 2 + 60, 100, 50)
        button_exit = pygame.Rect(SCREEN_WIDTH // 2 - 50, SCREEN_HEIGHT // 2 + 120, 100, 50)

        pygame.draw.rect(screen, WHITE, button_retry)
        pygame.draw.rect(screen, WHITE, button_store)
        pygame.draw.rect(screen, WHITE, button_exit)

        draw_text('Retry', font, BLACK, screen, SCREEN_WIDTH // 2 - 30, SCREEN_HEIGHT // 2 + 10)
        draw_text('Store', font, BLACK, screen, SCREEN_WIDTH // 2 - 30, SCREEN_HEIGHT // 2 + 70)
        draw_text('Exit', font, BLACK, screen, SCREEN_WIDTH // 2 - 30, SCREEN_HEIGHT // 2 + 130)

        score_text = f'Score: {global_score}'
        draw_text(score_text, font, WHITE, screen, 10, 10)

        click = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                click = True

        if button_retry.collidepoint((mx, my)) and click:
            GAME_STATE = "PLAYING"
            return
        if button_store.collidepoint((mx, my)) and click:
            GAME_STATE = "STORE"
            return
        if button_exit.collidepoint((mx, my)) and click:
            pygame.quit()
            sys.exit()

        pygame.display.update()


def store_screen():
    global GAME_STATE
    global global_score
    global player_health_boost
    global player_jump_boost
    global player_speed_boost
    running = True
    store_image = pygame.image.load('store.jpg')
    store_image = pygame.transform.scale(store_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
    screen.blit(store_image, (0, 0))

    # Load and scale item images
    item_size = SCREEN_WIDTH // 4
    grid_x = SCREEN_WIDTH // 4
    grid_y = SCREEN_HEIGHT // 4
    grid_width = SCREEN_WIDTH // 2
    grid_height = SCREEN_HEIGHT // 2

    score_text = f'Score: {global_score}'
    draw_text(score_text, font, WHITE, screen, 10, 10)

    score_text = f'Info: '
    draw_text(score_text, font, WHITE, screen, 10, 100)

    armor_image = pygame.image.load('armor.jpg').convert_alpha()
    armor_image = pygame.transform.scale(armor_image, (item_size, item_size))
    armor_rect = pygame.Rect(grid_x, grid_y, item_size, item_size)

    potion_image = pygame.image.load('potion.jpg').convert_alpha()
    potion_image = pygame.transform.scale(potion_image, (item_size, item_size))
    potion_rect = pygame.Rect(grid_x + item_size, grid_y, item_size, item_size)

    boots_image = pygame.image.load('boots.jpg').convert_alpha()
    boots_image = pygame.transform.scale(boots_image, (item_size, item_size))
    boots_rect = pygame.Rect(grid_x, grid_y + item_size, item_size, item_size)

    dragon_head_image = pygame.image.load('head.png').convert_alpha()
    dragon_head_image = pygame.transform.scale(dragon_head_image, (item_size, item_size))
    dragon_head_rect = pygame.Rect(grid_x + item_size, grid_y + item_size, item_size, item_size)

    pygame.draw.rect(screen, WHITE, (grid_x, grid_y, grid_width, grid_height), 2)
    pygame.draw.line(screen, WHITE, (grid_x + item_size, grid_y), (grid_x + item_size, grid_y + grid_height), 2)
    pygame.draw.line(screen, WHITE, (grid_x, grid_y + item_size), (grid_x + grid_width, grid_y + item_size), 2)

    button_return = pygame.Rect(grid_x + grid_width + 50, grid_y + grid_height + 50, 100, 50)
    pygame.draw.rect(screen, WHITE, button_return)
    draw_text('Return', font, BLACK, screen, grid_x + grid_width + 50, grid_y + grid_height + 60)

    item_prices = {"armor": 100, "potion": 100, "boots": 100, "dragon_head": 1000}
    purchase_result = ""

    # Item descriptions
    descriptions = {
        "armor": "2x Health",
        "potion": "2x Speed",
        "boots": "2x Jump Height",
        "dragon_head": "VICTORY"
    }
    selected_item = ""
    purchase_result = ""

    draw_text('Store', font, WHITE, screen, grid_x + grid_width // 2 - 40, grid_y - 30)

    running = True
    while running:
        mx, my = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                click = True
                purchase_result = ""
                if armor_rect.collidepoint((mx, my)):
                    selected_item = "armor"
                elif potion_rect.collidepoint((mx, my)):
                    selected_item = "potion"
                elif boots_rect.collidepoint((mx, my)):
                    selected_item = "boots"
                elif dragon_head_rect.collidepoint((mx, my)):
                    selected_item = "dragon_head"
                elif button_return.collidepoint((mx, my)):
                    GAME_STATE = "GAME_OVER"
                    return

                # Purchase logic
                if selected_item and click:
                    if global_score >= item_prices[selected_item]:
                        global_score -= item_prices[selected_item]
                        purchase_result = f"Purchased {selected_item}!"
                        if selected_item == "armor":
                            player_health_boost = player_health_boost * 2
                        if selected_item == "boots":
                            player_jump_boost = player_jump_boost * 2
                        if selected_item == "potion":
                            player_speed_boost = player_speed_boost * 2
                        if selected_item == "dragon_head":
                            GAME_STATE = "VICTORY"
                            return

                    else:
                        purchase_result = "Not enough score."

        # Draw item images
        screen.blit(armor_image, armor_rect)
        screen.blit(potion_image, potion_rect)
        screen.blit(boots_image, boots_rect)
        screen.blit(dragon_head_image, dragon_head_rect)

        if selected_item:
            draw_text(descriptions[selected_item], font, WHITE, screen, 80, 100)  # Show item info
        draw_text(purchase_result, font, WHITE, screen, 10, 120)  # Show purchase result

        click = False

        pygame.display.update()

        # Handle exiting the store
        keys = pygame.key.get_pressed()
        if keys[pygame.K_ESCAPE]:
            GAME_STATE = "GAME_OVER"
            return


def victory_screen():
    global GAME_STATE
    running = True
    victory_image = pygame.image.load('victory.jpg')
    victory_image = pygame.transform.scale(victory_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
    screen.blit(victory_image, (0, 0))

    while running:
        draw_text('You Win!', font, WHITE, screen, SCREEN_WIDTH // 2 - 50, SCREEN_HEIGHT // 4)

        button_exit = pygame.Rect(SCREEN_WIDTH // 2 - 50, SCREEN_HEIGHT // 2, 100, 50)
        pygame.draw.rect(screen, WHITE, button_exit)
        draw_text('Exit', font, BLACK, screen, SCREEN_WIDTH // 2 - 30, SCREEN_HEIGHT // 2 + 10)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if button_exit.collidepoint(pygame.mouse.get_pos()):
                    pygame.quit()
                    sys.exit()

        pygame.display.update()

        keys = pygame.key.get_pressed()
        if keys[pygame.K_ESCAPE]:
            pygame.quit()
            sys.exit()



if __name__ == "__main__":
    while True:
        if GAME_STATE == "MAIN_MENU":
            main_menu()
        elif GAME_STATE == "PLAYING":
            game()
        elif GAME_STATE == "GAME_OVER":
            game_over()
        elif GAME_STATE == "STORE":
            store_screen()
        elif GAME_STATE == "VICTORY":
            victory_screen()
        else:
            break
pygame.quit()
sys.exit()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
