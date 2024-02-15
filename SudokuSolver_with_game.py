# %%
import pygame
import sys
from typing import List, Tuple
import random


def generate_solved_sudoku_board() -> List[List[int]]:
    base = 3
    side = base * base
    nums = random.sample(range(1, side + 1), side)
    board = [[0] * side for _ in range(side)]

    for r in range(side):
        for c in range(side):
            board[r][c] = nums[(base * (r % base) + r // base + c) % side]

    return board


def remove_values(board: List[List[int]], num_to_remove: int) -> List[List[int]]:
    for _ in range(num_to_remove):
        row, col = random.randint(0, 8), random.randint(0, 8)
        while board[row][col] == 0:
            row, col = random.randint(0, 8), random.randint(0, 8)
        board[row][col] = 0
    return board


def random_generator(_, _1, _2) -> List[List[int]]:
    temp = generate_solved_sudoku_board()
    temp = remove_values(temp, random.randint(45, 70))
    return temp


def is_valid(board: List[List[int]], row: int, col: int, val: int) -> bool:
    return (
        val not in board[row]
        and val not in [board[i][col] for i in range(9)]
        and val
        not in [
            board[i][j]
            for i in range(row // 3 * 3, row // 3 * 3 + 3)
            for j in range(col // 3 * 3, col // 3 * 3 + 3)
        ]
    )


def solve(
    board: List[List[int]], row: int, col: int
) -> Tuple[bool, List[List[int]] | None]:
    if row == 9:
        return True, board
    elif col == 9:
        return solve(board, row + 1, 0)
    elif board[row][col]:
        return solve(board, row, col + 1)
    else:
        for val in range(1, 10):
            if is_valid(board, row, col, val):
                board[row][col] = val
                if solve(board, row, col + 1)[0]:
                    return True, board
                board[row][col] = 0

        return False, None


def is_valid_all(board: List[List[int]], dummy1, dummy2):
    for i in range(len(board)):
        for j in range(len(board[i])):
            if board[i].count(board[i][j]) > 1:
                return False, (i, j)
    cols = [[board[k][l] for k in range(len(board[l]))] for l in range(len(board))]
    for i in range(len(cols)):
        for j in range(len(cols[i])):
            if cols[i].count(cols[i][j]) > 1:
                return False, (j, i)
    for i in range(len(board)):
        for j in range(len(board[i])):
            if [
                board[r][c]
                for r in range(i // 3 * 3, i // 3 * 3 + 3)
                for c in range(j // 3 * 3, j // 3 * 3 + 3)
            ].count(board[i][j]) > 1:
                return False, (i, j)

    return (True,)


class Tile:
    def __init__(self, cord: Tuple[int, int], size: int, val: int = 0) -> None:
        self.is_selected = False
        self.x, self.y = cord
        self.width = size
        self.val = val
        self.is_preset = False
        self.comp_preset = False
        self.wrong = False

    def draw_tile(self, surface: pygame.Surface) -> None:
        if self.wrong and self.is_selected:
            color = (139, 0, 0)
        elif self.wrong:
            color = "red"
        elif self.is_selected:
            color = "grey"
        else:
            color = "white"

        pygame.draw.rect(
            surface,
            color,
            (self.x, self.y, self.width, self.width),
        )
        if self.val != 0:
            text_col = (
                "black"
                if not self.is_preset and not self.comp_preset
                else "red" if not self.comp_preset else "blue"
            )
            text = pygame.font.Font(None, 36).render(str(self.val), True, text_col)
            text_rect = text.get_rect(
                center=(self.x + self.width // 2, self.y + self.width // 2)
            )

            surface.blit(text, text_rect)


class Button:
    def __init__(
        self,
        cords: Tuple[int, int],
        size: Tuple[int, int],
        text: str,
        text_color: str = "black",
        font_size: int = 36,
    ) -> None:
        self.x, self.y = cords
        self.width, self.height = size
        self.text = text
        self.is_pressed = False  # New state variable
        self.font_size = font_size
        self.text_color = text_color

    def draw_button(self, surface: pygame.Surface) -> None:
        color = "white"
        if self.is_pressed:
            color = "grey"  # Change color if button is pressed
        pygame.draw.rect(surface, color, (self.x, self.y, self.width, self.height))
        text = pygame.font.Font(None, self.font_size).render(
            self.text, True, self.text_color
        )
        surface.blit(text, (self.x + 10, self.y + 10))  # Adjust text position

    def check_collision(self, mouse_x: int, mouse_y: int) -> bool:
        return (
            self.x <= mouse_x <= self.x + self.width
            and self.y <= mouse_y <= self.y + self.height
        )


class Screen:
    def __init__(self, width: int, height: int, caption: str) -> None:
        pygame.init()
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption(caption)
        self.clock = pygame.time.Clock()
        self.board: List[List[Tile]] = None
        self.selected_tile = None
        self.buttons: set[Button] = set()
        self.output = None
        self.button_funcs = {}
        self.empty = None

    def setup(self) -> None:
        padding = 5
        size = (self.width - 10 * padding) // 9
        board = []
        for i in range(1, 10):
            temp = []
            for j in range(1, 10):
                offsetter_x = 0
                offsetter_y = 0
                if j <= 3:
                    offsetter_x = -3
                elif j > 6:
                    offsetter_x = 3
                if i <= 3:
                    offsetter_y = -3
                elif i > 6:
                    offsetter_y = 3
                tile = Tile(
                    (
                        padding * j + size * (j - 1) + offsetter_x,
                        padding * i + size * (i - 1) + offsetter_y,
                    ),
                    size,
                )
                temp.append(tile)
            board.append(temp)

        self.board = board

        tile_size = self.board[-1][0].width

        valid_button_x = self.board[-1][0].x + 18
        valid_button_y = self.board[-1][0].y + tile_size + 10

        valid_button = Button(
            (valid_button_x, valid_button_y),
            (tile_size * 3, tile_size),
            "Check Validity",
        )
        self.buttons.add(valid_button)
        self.button_funcs[valid_button] = is_valid_all

        solve_it_button_x = valid_button_x + valid_button.width + 5
        solve_it_button_y = valid_button_y

        solve_it_button = Button(
            (solve_it_button_x, solve_it_button_y),
            (tile_size * 3, tile_size),
            "Solve it",
        )
        self.buttons.add(solve_it_button)
        self.button_funcs[solve_it_button] = solve

        reset_button_x = solve_it_button_x + solve_it_button.width + 5
        reset_button_y = solve_it_button_y

        reset = Button(
            (reset_button_x, reset_button_y), (tile_size * 3, tile_size), "Reset"
        )

        self.buttons.add(reset)
        self.button_funcs[reset] = self.reseter

        random_generate = Button(
            (valid_button_x, valid_button_y + tile_size + 5),
            (tile_size * 3, tile_size),
            "Random Generation",
            font_size=24,
        )
        self.buttons.add(random_generate)
        self.button_funcs[random_generate] = random_generator

        self.box = Button(
            (solve_it_button_x, solve_it_button_y + tile_size + 5),
            (tile_size * 3, tile_size),
            "",
            "green",
        )
        self.empty = Button(
            (reset_button_x, reset_button_y + tile_size + 5),
            (tile_size * 3, tile_size),
            "",
        )

    def reseter(self, _, _1, _2):
        for row in self.board:
            for tile in row:
                tile.val = 0
                tile.is_preset = False
                tile.comp_preset = False
                tile.wrong = False

        self.box.text = ""

    def handle_mouse_click(
        self,
        mouse_x: int,
        mouse_y: int,
        is_pressed: bool,
    ) -> None:
        if mouse_y <= 600 and is_pressed:
            for row in self.board:
                for tile in row:
                    if not tile.comp_preset:
                        if (
                            tile.x <= mouse_x <= tile.x + tile.width
                            and tile.y <= mouse_y <= tile.y + tile.width
                        ):
                            tile.is_selected = (
                                not tile.is_selected
                            )  # Toggle the selection state
                            if tile.is_selected:
                                self.selected_tile = tile
                        else:
                            tile.is_selected = False
        else:
            self.selected_tile = None
            for button in self.buttons:
                if button.check_collision(mouse_x, mouse_y):
                    button.is_pressed = is_pressed
                    if is_pressed:
                        self.output = self.button_funcs[button](
                            [
                                [
                                    j.val if (j.comp_preset or j.is_preset) else 0
                                    for j in self.board[i]
                                ]
                                for i in range(len(self.board))
                            ],
                            0,
                            0,
                        )
                        if button.text == "Solve it":
                            for i in range(len(self.board)):
                                for j in range(len(self.board[i])):
                                    self.board[i][j].val = self.output[1][i][j]
                        if button.text == "Check Validity":
                            if len(self.output) > 1:
                                i, j = self.output[1]
                                self.board[i][j].wrong = True

                            else:
                                self.box.text = "CONGRATS!!!"
                                for i in range(len(self.board)):
                                    for j in range(len(self.board[i])):
                                        self.board[i][j].wrong = False
                        if button.text == "Random Generation":
                            for i in range(len(self.board)):
                                for j in range(len(self.board[i])):
                                    self.board[i][j].val = self.output[i][j]
                                    self.board[i][j].comp_preset = (
                                        True if self.output[i][j] else False
                                    )
                    break

    def handle_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                self.handle_mouse_click(mouse_x, mouse_y, True)
            if event.type == pygame.MOUSEBUTTONUP:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                self.handle_mouse_click(mouse_x, mouse_y, False)
            if event.type == pygame.KEYDOWN:
                keys = pygame.key.get_pressed()
                for i in range(len(keys)):
                    if keys[i]:
                        if self.selected_tile:
                            if pygame.K_0 <= i <= pygame.K_9:
                                if not self.selected_tile.is_preset:
                                    self.selected_tile.val = i - pygame.K_0
                                break

                            if pygame.K_s == i:
                                self.selected_tile.is_preset = (
                                    not self.selected_tile.is_preset
                                )
                        if pygame.K_a == i:
                            for i in range(len(self.board)):
                                for j in range(len(self.board[i])):
                                    self.board[i][j].is_preset = True
                        if pygame.K_u == i:
                            for i in range(len(self.board)):
                                for j in range(len(self.board[i])):
                                    self.board[i][j].is_preset = False

    def update_display(self) -> None:
        pygame.display.flip()

    def draw(self) -> None:
        for row in self.board:
            for tile in row:
                tile.draw_tile(self.screen)

        for button in self.buttons:
            button.draw_button(self.screen)

        self.box.draw_button(self.screen)
        self.empty.draw_button(self.screen)

    def run(self) -> None:
        self.setup()
        while True:
            self.handle_events()
            # Game logic goes here

            # Drawing code goes here
            self.screen.fill("black")
            self.draw()

            self.update_display()
            self.clock.tick(60)  # Adjust the frame rate as needed


if __name__ == "__main__":
    screen = Screen(600, 750, "Sudoku")
    screen.run()

# %%
