import random
import pygame


pygame.init()

WIDTH, HEIGHT = 960, 720
CELL_SIZE = 28
BOARD_COLUMNS, BOARD_ROWS = 24, 19
BOARD_X, BOARD_Y = 48, 150
BOARD_WIDTH = BOARD_COLUMNS * CELL_SIZE
BOARD_HEIGHT = BOARD_ROWS * CELL_SIZE

BACKGROUND = (13, 23, 24)
PANEL = (22, 36, 36)
BOARD_COLOR = (17, 30, 30)
GRID_COLOR = (27, 43, 42)
TEXT = (235, 241, 228)
MUTED = (137, 158, 148)
GREEN = (137, 220, 111)
GREEN_DARK = (75, 153, 94)
CORAL = (255, 119, 103)
GOLD = (246, 202, 105)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake | Arcade")
clock = pygame.time.Clock()
font_small = pygame.font.SysFont("segoe ui", 16)
font_medium = pygame.font.SysFont("segoe ui", 22, bold=True)
font_large = pygame.font.SysFont("segoe ui", 40, bold=True)
font_title = pygame.font.SysFont("segoe ui", 58, bold=True)


def draw_text(surface, text, font, color, position, anchor="topleft"):
	image = font.render(text, True, color)
	rect = image.get_rect(**{anchor: position})
	surface.blit(image, rect)
	return rect


def make_food(snake):
	open_cells = [
		(column, row)
		for column in range(BOARD_COLUMNS)
		for row in range(BOARD_ROWS)
		if (column, row) not in snake
	]
	return random.choice(open_cells) if open_cells else None


def reset_game():
	center = (BOARD_COLUMNS // 2, BOARD_ROWS // 2)
	snake = [center, (center[0] - 1, center[1]), (center[0] - 2, center[1])]
	return snake, (1, 0), (1, 0), make_food(snake), 0


def draw_panel(rect, color=PANEL, border=None, radius=10):
	pygame.draw.rect(screen, color, rect, border_radius=radius)
	if border:
		pygame.draw.rect(screen, border, rect, width=1, border_radius=radius)


def draw_scene(state, snake, food, score, best_score):
	screen.fill(BACKGROUND)

	draw_text(screen, "FIELD NOTES  /  ARCADE", font_small, GREEN, (48, 30))
	draw_text(screen, "SNAKE", font_large, TEXT, (48, 55))
	draw_text(screen, "A little focus goes a long way.", font_small, MUTED, (50, 105))

	score_panel = pygame.Rect(556, 42, 164, 76)
	best_panel = pygame.Rect(732, 42, 164, 76)
	draw_panel(score_panel)
	draw_panel(best_panel)
	draw_text(screen, "SCORE", font_small, MUTED, (574, 54))
	draw_text(screen, f"{score:04d}", font_medium, TEXT, (574, 76))
	draw_text(screen, "BEST", font_small, MUTED, (750, 54))
	draw_text(screen, f"{best_score:04d}", font_medium, GOLD, (750, 76))

	board_rect = pygame.Rect(BOARD_X, BOARD_Y, BOARD_WIDTH, BOARD_HEIGHT)
	draw_panel(board_rect, BOARD_COLOR, (42, 62, 58), radius=12)
	for column in range(1, BOARD_COLUMNS):
		x = BOARD_X + column * CELL_SIZE
		pygame.draw.line(screen, GRID_COLOR, (x, BOARD_Y + 1), (x, BOARD_Y + BOARD_HEIGHT - 1))
	for row in range(1, BOARD_ROWS):
		y = BOARD_Y + row * CELL_SIZE
		pygame.draw.line(screen, GRID_COLOR, (BOARD_X + 1, y), (BOARD_X + BOARD_WIDTH - 1, y))

	if food is not None:
		food_center = (
			BOARD_X + food[0] * CELL_SIZE + CELL_SIZE // 2,
			BOARD_Y + food[1] * CELL_SIZE + CELL_SIZE // 2,
		)
		pulse = 1 + (pygame.time.get_ticks() // 350) % 2
		pygame.draw.circle(screen, (111, 58, 52), food_center, 10 + pulse)
		pygame.draw.circle(screen, CORAL, food_center, 7 + pulse)

	for index, (column, row) in enumerate(snake):
		inset = 3 if index else 2
		segment = pygame.Rect(
			BOARD_X + column * CELL_SIZE + inset,
			BOARD_Y + row * CELL_SIZE + inset,
			CELL_SIZE - inset * 2,
			CELL_SIZE - inset * 2,
		)
		color = GREEN if index == 0 else GREEN_DARK
		pygame.draw.rect(screen, color, segment, border_radius=7)
		if index == 0:
			eye_y = segment.y + 8
			eye_x = segment.right - 7
			pygame.draw.circle(screen, (16, 36, 26), (eye_x, eye_y), 2)
			pygame.draw.circle(screen, (16, 36, 26), (eye_x, eye_y + 8), 2)

	sidebar_x = 760
	draw_text(screen, "CONTROLS", font_small, GREEN, (sidebar_x, 158))
	controls = [("MOVE", "Arrow keys / WASD"), ("PAUSE", "P or Space"), ("RESTART", "R"), ("QUIT", "Esc")]
	for index, (label, detail) in enumerate(controls):
		y = 190 + index * 54
		draw_text(screen, label, font_small, MUTED, (sidebar_x, y))
		draw_text(screen, detail, font_small, TEXT, (sidebar_x, y + 21))

	pygame.draw.line(screen, (44, 63, 59), (sidebar_x, 425), (896, 425), 1)
	draw_text(screen, "PACE", font_small, GREEN, (sidebar_x, 447))
	level = 1 + score // 50
	draw_text(screen, f"LEVEL {level:02d}", font_medium, TEXT, (sidebar_x, 472))
	draw_text(screen, "Every 50 points", font_small, MUTED, (sidebar_x, 505))
	draw_text(screen, "the snake gets faster.", font_small, MUTED, (sidebar_x, 527))

	pygame.draw.line(screen, (44, 63, 59), (48, 704), (896, 704), 1)
	draw_text(screen, "GROW SLOW. THINK AHEAD.", font_small, MUTED, (48, 682))
	draw_text(screen, "ESC  /  EXIT", font_small, MUTED, (896, 682), anchor="topright")

	if state in ("title", "paused", "game_over", "won"):
		overlay = pygame.Surface((BOARD_WIDTH, BOARD_HEIGHT), pygame.SRCALPHA)
		overlay.fill((8, 17, 17, 190))
		screen.blit(overlay, (BOARD_X, BOARD_Y))

		if state == "title":
			heading, subheading, prompt = "READY?", "Collect the coral fruit. Avoid the edges and yourself.", "PRESS ENTER TO PLAY"
		elif state == "paused":
			heading, subheading, prompt = "PAUSED", "Take a breath. Your run is right where you left it.", "PRESS P OR SPACE TO RESUME"
		elif state == "won":
			heading, subheading, prompt = "PERFECT RUN", "You filled the whole field. That's the lot.", "PRESS ENTER TO PLAY AGAIN"
		else:
			heading, subheading, prompt = "RUN OVER", f"Final score: {score:04d}  /  Best: {best_score:04d}", "PRESS ENTER OR R TO TRY AGAIN"

		center_x = BOARD_X + BOARD_WIDTH // 2
		center_y = BOARD_Y + BOARD_HEIGHT // 2
		draw_text(screen, heading, font_title, TEXT, (center_x, center_y - 54), anchor="midbottom")
		draw_text(screen, subheading, font_small, MUTED, (center_x, center_y - 27), anchor="midtop")
		draw_text(screen, prompt, font_small, GREEN, (center_x, center_y + 27), anchor="midtop")

	pygame.display.flip()


def main():
	snake, direction, next_direction, food, score = reset_game()
	best_score = 0
	state = "title"
	elapsed = 0
	running = True

	direction_keys = {
		pygame.K_UP: (0, -1), pygame.K_w: (0, -1),
		pygame.K_DOWN: (0, 1), pygame.K_s: (0, 1),
		pygame.K_LEFT: (-1, 0), pygame.K_a: (-1, 0),
		pygame.K_RIGHT: (1, 0), pygame.K_d: (1, 0),
	}

	while running:
		frame_time = min(clock.tick(60), 100)
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				running = False
			elif event.type == pygame.KEYDOWN:
				if event.key == pygame.K_ESCAPE:
					running = False
				elif state == "playing":
					if event.key in (pygame.K_p, pygame.K_SPACE):
						state = "paused"
					elif event.key == pygame.K_r:
						snake, direction, next_direction, food, score = reset_game()
						elapsed = 0
					elif event.key in direction_keys:
						requested = direction_keys[event.key]
						if requested != (-direction[0], -direction[1]):
							next_direction = requested
				elif state == "paused":
					if event.key in (pygame.K_p, pygame.K_SPACE, pygame.K_RETURN):
						state = "playing"
						elapsed = 0
					elif event.key == pygame.K_r:
						snake, direction, next_direction, food, score = reset_game()
						state = "playing"
						elapsed = 0
				elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE, pygame.K_r):
					snake, direction, next_direction, food, score = reset_game()
					state = "playing"
					elapsed = 0

		if state == "playing":
			elapsed += frame_time
			step_time = max(65, 145 - (score // 50) * 10)
			while elapsed >= step_time and state == "playing":
				elapsed -= step_time
				direction = next_direction
				head = (snake[0][0] + direction[0], snake[0][1] + direction[1])
				growing = head == food
				body_to_check = snake if growing else snake[:-1]
				outside = not (0 <= head[0] < BOARD_COLUMNS and 0 <= head[1] < BOARD_ROWS)

				if outside or head in body_to_check:
					state = "game_over"
					break

				snake.insert(0, head)
				if growing:
					score += 10
					best_score = max(best_score, score)
					food = make_food(snake)
					if food is None:
						state = "won"
				else:
					snake.pop()

		draw_scene(state, snake, food, score, best_score)

	pygame.quit()


if __name__ == "__main__":
	main()


