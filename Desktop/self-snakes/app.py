import pygame
import random

# Initialize pygame
pygame.init()

# Screen settings
width, height = 400, 400
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption('Self-Playing Snake Game')

# Colors
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLACK = (0, 0, 0)

# Snake settings
snake_pos = [100, 50]
snake_body = [[100, 50], [90, 50], [80, 50]]
snake_direction = 'RIGHT'
change_to = snake_direction
speed = 15

# Food settings
food_pos = [random.randrange(1, (width//10)) * 10, random.randrange(1, (height//10)) * 10]
food_spawn = True

# Score
score = 0

clock = pygame.time.Clock()

def move_snake(snake_pos, snake_body, food_pos):
    if food_pos[0] < snake_pos[0]:
        return 'LEFT'
    elif food_pos[0] > snake_pos[0]:
        return 'RIGHT'
    elif food_pos[1] < snake_pos[1]:
        return 'UP'
    elif food_pos[1] > snake_pos[1]:
        return 'DOWN'

# Main loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    snake_direction = move_snake(snake_pos, snake_body, food_pos)

    if snake_direction == 'UP':
        snake_pos[1] -= 10
    if snake_direction == 'DOWN':
        snake_pos[1] += 10
    if snake_direction == 'LEFT':
        snake_pos[0] -= 10
    if snake_direction == 'RIGHT':
        snake_pos[0] += 10

    snake_body.insert(0, list(snake_pos))
    if snake_pos == food_pos:
        score += 10
        food_spawn = False
    else:
        snake_body.pop()
        
    if not food_spawn:
        food_pos = [random.randrange(1, (width//10)) * 10, random.randrange(1, (height//10)) * 10]
        food_spawn = True

    screen.fill(BLACK)

    for pos in snake_body:
        pygame.draw.rect(screen, GREEN, pygame.Rect(pos[0], pos[1], 10, 10))

    pygame.draw.rect(screen, RED, pygame.Rect(food_pos[0], food_pos[1], 10, 10))

    # Game over conditions
    if snake_pos[0] < 0 or snake_pos[0] > width-10:
        running = False
    if snake_pos[1] < 0 or snake_pos[1] > height-10:
        running = False

    # Self collision
    for block in snake_body[1:]:
        if snake_pos == block:
            running = False

    pygame.display.set_caption(f'Score: {score}')
    pygame.display.flip()
    clock.tick(speed)

pygame.quit()