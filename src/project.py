import pygame
import numpy as np
import random
import colorsys
import sys

# --- Configuration ---
GRID_WIDTH, GRID_HEIGHT = 200, 200
CELL_SIZE = 4
FPS = 10

# --- Chaos Modifiers ---
SUCCESS_RATE = 0.80
MUTATION_RATE = 0.01

RULESETS = [
    {"name": "Fast Spirals", "states": 14, "threshold": 1, "neighborhood": "moore"},
    {"name": "Slow Crystals", "states": 6, "threshold": 1, "neighborhood": "von_neumann"},
    {"name": "Resilient Microbes", "states": 5, "threshold": 2, "neighborhood": "moore"}
]


def generate_monochromatic_palette(num_states):
    
    base_hue = random.random() 
    palette = []
    
    for i in range(num_states):
        value = 0.2 + 0.8 * (i / max(1, num_states - 1))
        r, g, b = colorsys.hsv_to_rgb(base_hue, 0.9, value)
        palette.append([int(r * 255), int(g * 255), int(b * 255)])
    return np.array(palette)

def sprout_cells(grid, cx, cy, radius, num_states):
    for x in range(-radius, radius + 1):
        for y in range(-radius, radius + 1):
            if x*x + y*y <= radius*radius: 
                grid_x = (cx + x) % GRID_WIDTH
                grid_y = (cy + y) % GRID_HEIGHT
                grid[grid_x, grid_y] = random.randint(0, num_states - 1)

def count_neighbors(grid, target_state, neighborhood):
    
    target_grid = (grid == target_state).astype(int)
    if neighborhood == 'moore': 
        return (np.roll(target_grid, 1, 0) + np.roll(target_grid, -1, 0) +
                np.roll(target_grid, 1, 1) + np.roll(target_grid, -1, 1) +
                np.roll(np.roll(target_grid, 1, 0), 1, 1) +
                np.roll(np.roll(target_grid, -1, 0), 1, 1) +
                np.roll(np.roll(target_grid, 1, 0), -1, 1) +
                np.roll(np.roll(target_grid, -1, 0), -1, 1))
    else: 
        return (np.roll(target_grid, 1, 0) + np.roll(target_grid, -1, 0) +
                np.roll(target_grid, 1, 1) + np.roll(target_grid, -1, 1))
    

class Ecosystem:
    
    def __init__(self):
        self.current_rule_index = 0
        self.reset_simulation()

    def reset_simulation(self):
        self.rule = RULESETS[self.current_rule_index]
        self.grid = np.random.randint(0, self.rule["states"], size=(GRID_WIDTH, GRID_HEIGHT))
        self.update_palette()

    def update_palette(self):
        if "generate_monochromatic_palette" in globals():
            self.palette = generate_monochromatic_palette(self.rule["states"])

    def cycle_rules(self):
        self.current_rule_index = (self.current_rule_index + 1) % len(RULESETS)
        self.reset_simulation()

    def handle_click(self, pos):
        """Safely calls sprout_cells if it exists."""
        if "sprout_cells" in globals():
            mx, my = pos[0] // CELL_SIZE, pos[1] // CELL_SIZE
            sprout_cells(self.grid, mx, my, 15, self.rule["states"])
        self.update_palette()

    def update(self):
        """Simulation logic with a safety check for the neighbor counter."""
        if "count_neighbors" not in globals():
            return # Cannot simulate without neighbor logic

        next_grid = self.grid.copy()
        num_states = self.rule["states"]
        chance_mask = np.random.random(self.grid.shape) < SUCCESS_RATE
        
        for state in range(num_states):
            next_state = (state + 1) % num_states
            attacking_neighbors = count_neighbors(self.grid, next_state, self.rule["neighborhood"])
            consumed_mask = (self.grid == state) & (attacking_neighbors >= self.rule["threshold"]) & chance_mask
            next_grid[consumed_mask] = next_state

        mutation_mask = np.random.random(self.grid.shape) < MUTATION_RATE
        if np.any(mutation_mask):
            next_grid[mutation_mask] = np.random.randint(0, num_states, size=np.count_nonzero(mutation_mask))
        
        self.grid = next_grid

def draw_text(screen, text, size, x, y):
    font = pygame.font.SysFont("arial", size, bold=True)
    text_surface = font.render(text, True, (255, 255, 255))
    screen.blit(text_surface, text_surface.get_rect(center=(x, y)))

def main():
    pygame.init()
    screen_res = (GRID_WIDTH * CELL_SIZE, GRID_HEIGHT * CELL_SIZE)
    screen = pygame.display.set_mode(screen_res)
    clock = pygame.time.Clock()
    
    sim = Ecosystem()
    waiting_to_start = True
    running = True
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                if event.key == pygame.K_RETURN:
                    waiting_to_start = False
                if not waiting_to_start and event.key == pygame.K_SPACE:
                    sim.cycle_rules()
            
            
            if event.type == pygame.MOUSEBUTTONDOWN and not waiting_to_start:
                sim.handle_click(pygame.mouse.get_pos())
            
        
        if waiting_to_start:
            screen.fill((30, 30, 35))
            draw_text(screen, "ECOSYSTEM ART SANDBOX", 40, screen_res[0]//2, screen_res[1]//2 - 60)
            draw_text(screen, "Press [ENTER] to Start", 25, screen_res[0]//2, screen_res[1]//2 + 80)
            draw_text(screen, "Press [SPACE] to Cycle Rules", 25, screen_res[0]//2, screen_res[1]//2)
            draw_text(screen, "Press [MOUSE] to Add Cells", 25, screen_res[0]//2, screen_res[1]//2 + 40)
            draw_text(screen, "Press [ESCAPE] to Quit", 25, screen_res[0]//2, screen_res[1]//2 + 120)
        
        else: #Change to else: when if is added above
            sim.update()
            rgb_grid = sim.palette[sim.grid]
            surface = pygame.surfarray.make_surface(rgb_grid)
            screen.blit(pygame.transform.scale(surface, screen_res), (0, 0))
    
        
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()