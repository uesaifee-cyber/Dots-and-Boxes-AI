
import tkinter as tk
from tkinter import messagebox
import math

# -------------------- GAME SETTINGS --------------------

MIN_SIZE = 3
MAX_SIZE = 10

HUMAN = 0
AI = 1

DOT_GAP = 55
MARGIN = 35
DOT_RADIUS = 5

SEARCH_DEPTH = 1

HUMAN_COLOR = "#2878D0"
AI_COLOR = "#E67E22"
BACKGROUND = "#F7F7F7"
EMPTY_LINE_COLOR = "#C7C7C7"


# -------------------- GAME LOGIC --------------------

class DotsAndBoxes:

    @staticmethod
    def new_state(n):
        horizontal = [
            [False for _ in range(n)]
            for _ in range(n + 1)
        ]

        vertical = [
            [False for _ in range(n + 1)]
            for _ in range(n)
        ]

        owners = [
            [-1 for _ in range(n)]
            for _ in range(n)
        ]

        scores = [0, 0]

        return horizontal, vertical, owners, scores

    @staticmethod
    def copy_state(state):
        horizontal, vertical, owners, scores = state

        return (
            [row[:] for row in horizontal],
            [row[:] for row in vertical],
            [row[:] for row in owners],
            scores[:]
        )

    @staticmethod
    def valid_move(state, move, n):
        horizontal, vertical, owners, scores = state

        line_type, row, col = move

        if line_type == 0:
            return (
                0 <= row <= n
                and 0 <= col < n
                and not horizontal[row][col]
            )

        if line_type == 1:
            return (
                0 <= row < n
                and 0 <= col <= n
                and not vertical[row][col]
            )

        return False

    @staticmethod
    def get_moves(state, n):
        horizontal, vertical, owners, scores = state
        moves = []

        for row in range(n + 1):
            for col in range(n):
                if not horizontal[row][col]:
                    moves.append((0, row, col))

        for row in range(n):
            for col in range(n + 1):
                if not vertical[row][col]:
                    moves.append((1, row, col))

        return moves

    @staticmethod
    def count_box_sides(state, row, col):
        horizontal, vertical, owners, scores = state

        count = 0

        if horizontal[row][col]:
            count += 1

        if horizontal[row + 1][col]:
            count += 1

        if vertical[row][col]:
            count += 1

        if vertical[row][col + 1]:
            count += 1

        return count

    @staticmethod
    def apply_move(state, player, move, n):

        if not DotsAndBoxes.valid_move(state, move, n):
            return -1

        horizontal, vertical, owners, scores = state

        line_type, row, col = move

        if line_type == 0:
            horizontal[row][col] = True
            possible_boxes = [
                (row - 1, col),
                (row, col)
            ]
        else:
            vertical[row][col] = True
            possible_boxes = [
                (row, col - 1),
                (row, col)
            ]

        completed = 0

        for box_row, box_col in possible_boxes:

            if not (
                0 <= box_row < n
                and 0 <= box_col < n
            ):
                continue

            if owners[box_row][box_col] != -1:
                continue

            if DotsAndBoxes.count_box_sides(
                state, box_row, box_col
            ) == 4:

                owners[box_row][box_col] = player
                completed += 1

        scores[player] += completed

        return completed

    @staticmethod
    def is_game_over(state):
        horizontal, vertical, owners, scores = state

        return (
            all(all(row) for row in horizontal)
            and all(all(row) for row in vertical)
        )

    @staticmethod
    def evaluate(state, player_to_move, n):

        horizontal, vertical, owners, scores = state

        value = (scores[AI] - scores[HUMAN]) * 100

        for row in range(n):
            for col in range(n):

                if owners[row][col] != -1:
                    continue

                sides = DotsAndBoxes.count_box_sides(
                    state, row, col
                )

                if sides == 3:
                    if player_to_move == AI:
                        value += 12
                    else:
                        value -= 12

                elif sides == 2:
                    value += 1 if player_to_move == AI else -1

        return value

    @staticmethod
    def minimax(state, player, depth, alpha, beta, n):

        if depth == 0 or DotsAndBoxes.is_game_over(state):
            return DotsAndBoxes.evaluate(
                state, player, n
            )

        moves = DotsAndBoxes.get_moves(state, n)

        if not moves:
            return DotsAndBoxes.evaluate(
                state, player, n
            )

        maximizing = (player == AI)

        # Try box-completing moves first.
        ordered_moves = []

        for move in moves:
            test_state = DotsAndBoxes.copy_state(state)

            gained = DotsAndBoxes.apply_move(
                test_state, player, move, n
            )

            ordered_moves.append((gained, move))

        ordered_moves.sort(
            key=lambda item: item[0],
            reverse=True
        )

        if maximizing:
            best_value = -math.inf

            for gained, move in ordered_moves:

                new_state = DotsAndBoxes.copy_state(state)

                DotsAndBoxes.apply_move(
                    new_state, player, move, n
                )

                next_player = (
                    player if gained > 0 else 1 - player
                )

                value = DotsAndBoxes.minimax(
                    new_state,
                    next_player,
                    depth - 1,
                    alpha,
                    beta,
                    n
                )

                best_value = max(best_value, value)
                alpha = max(alpha, best_value)

                if beta <= alpha:
                    break

            return best_value

        else:
            best_value = math.inf

            for gained, move in ordered_moves:

                new_state = DotsAndBoxes.copy_state(state)

                DotsAndBoxes.apply_move(
                    new_state, player, move, n
                )

                next_player = (
                    player if gained > 0 else 1 - player
                )

                value = DotsAndBoxes.minimax(
                    new_state,
                    next_player,
                    depth - 1,
                    alpha,
                    beta,
                    n
                )

                best_value = min(best_value, value)
                beta = min(beta, best_value)

                if beta <= alpha:
                    break

            return best_value

    @staticmethod
    def choose_ai_move(state, n):

        moves = DotsAndBoxes.get_moves(state, n)

        if not moves:
            return None

        best_move = None
        best_value = -math.inf

        alpha = -math.inf
        beta = math.inf

        # Prioritize moves that complete boxes.
        ordered_moves = []

        for move in moves:

            test_state = DotsAndBoxes.copy_state(state)

            gained = DotsAndBoxes.apply_move(
                test_state, AI, move, n
            )

            ordered_moves.append((gained, move))

        ordered_moves.sort(
            key=lambda item: item[0],
            reverse=True
        )

        for gained, move in ordered_moves:

            new_state = DotsAndBoxes.copy_state(state)

            DotsAndBoxes.apply_move(
                new_state, AI, move, n
            )

            next_player = AI if gained > 0 else HUMAN

            value = DotsAndBoxes.minimax(
                new_state,
                next_player,
                SEARCH_DEPTH,
                alpha,
                beta,
                n
            )

            if value > best_value:
                best_value = value
                best_move = move

            alpha = max(alpha, best_value)

        return best_move


# -------------------- GRAPHICAL INTERFACE --------------------

class DotsAndBoxesGUI:

    def __init__(self, root):

        self.root = root
        self.root.title("Dots and Boxes - Human vs AI")
        self.root.configure(bg=BACKGROUND)
        self.root.resizable(False, False)

        self.n = 8
        self.state = None

        self.turn = HUMAN
        self.game_over = False
        self.ai_pending = False

        self.selection_frame = None
        self.game_frame = None

        self.show_start_screen()

    # -------------------- START SCREEN --------------------

    def show_start_screen(self):

        if self.game_frame:
            self.game_frame.destroy()
            self.game_frame = None

        self.selection_frame = tk.Frame(
            self.root,
            bg=BACKGROUND,
            padx=35,
            pady=35
        )

        self.selection_frame.pack(
            padx=20,
            pady=35
        )

        tk.Label(
            self.selection_frame,
            text="DOTS AND BOXES",
            font=("Arial", 25, "bold"),
            bg=BACKGROUND,
            fg="#222222"
        ).pack(pady=15)

        tk.Label(
            self.selection_frame,
            text="Human vs AI",
            font=("Arial", 14),
            bg=BACKGROUND
        ).pack(pady=5)

        tk.Label(
            self.selection_frame,
            text="Choose Your Board Size",
            font=("Arial", 15, "bold"),
            bg=BACKGROUND
        ).pack(pady=(25, 10))

        self.size_var = tk.StringVar(value="8 x 8")

        size_options = [
            f"{size} x {size}"
            for size in range(MIN_SIZE, MAX_SIZE + 1)
        ]

        size_menu = tk.OptionMenu(
            self.selection_frame,
            self.size_var,
            *size_options
        )

        size_menu.config(
            font=("Arial", 13),
            width=12,
            bg="white"
        )

        size_menu.pack(pady=10)

        self.box_count_label = tk.Label(
            self.selection_frame,
            text="64 boxes",
            font=("Arial", 11),
            bg=BACKGROUND,
            fg="#555555"
        )

        self.box_count_label.pack(pady=5)

        self.size_var.trace_add(
            "write",
            self.update_box_count
        )

        tk.Button(
            self.selection_frame,
            text="START GAME",
            font=("Arial", 13, "bold"),
            width=18,
            bg="#2878D0",
            fg="white",
            activebackground="#185CA8",
            activeforeground="white",
            command=self.start_game
        ).pack(pady=25)

        tk.Label(
            self.selection_frame,
            text="Select a board from 3 x 3 to 10 x 10.",
            font=("Arial", 10),
            bg=BACKGROUND,
            fg="#555555"
        ).pack(pady=5)

    def update_box_count(self, *args):

        try:
            selected = int(
                self.size_var.get().split(" ")[0]
            )

            self.box_count_label.config(
                text=f"{selected * selected} boxes"
            )

        except (ValueError, IndexError):
            pass

    # -------------------- START GAME --------------------

    def start_game(self):

        self.n = int(
            self.size_var.get().split(" ")[0]
        )

        if not MIN_SIZE <= self.n <= MAX_SIZE:
            messagebox.showerror(
                "Invalid Size",
                "Choose a board size from 3 x 3 to 10 x 10."
            )
            return

        self.state = DotsAndBoxes.new_state(self.n)

        self.turn = HUMAN
        self.game_over = False
        self.ai_pending = False

        self.selection_frame.destroy()
        self.selection_frame = None

        self.create_game_screen()

        self.draw_board()
        self.update_status()

    # -------------------- GAME SCREEN --------------------

    def create_game_screen(self):

        self.game_frame = tk.Frame(
            self.root,
            bg=BACKGROUND
        )

        self.game_frame.pack(padx=10, pady=10)

        tk.Label(
            self.game_frame,
            text=f"DOTS AND BOXES - {self.n} x {self.n}",
            font=("Arial", 20, "bold"),
            bg=BACKGROUND
        ).pack(pady=10)

        self.score_label = tk.Label(
            self.game_frame,
            text="",
            font=("Arial", 14, "bold"),
            bg=BACKGROUND
        )

        self.score_label.pack(pady=5)

        self.status_label = tk.Label(
            self.game_frame,
            text="",
            font=("Arial", 12),
            bg=BACKGROUND
        )

        self.status_label.pack(pady=5)

        self.canvas_size = (
            2 * MARGIN + self.n * DOT_GAP
        )

        self.canvas = tk.Canvas(
            self.game_frame,
            width=self.canvas_size,
            height=self.canvas_size,
            bg="white",
            highlightthickness=1,
            highlightbackground="#BBBBBB"
        )

        self.canvas.pack(padx=10, pady=10)

        self.canvas.bind(
            "<Button-1>",
            self.handle_click
        )

        button_frame = tk.Frame(
            self.game_frame,
            bg=BACKGROUND
        )

        button_frame.pack(pady=10)

        tk.Button(
            button_frame,
            text="New Game",
            font=("Arial", 11, "bold"),
            width=12,
            bg="#2878D0",
            fg="white",
            command=self.new_game
        ).pack(side=tk.LEFT, padx=8)

        tk.Button(
            button_frame,
            text="Exit",
            font=("Arial", 11),
            width=12,
            command=self.root.destroy
        ).pack(side=tk.LEFT, padx=8)

        tk.Label(
            self.game_frame,
            text=(
                "Click near the middle of a grey line to draw it.\n"
                "Completing a box earns one point and another turn."
            ),
            font=("Arial", 10),
            bg=BACKGROUND,
            fg="#555555",
            justify=tk.CENTER
        ).pack(pady=8)

    # -------------------- DRAWING --------------------

    def get_coordinates(self, row, col):

        return (
            MARGIN + col * DOT_GAP,
            MARGIN + row * DOT_GAP
        )

    def draw_board(self):

        self.canvas.delete("all")

        horizontal, vertical, owners, scores = self.state

        # Draw completed boxes.
        for row in range(self.n):
            for col in range(self.n):

                owner = owners[row][col]

                if owner == -1:
                    continue

                x1, y1 = self.get_coordinates(row, col)
                x2, y2 = self.get_coordinates(row + 1, col + 1)

                color = (
                    "#D9EAFB" if owner == HUMAN
                    else "#FCE4CC"
                )

                self.canvas.create_rectangle(
                    x1, y1, x2, y2,
                    fill=color,
                    outline=""
                )

        # Draw horizontal lines.
        for row in range(self.n + 1):
            for col in range(self.n):

                x1, y1 = self.get_coordinates(row, col)
                x2, y2 = self.get_coordinates(row, col + 1)

                if horizontal[row][col]:
                    color = self.get_line_color(
                        row, col, 0
                    )
                    width = 5
                else:
                    color = EMPTY_LINE_COLOR
                    width = 3

                self.canvas.create_line(
                    x1, y1, x2, y2,
                    fill=color,
                    width=width,
                    capstyle=tk.ROUND
                )

        # Draw vertical lines.
        for row in range(self.n):
            for col in range(self.n + 1):

                x1, y1 = self.get_coordinates(row, col)
                x2, y2 = self.get_coordinates(row + 1, col)

                if vertical[row][col]:
                    color = self.get_line_color(
                        row, col, 1
                    )
                    width = 5
                else:
                    color = EMPTY_LINE_COLOR
                    width = 3

                self.canvas.create_line(
                    x1, y1, x2, y2,
                    fill=color,
                    width=width,
                    capstyle=tk.ROUND
                )

        # Draw dots.
        for row in range(self.n + 1):
            for col in range(self.n + 1):

                x, y = self.get_coordinates(row, col)

                self.canvas.create_oval(
                    x - DOT_RADIUS,
                    y - DOT_RADIUS,
                    x + DOT_RADIUS,
                    y + DOT_RADIUS,
                    fill="#222222",
                    outline="#222222"
                )

        self.update_score()

    def get_line_color(self, row, col, line_type):

        horizontal, vertical, owners, scores = self.state

        if line_type == 0:
            boxes = [
                (row - 1, col),
                (row, col)
            ]
        else:
            boxes = [
                (row, col - 1),
                (row, col)
            ]

        for box_row, box_col in boxes:

            if (
                0 <= box_row < self.n
                and 0 <= box_col < self.n
            ):

                owner = owners[box_row][box_col]

                if owner == HUMAN:
                    return HUMAN_COLOR

                if owner == AI:
                    return AI_COLOR

        return "#555555"

    def update_score(self):

        scores = self.state[3]

        self.score_label.config(
            text=(
                f"YOU: {scores[HUMAN]}      "
                f"AI: {scores[AI]}"
            )
        )

    def update_status(self):

        if self.game_over:
            return

        if self.turn == HUMAN:

            self.status_label.config(
                text="Your turn - Select a line",
                fg=HUMAN_COLOR
            )

        else:

            self.status_label.config(
                text="AI is thinking...",
                fg=AI_COLOR
            )

    # -------------------- HUMAN MOVE --------------------

    def handle_click(self, event):

        if (
            self.game_over
            or self.turn != HUMAN
            or self.ai_pending
        ):
            return

        x = event.x
        y = event.y

        best_move = None
        best_distance = float("inf")

        # Find nearest available horizontal line.
        for row in range(self.n + 1):
            for col in range(self.n):

                x1, y1 = self.get_coordinates(row, col)
                x2, y2 = self.get_coordinates(row, col + 1)

                mid_x = (x1 + x2) / 2
                mid_y = (y1 + y2) / 2

                distance = math.hypot(
                    x - mid_x,
                    y - mid_y
                )

                move = (0, row, col)

                if (
                    distance < best_distance
                    and DotsAndBoxes.valid_move(
                        self.state, move, self.n
                    )
                ):

                    best_distance = distance
                    best_move = move

        # Find nearest available vertical line.
        for row in range(self.n):
            for col in range(self.n + 1):

                x1, y1 = self.get_coordinates(row, col)
                x2, y2 = self.get_coordinates(row + 1, col)

                mid_x = (x1 + x2) / 2
                mid_y = (y1 + y2) / 2

                distance = math.hypot(
                    x - mid_x,
                    y - mid_y
                )

                move = (1, row, col)

                if (
                    distance < best_distance
                    and DotsAndBoxes.valid_move(
                        self.state, move, self.n
                    )
                ):

                    best_distance = distance
                    best_move = move

        if best_move is None or best_distance > 17:
            return

        self.play_move(HUMAN, best_move)

    # -------------------- PLAY MOVE --------------------

    def play_move(self, player, move):

        completed = DotsAndBoxes.apply_move(
            self.state, player, move, self.n
        )

        if completed == -1:
            return

        self.draw_board()

        if DotsAndBoxes.is_game_over(self.state):
            self.finish_game()
            return

        if completed > 0:
            self.turn = player
        else:
            self.turn = 1 - player

        self.update_status()

        if self.turn == AI:
            self.schedule_ai_turn()

    # -------------------- AI TURN --------------------

    def schedule_ai_turn(self):

        if self.game_over or self.ai_pending:
            return

        self.ai_pending = True

        self.status_label.config(
            text="AI is thinking...",
            fg=AI_COLOR
        )

        self.root.after(150, self.ai_turn)

    def ai_turn(self):

        self.ai_pending = False

        if self.game_over or self.turn != AI:
            return

        move = DotsAndBoxes.choose_ai_move(
            self.state, self.n
        )

        if move is None:
            self.finish_game()
            return

        self.play_move(AI, move)

    # -------------------- GAME END --------------------

    def finish_game(self):

        self.game_over = True

        self.update_score()

        human_score = self.state[3][HUMAN]
        ai_score = self.state[3][AI]

        if human_score > ai_score:
            result = "Congratulations! You won!"

        elif ai_score > human_score:
            result = "AI wins! Better luck next time."

        else:
            result = "It's a draw!"

        self.status_label.config(
            text=result,
            fg="#222222"
        )

        messagebox.showinfo(
            "Game Over",
            (
                f"{result}\n\n"
                f"Your Score: {human_score}\n"
                f"AI Score: {ai_score}"
            )
        )

    # -------------------- NEW GAME --------------------

    def new_game(self):

        # Return to the size-selection screen.
        self.show_start_screen()


# -------------------- MAIN PROGRAM --------------------

def main():

    root = tk.Tk()

    DotsAndBoxesGUI(root)

    root.mainloop()


if __name__ == "__main__":
    main()
