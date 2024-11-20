import pygame
import sys
from agent import Agent
from environment import Environment
import copy

# Constants
WINDOW_WIDTH, WINDOW_HEIGHT = 800, 600
GRID_SIZE = 40
STATUS_WIDTH = 300
BACKGROUND_COLOR = (255, 255, 255)
BARRIER_COLOR = (0, 0, 0)       # Barrier color is black
TASK_COLOR = (255, 0, 0)        # Task color is red
TEXT_COLOR = (0, 0, 0)
BUTTON_COLOR = (248, 67, 129)
BUTTON_HOVER_COLOR = (255, 168, 0)
BUTTON_TEXT_COLOR = (255, 255, 255)
VISITED_TASK_COLOR = (45, 207, 89)
MOVEMENT_DELAY = 150  # Milliseconds between movements
button_spacing = 20

def reset_task_colors(environment):
    """Reset all task colors to red when starting Agent"""
    return {location: TASK_COLOR for location in environment.task_locations}

def main():
    pygame.init()

    # Set up display with an additional status panel
    screen = pygame.display.set_mode((WINDOW_WIDTH + STATUS_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("Pygame AI Grid Simulation")

    # Clock to control frame rate
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 22)

    # Initialize environment and agent
    environment = Environment(WINDOW_WIDTH, WINDOW_HEIGHT, GRID_SIZE, num_tasks=5, num_barriers=15)
    ucs_environment = copy.deepcopy(environment)
    astar_environment = copy.deepcopy(environment)
    ucs_agent = Agent(ucs_environment, GRID_SIZE)
    astar_agent = Agent(astar_environment, GRID_SIZE)
    all_sprites = pygame.sprite.Group()
    all_sprites.add(ucs_agent, astar_agent)
    agent = None
    task_colors = reset_task_colors(environment)  # Initialize task colors

    # Buttons for UCS and A* positioned on the right side (status panel)
    button_width, button_height = 90, 30
    ucs_button_x = WINDOW_WIDTH + 200
    # ucs_button_y = WINDOW_HEIGHT  - button_height - 20
    ucs_button_y = WINDOW_HEIGHT -  3 * button_height 
    ucs_button_rect = pygame.Rect(ucs_button_x, ucs_button_y, button_width, button_height)


    astar_button_x = WINDOW_WIDTH + 200
    # astar_button_y = WINDOW_HEIGHT  - button_height - 20
    astar_button_y = WINDOW_HEIGHT - button_height -10
    astar_button_rect = pygame.Rect(astar_button_x, astar_button_y, button_width, button_height)

    # Variables for movement delay
    last_move_time = pygame.time.get_ticks()
    active_algorithm = None  # None, UCS, or A*

    # Main loop
    running = True
    while running:
        clock.tick(60)  # Limit to 60 FPS

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                if ucs_button_rect.collidepoint(event.pos):
                    # Only reset the agent if it's not already set to UCS
                    if active_algorithm != "UCS":
                        active_algorithm = "UCS"
                        agent = ucs_agent
                        ucs_agent.algorithm = "UCS"
                        task_colors = reset_task_colors(ucs_environment)
                        if ucs_environment.task_locations:
                            ucs_agent.find_nearest_task()

                elif astar_button_rect.collidepoint(event.pos):
                    # Only reset the agent if it's not already set to A*
                    if active_algorithm != "A*":
                        active_algorithm = "A*"
                        agent = astar_agent
                        astar_agent.algorithm = "A*"
                        task_colors = reset_task_colors(astar_environment)
                        if astar_environment.task_locations:
                            astar_agent.find_nearest_task()

        # Clear the screen
        screen.fill(BACKGROUND_COLOR)

        # Draw grid and barriers
        for x in range(environment.columns):
            for y in range(environment.rows):
                rect = pygame.Rect(x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE, GRID_SIZE)
                pygame.draw.rect(screen, (200, 200, 200), rect, 1)  # Draw grid lines

        # Draw barriers
        for (bx, by) in environment.barrier_locations:
            barrier_rect = pygame.Rect(bx * GRID_SIZE, by * GRID_SIZE, GRID_SIZE, GRID_SIZE)
            pygame.draw.rect(screen, BARRIER_COLOR, barrier_rect)

        # Draw tasks with numbers and their current color
        for (tx, ty), task_number in environment.task_locations.items():
            task_rect = pygame.Rect(tx * GRID_SIZE, ty * GRID_SIZE, GRID_SIZE, GRID_SIZE)
            pygame.draw.rect(screen, task_colors[(tx, ty)], task_rect)  # Draw task with its color
            # Draw task number
            task_num_surface = font.render(str(task_number), True, (255, 255, 255))
            task_num_rect = task_num_surface.get_rect(center=task_rect.center)
            screen.blit(task_num_surface, task_num_rect)

        # Draw agents
        all_sprites.draw(screen)

        # Display status panel
        status_x = WINDOW_WIDTH + 10
        status_y = 10

        # Display UCS Agent status
        algo_text1 = f"Algorithm: UCS"
        task_status_text1 = f"Tasks Completed : {ucs_agent.task_completed}"
        position_text1 = f"Position: {ucs_agent.position}"
        completed_tasks_text1 = f"Completed Tasks:"
        
        algo_surface1 = font.render(algo_text1, True, TEXT_COLOR)
        status_surface1 = font.render(task_status_text1, True, TEXT_COLOR)
        position_surface1 = font.render(position_text1, True, TEXT_COLOR)
        completed_tasks_surface1 = font.render(completed_tasks_text1, True, TEXT_COLOR)

        screen.blit(algo_surface1, (status_x, status_y))
        status_y += 25
        screen.blit(status_surface1, (status_x, status_y))
        status_y += 25
        screen.blit(completed_tasks_surface1, (status_x, status_y))
        status_y += 25
        screen.blit(position_surface1, (status_x, status_y))
        status_y += 25
    
        for i in ucs_agent.completed_tasks:
            task_info_text = f"{i[0]}, {i[1]}"
            task_info_surface = font.render(task_info_text, True, TEXT_COLOR)
            screen.blit(task_info_surface, (status_x + 20, status_y))
            status_y += 25

        path_cost_text1 = f"Total Path Cost: {ucs_agent.path_cost}"
        path_cost_surface1 = font.render(path_cost_text1, True, TEXT_COLOR)
        screen.blit(path_cost_surface1, (status_x, status_y))
        status_y += 25

        # Display A* Agent status
        status_y += 15
        algo_text2 = f"Algorithm: A*"
        task_status_text2 = f"Tasks Completed : {astar_agent.task_completed}"
        position_text2 = f"Position: {astar_agent.position}"
        completed_tasks_text2 = f"Completed Tasks:"
        
        algo_surface2 = font.render(algo_text2, True, TEXT_COLOR)
        status_surface2 = font.render(task_status_text2, True, TEXT_COLOR)
        position_surface2 = font.render(position_text2, True, TEXT_COLOR)
        completed_tasks_surface2 = font.render(completed_tasks_text2, True, TEXT_COLOR)

        screen.blit(algo_surface2, (status_x, status_y))
        status_y += 25
        screen.blit(status_surface2, (status_x, status_y))
        status_y += 25
        screen.blit(completed_tasks_surface2, (status_x, status_y))
        status_y += 25
        screen.blit(position_surface2, (status_x, status_y))
        status_y += 25

        for i in astar_agent.completed_tasks:
            task_info_text = f"{i[0]}, {i[1]}"
            task_info_surface = font.render(task_info_text, True, TEXT_COLOR)
            screen.blit(task_info_surface, (status_x + 20, status_y))
            status_y += 25

        path_cost_text2 = f"Total Path Cost: {astar_agent.path_cost}"
        path_cost_surface2 = font.render(path_cost_text2, True, TEXT_COLOR)
        screen.blit(path_cost_surface2, (status_x, status_y))

        # Draw the UCS button
        mouse_pos = pygame.mouse.get_pos()
        if ucs_button_rect.collidepoint(mouse_pos):
            ucs_button_color = BUTTON_HOVER_COLOR
        else:
            ucs_button_color = BUTTON_COLOR
        pygame.draw.rect(screen, ucs_button_color, ucs_button_rect)
        ucs_button_text = font.render("Run UCS", True, BUTTON_TEXT_COLOR)
        ucs_text_rect = ucs_button_text.get_rect(center=ucs_button_rect.center)
        screen.blit(ucs_button_text, ucs_text_rect)

        # Draw the A* button
        if astar_button_rect.collidepoint(mouse_pos):
            astar_button_color = BUTTON_HOVER_COLOR
        else:
            astar_button_color = BUTTON_COLOR
        pygame.draw.rect(screen, astar_button_color, astar_button_rect)
        astar_button_text = font.render("Run A*", True, BUTTON_TEXT_COLOR)
        astar_text_rect = astar_button_text.get_rect(center=astar_button_rect.center)
        screen.blit(astar_button_text, astar_text_rect)

        # Draw the status panel separator
        pygame.draw.line(screen, (0, 0, 0), (WINDOW_WIDTH, 0), (WINDOW_WIDTH, WINDOW_HEIGHT))

        # Automatic movement with delay
        if active_algorithm and agent:
            current_time = pygame.time.get_ticks()
            if current_time - last_move_time > MOVEMENT_DELAY:
                if not agent.moving and environment.task_locations:
                    agent.find_nearest_task()
                elif agent.moving:
                    agent.move()
                    task_pos = tuple(agent.position)
                    if task_pos in task_colors and task_colors[task_pos] == TASK_COLOR:
                        task_colors[task_pos] = VISITED_TASK_COLOR  # Change color to green when task is completed
                last_move_time = current_time

        # Update the display
        pygame.display.flip()

    # Quit Pygame properly
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
