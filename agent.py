# agent.py
import pygame
import heapq

class Agent(pygame.sprite.Sprite):
    def __init__(self, environment, grid_size):
        super().__init__()
        self.image = pygame.Surface((grid_size, grid_size))
        self.image.fill((0, 0, 255))  
        self.rect = self.image.get_rect()
        self.grid_size = grid_size
        self.environment = environment
        self.position = [0, 0]  # Starting at the top-left corner of the grid
        self.rect.topleft = (0, 0)
        self.task_completed = 0
        self.completed_tasks = []
        self.path = []  # List of positions to follow
        self.moving = False  # Flag to indicate if the agent is moving
        self.path_cost = 0
        self.last_cost = 0
        self.algorithm = "UCS"  # Default to UCS; toggle this to switch to A*

    def move(self):
        """Move the agent along the path."""
        if self.path:
            next_position = self.path.pop(0)
            self.position = list(next_position)
            self.rect.topleft = (self.position[0] * self.grid_size, self.position[1] * self.grid_size)
            self.path_cost += 1
            self.check_task_completion()
        else:
            self.moving = False  # Stop moving when path is exhausted

    def check_task_completion(self):
        """Check if the agent has reached a task location."""
        position_tuple = tuple(self.position)
        if position_tuple in self.environment.task_locations:
            task_number = self.environment.task_locations.pop(position_tuple)
            self.task_completed += 1
            self.completed_tasks.append((task_number, "Cost = " + str(self.path_cost - self.last_cost)))
            self.last_cost = self.path_cost

    def find_nearest_task(self):
        """Find the nearest task using the selected algorithm."""
        self.task_costs = {}  # Reset task costs
        nearest_task = None
        shortest_path = None
        shortest_cost = float('inf')

        for task_position in self.environment.task_locations.keys():
            path, cost = self.find_path_to(task_position)
            if path:
                self.task_costs[task_position] = cost
                if cost < shortest_cost:
                    shortest_path = path
                    nearest_task = task_position
                    shortest_cost = cost
        if shortest_path:
            self.path = shortest_path[1:]  # Exclude the current position
            self.moving = True

    def find_path_to(self, target):
        """Find a path to the target position using the selected algorithm."""
        start = tuple(self.position)
        goal = target

        if self.algorithm == "UCS":
            return self.ucs(start, goal)
        else:
            return self.astar(start, goal)

    def ucs(self, start, goal):
        """Find a path to the target position using UCS."""
        queue = [(0, start, [start])]
        visited = set()

        while queue:
            (cost, vertex, path) = heapq.heappop(queue)
            if vertex not in visited:
                if vertex in self.environment.barrier_locations:
                    continue
                visited.add(vertex)
                if vertex == goal:
                    return path, cost
                neighbors = self.get_neighbors(vertex[0], vertex[1])
                for neighbor in neighbors:
                    heapq.heappush(queue, (cost + 1, neighbor, path + [neighbor]))
        return None, float('inf')  # No path found

    def astar(self, start, goal):
        """Find a path to the target position using A*."""
        open_set = []
        heapq.heappush(open_set, (0, start, [start]))
        g_scores = {start: 0}

        while open_set:
            (_, current, path) = heapq.heappop(open_set)
            if current == goal:
                return path, g_scores[current]

            neighbors = self.get_neighbors(current[0], current[1])
            for neighbor in neighbors:
                tentative_g_score = g_scores[current] + 1
                if neighbor not in g_scores or tentative_g_score < g_scores[neighbor]:
                    g_scores[neighbor] = tentative_g_score
                    f_score = tentative_g_score + self.heuristic(neighbor, goal)
                    heapq.heappush(open_set, (f_score, neighbor, path + [neighbor]))
        return None, float('inf')  # No path found

    def heuristic(self, a, b):
        """Heuristic function for A* (Manhattan distance)."""
        (x1, y1) = a
        (x2, y2) = b
        return abs(x1 - x2) + abs(y1 - y2)

    def get_neighbors(self, x, y):
        """Get walkable neighboring positions."""
        neighbors = []
        directions = [("up", (0, -1)), ("down", (0, 1)), ("left", (-1, 0)), ("right", (1, 0))]
        for _, (dx, dy) in directions:
            nx, ny = x + dx, y + dy
            if self.environment.is_within_bounds(nx, ny) and not self.environment.is_barrier(nx, ny):
                neighbors.append((nx, ny))
        return neighbors
