import pygame
import random
import json

from pathlib import Path
from collections import deque

pygame.init()

COLS = 10
ROWS = 20
CELL = 30

WIDTH = COLS * CELL
PANEL_HEIGHT = 50
HEIGHT = ROWS * CELL + PANEL_HEIGHT

FPS = 60
DROP_INTERVAL = 0.5
FAST_DROP_INTERVAL = 0.05
LOCK_DELAY = 0.2

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (100, 100, 100)
GOLD = (255, 215, 0)

MENU_BG = (222, 248, 116)
BUTTON_GREEN = (100, 150, 50)

FONT = pygame.font.Font(None, 32)
MENU_FONT = pygame.font.Font(None, 48)
SMALL_FONT = pygame.font.Font(None, 24)

SAVE_FILE = (
    Path.home()
    / ".nestims"
    / "tetris"
    / "records.json"
)



SHAPES = [
    [[1, 1, 1, 1]],

    [[1, 0, 0],
     [1, 1, 1]],

    [[0, 0, 1],
     [1, 1, 1]],

    [[1, 1],
     [1, 1]],

    [[1, 1, 0],
     [0, 1, 1]],

    [[0, 1, 0],
     [1, 1, 1]],

    [[0, 1, 1],
     [1, 1, 0]]
]

COLORS = [
    (255, 0, 0),
    (255, 255, 0),
    (255, 128, 0),
    (0, 255, 0),
    (0, 255, 255),
    (255, 0, 255),
    (0, 0, 255)
]

def load_record():

    try:
        data = json.loads(
            SAVE_FILE.read_text(encoding="utf-8")
        )

        return max(
            0, int(data.get("best_score", 0))
        )

    except (OSError, ValueError, TypeError, AttributeError):
        return 0


def save_record(score):

    try:
        SAVE_FILE.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        temp = SAVE_FILE.with_suffix(".tmp")

        temp.write_text(
            json.dumps(
                {"best_score": score},
                indent=4
            ),
            encoding="utf-8"
        )

        temp.replace(SAVE_FILE)

        return True

    except OSError:
        return False




class PieceGenerator:

    def __init__(self):
        self.bag = deque()

    def next_piece(self):

        if not self.bag:

            indices = list(range(len(SHAPES)))
            random.shuffle(indices)

            self.bag.extend(indices)

        return Piece(self.bag.popleft())


class Piece:

    def __init__(self, shape_id):

        self.shape_id = shape_id

        self.shape = [
            row[:] for row in SHAPES[shape_id]
        ]

        self.color = COLORS[shape_id]

        self.x = COLS // 2 - len(self.shape[0]) // 2
        self.y = 0

    def cells(self, dx=0, dy=0, shape=None):

        if shape is None:
            shape = self.shape

        return [
            (
                self.x + x + dx,
                self.y + y + dy
            )
            for y, row in enumerate(shape)
            for x, value in enumerate(row)
            if value
        ]

    def rotated_shape(self):

        return [
            list(row)
            for row in zip(*self.shape[::-1])
        ]



class Board:

    def __init__(self):

        self.grid = [
            [None] * COLS
            for _ in range(ROWS)
        ]

    def valid(self, piece, dx=0, dy=0, shape=None):

        for x, y in piece.cells(dx, dy, shape):

            if not 0 <= x < COLS:
                return False

            if y >= ROWS:
                return False

            if y >= 0 and self.grid[y][x] is not None:
                return False

        return True

    def lock(self, piece):

        cells = piece.cells()

        if any(y < 0 for x, y in cells):
            return False

        if not self.valid(piece):
            return False

        for x, y in cells:
            self.grid[y][x] = piece.color

        return True

    def clear_lines(self):

        remaining = [
            row for row in self.grid
            if not all(
                cell is not None
                for cell in row
            )
        ]

        cleared = ROWS - len(remaining)

        self.grid = (
            [[None] * COLS for _ in range(cleared)]
            + remaining
        )

        return cleared

class Game:

    def __init__(self):

        self.screen = pygame.display.set_mode(
            (WIDTH, HEIGHT)
        )

        pygame.display.set_caption(
            "Tetris | NESTIMS"
        )

        self.clock = pygame.time.Clock()

        self.running = True
        self.state = "MENU"

        self.best_score = load_record()
        self.score = 0
        self.lines = 0

        self.new_record = False
        self.save_error = False

        self.play_button = pygame.Rect(
            WIDTH // 2 - 50,
            HEIGHT // 2 - 40,
            100, 40
        )

        self.help_button = pygame.Rect(
            WIDTH // 2 - 50,
            HEIGHT // 2 + 10,
            100, 40
        )

        self.back_button = pygame.Rect(
            WIDTH // 2 - 50,
            HEIGHT // 2 + 60,
            100, 40
        )

        self.restart_button = pygame.Rect(
            WIDTH // 2 - 70,
            400, 140, 40
        )

        self.menu_button = pygame.Rect(
            WIDTH // 2 - 70,
            455, 140, 40
        )

        self.overlay = pygame.Surface(
            (WIDTH, HEIGHT),
            pygame.SRCALPHA
        )

        self.overlay.fill((0, 0, 0, 190))



    def start_game(self):

        self.board = Board()
        self.generator = PieceGenerator()

        self.piece = self.generator.next_piece()
        self.next_piece = self.generator.next_piece()

        self.score = 0
        self.lines = 0

        self.drop_timer = 0.0
        self.lock_timer = 0.0

        self.new_record = False
        self.save_error = False

        self.state = "PLAYING"

    def spawn_piece(self):

        self.piece = self.next_piece
        self.next_piece = self.generator.next_piece()

        self.drop_timer = 0.0
        self.lock_timer = 0.0

        if not self.board.valid(self.piece):
            self.finish_game()



    def move(self, dx, dy):

        if self.board.valid(self.piece, dx, dy):

            self.piece.x += dx
            self.piece.y += dy

            if self.board.valid(self.piece, dy=1):
                self.lock_timer = 0.0

            return True

        return False

    def rotate(self):


        if self.piece.shape_id == 3:
            return

        rotated = self.piece.rotated_shape()

        # Simple wall-kick system
        kicks = [
            (0, 0),
            (-1, 0),
            (1, 0),
            (-2, 0),
            (2, 0),
            (0, -1),
            (-1, -1),
            (1, -1)
        ]

        for dx, dy in kicks:

            if self.board.valid(
                self.piece,
                dx,
                dy,
                rotated
            ):

                self.piece.shape = rotated
                self.piece.x += dx
                self.piece.y += dy

                if self.board.valid(
                    self.piece, dy=1
                ):
                    self.lock_timer = 0.0

                return

    def hard_drop(self):

        while self.move(0, 1):
            pass

        self.lock_piece()



    def lock_piece(self):

        if not self.board.lock(self.piece):

            self.finish_game()
            return

        cleared = self.board.clear_lines()

        self.lines += cleared


        self.score += cleared * 10

        self.update_record()
        self.spawn_piece()

    def update_record(self):

        if self.score > self.best_score:

            self.best_score = self.score
            self.new_record = True

            self.save_error = not save_record(
                self.best_score
            )

    def finish_game(self):

        self.update_record()
        self.state = "GAME_OVER"



    def handle_events(self):

        for event in pygame.event.get():

            if event.type == pygame.QUIT:

                self.update_record()
                self.running = False
                return

            if event.type == pygame.MOUSEBUTTONDOWN:

                if event.button != 1:
                    continue

                pos = event.pos

                if self.state == "MENU":

                    if self.play_button.collidepoint(pos):
                        self.start_game()

                    elif self.help_button.collidepoint(pos):
                        self.state = "HELP"

                elif self.state == "HELP":

                    if self.back_button.collidepoint(pos):
                        self.state = "MENU"

                elif self.state == "GAME_OVER":

                    if self.restart_button.collidepoint(pos):
                        self.start_game()

                    elif self.menu_button.collidepoint(pos):
                        self.state = "MENU"

            if event.type != pygame.KEYDOWN:
                continue

            key = event.key

            if self.state == "MENU":

                if key == pygame.K_RETURN:
                    self.start_game()

                elif key == pygame.K_ESCAPE:
                    self.running = False

            elif self.state == "HELP":

                if key == pygame.K_ESCAPE:
                    self.state = "MENU"

            elif self.state == "PLAYING":

                if key == pygame.K_LEFT:
                    self.move(-1, 0)

                elif key == pygame.K_RIGHT:
                    self.move(1, 0)

                elif key == pygame.K_UP:
                    self.rotate()

                elif key == pygame.K_SPACE:
                    self.hard_drop()

                elif key == pygame.K_p:
                    self.state = "PAUSED"

                elif key == pygame.K_ESCAPE:

                    self.update_record()
                    self.state = "MENU"

            elif self.state == "PAUSED":

                if key == pygame.K_p:
                    self.state = "PLAYING"

                elif key == pygame.K_ESCAPE:

                    self.update_record()
                    self.state = "MENU"

            elif self.state == "GAME_OVER":

                if key == pygame.K_r:
                    self.start_game()

                elif key in (
                    pygame.K_m,
                    pygame.K_ESCAPE
                ):
                    self.state = "MENU"



    def update(self, dt):

        if self.state != "PLAYING":
            return

        keys = pygame.key.get_pressed()

        interval = (
            FAST_DROP_INTERVAL
            if keys[pygame.K_DOWN]
            else DROP_INTERVAL
        )

        self.drop_timer += dt

        while self.drop_timer >= interval:

            self.drop_timer -= interval

            if not self.move(0, 1):

                self.drop_timer = 0.0
                break

        grounded = not self.board.valid(
            self.piece, dy=1
        )

        if grounded:

            self.lock_timer += dt

            if self.lock_timer >= LOCK_DELAY:
                self.lock_piece()

        else:
            self.lock_timer = 0.0



    def text(self, message, font, color, x, y):

        surface = font.render(
            str(message), True, color
        )

        rect = surface.get_rect(
            center=(x, y)
        )

        self.screen.blit(surface, rect)

    def button(self, rect, label):

        pygame.draw.rect(
            self.screen,
            BUTTON_GREEN,
            rect
        )

        pygame.draw.rect(
            self.screen,
            BLACK,
            rect,
            2
        )

        self.text(
            label,
            FONT,
            WHITE,
            rect.centerx,
            rect.centery
        )

    def draw_cell(self, x, y, color):

        if y < 0:
            return

        rect = pygame.Rect(
            x * CELL,
            y * CELL + PANEL_HEIGHT,
            CELL,
            CELL
        )

        pygame.draw.rect(
            self.screen, color, rect
        )

        pygame.draw.rect(
            self.screen, WHITE, rect, 3
        )

        pygame.draw.rect(
            self.screen, BLACK, rect, 1
        )



    def draw_menu(self):

        self.screen.fill(MENU_BG)

        pygame.draw.rect(
            self.screen,
            BLACK,
            (0, 0, WIDTH, HEIGHT),
            10
        )

        self.text(
            "TETRIS",
            MENU_FONT,
            BLACK,
            WIDTH // 2,
            HEIGHT // 2 - 100
        )

        self.button(
            self.play_button, "Play"
        )

        self.button(
            self.help_button, "Help"
        )

        self.text(
            f"Best: {self.best_score}",
            FONT,
            BLACK,
            WIDTH // 2,
            HEIGHT - 80
        )

        self.text(
            "Version 1.1 | NS-007",
            SMALL_FONT,
            BLACK,
            WIDTH // 2,
            HEIGHT - 35
        )



    def draw_help(self):

        self.screen.fill(MENU_BG)

        pygame.draw.rect(
            self.screen,
            BLACK,
            (0, 0, WIDTH, HEIGHT),
            10
        )

        self.text(
            "HOW TO PLAY",
            MENU_FONT,
            BLACK,
            WIDTH // 2,
            50
        )

        instructions = [
            "LEFT / RIGHT - Move",
            "UP - Rotate",
            "DOWN - Fast drop",
            "SPACE - Hard drop",
            "P - Pause",
            "ESC - Main menu",
            "",
            "1. Fill in the lines",
            "2. Get points",
            "3. Don't give up"
        ]

        for index, line in enumerate(instructions):

            self.text(
                line,
                SMALL_FONT,
                BLACK,
                WIDTH // 2,
                110 + index * 25
            )

        self.button(
            self.back_button, "Back"
        )



    def draw_preview(self):

        preview = pygame.Rect(
            215, 5, 75, 40
        )

        pygame.draw.rect(
            self.screen,
            (30, 30, 30),
            preview
        )

        pygame.draw.rect(
            self.screen,
            GRAY,
            preview,
            1
        )

        shape = self.next_piece.shape

        size = min(
            11,
            65 // len(shape[0]),
            32 // len(shape)
        )

        start_x = (
            preview.centerx
            - len(shape[0]) * size // 2
        )

        start_y = (
            preview.centery
            - len(shape) * size // 2
        )

        for y, row in enumerate(shape):
            for x, value in enumerate(row):

                if not value:
                    continue

                rect = pygame.Rect(
                    start_x + x * size,
                    start_y + y * size,
                    size - 1,
                    size - 1
                )

                pygame.draw.rect(
                    self.screen,
                    self.next_piece.color,
                    rect
                )

                pygame.draw.rect(
                    self.screen,
                    WHITE,
                    rect,
                    1
                )



    def draw_panel(self):

        pygame.draw.rect(
            self.screen,
            (50, 50, 50),
            (0, 0, WIDTH, PANEL_HEIGHT)
        )

        pygame.draw.rect(
            self.screen,
            GRAY,
            (0, 0, WIDTH, PANEL_HEIGHT),
            2
        )

        score_text = SMALL_FONT.render(
            f"Score: {self.score}",
            True,
            WHITE
        )

        best_text = SMALL_FONT.render(
            f"Best: {self.best_score}",
            True,
            GOLD
        )

        self.screen.blit(score_text, (10, 5))
        self.screen.blit(best_text, (10, 27))

        self.text(
            "Next:",
            SMALL_FONT,
            WHITE,
            185,
            25
        )

        self.draw_preview()



    def draw_board(self):

        self.screen.fill(BLACK)

        for y in range(ROWS):
            for x in range(COLS):

                color = self.board.grid[y][x]

                if color is not None:

                    self.draw_cell(x, y, color)

                else:

                    size = CELL // 3
                    offset = (CELL - size) // 2

                    rect = pygame.Rect(
                        x * CELL + offset,
                        y * CELL + offset + PANEL_HEIGHT,
                        size,
                        size
                    )

                    pygame.draw.rect(
                        self.screen,
                        (80, 80, 80),
                        rect
                    )

        for x, y in self.piece.cells():

            self.draw_cell(
                x, y, self.piece.color
            )

        self.draw_panel()



    def draw_pause(self):

        self.draw_board()

        self.screen.blit(
            self.overlay, (0, 0)
        )

        self.text(
            "PAUSED",
            MENU_FONT,
            WHITE,
            WIDTH // 2,
            260
        )

        self.text(
            "P - Continue",
            FONT,
            WHITE,
            WIDTH // 2,
            330
        )

        self.text(
            "ESC - Menu",
            SMALL_FONT,
            WHITE,
            WIDTH // 2,
            370
        )



    def draw_game_over(self):

        self.screen.fill(MENU_BG)

        pygame.draw.rect(
            self.screen,
            BLACK,
            (0, 0, WIDTH, HEIGHT),
            10
        )

        self.text(
            "GAME OVER",
            MENU_FONT,
            BLACK,
            WIDTH // 2,
            120
        )

        self.text(
            f"Score: {self.score}",
            FONT,
            BLACK,
            WIDTH // 2,
            210
        )

        self.text(
            f"Best: {self.best_score}",
            FONT,
            BLACK,
            WIDTH // 2,
            250
        )

        self.text(
            f"Lines: {self.lines}",
            FONT,
            BLACK,
            WIDTH // 2,
            290
        )

        if self.new_record:

            self.text(
                "NEW RECORD!",
                FONT,
                (60, 120, 30),
                WIDTH // 2,
                340
            )

        self.button(
            self.restart_button,
            "Play again"
        )

        self.button(
            self.menu_button,
            "Main menu"
        )

        if self.save_error:

            self.text(
                "Unable to save record",
                SMALL_FONT,
                BLACK,
                WIDTH // 2,
                570
            )

        self.text(
            "NESTIMS | Version 2.0",
            SMALL_FONT,
            BLACK,
            WIDTH // 2,
            610
        )



    def render(self):

        if self.state == "MENU":
            self.draw_menu()

        elif self.state == "HELP":
            self.draw_help()

        elif self.state == "PLAYING":
            self.draw_board()

        elif self.state == "PAUSED":
            self.draw_pause()

        elif self.state == "GAME_OVER":
            self.draw_game_over()

        pygame.display.flip()



    def run(self):

        while self.running:

            dt = min(
                self.clock.tick(FPS) / 1000.0,
                0.1
            )

            self.handle_events()

            if not self.running:
                break

            self.update(dt)
            self.render()

        pygame.quit()


def main():

    game = Game()
    game.run()


if __name__ == "__main__":
    main()
