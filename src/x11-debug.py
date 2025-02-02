import pygame

# Initialize Pygame
pygame.init()

# Set up the display (800x600 window)
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Simple Circle Test")

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

# Main loop
running = True
while running:
    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Fill screen with black
    screen.fill(BLACK)
    
    # Draw white circle in center (radius 50)
    pygame.draw.circle(screen, WHITE, (400, 300), 50)
    
    # Update display
    pygame.display.flip()

# Cleanup
pygame.quit()
