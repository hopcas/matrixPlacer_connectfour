"""
四子棋（Connect Four）— 图形界面版

规则与控制台版相同：
- 6×7 棋盘，点击某一列落子
- 棋子受重力下落到该列最低空位
- X 先手，横/纵/斜连成 4 子获胜；棋盘满则平局
"""

import tkinter as tk
from tkinter import messagebox


BG = "#F5F0E6"
BOARD_WOOD = "#D4A757"
GRID_LINE = "#3D2B1F"
BOARD_BORDER = "#4A3426"
TITLE_FG = "#2C2416"
SUBTITLE_FG = "#8A7A68"
INFO_FG = "#5C4E3A"
MARK_X = "#1A1A1A"
MARK_O = "#8B3A2A"
HOLE = "#EDE4D4"
PREVIEW = "#C9B48A"


class ConnectFourGUI:
    """四子棋 GUI：纵向重力落子，连四判定与控制台版一致。"""

    DIRECTIONS = [(0, 1), (1, 0), (1, 1), (1, -1)]

    def __init__(self, rows=6, cols=7, win_length=4):
        self.rows = rows
        self.cols = cols
        self.win_length = win_length
        self.board = [[' ' for _ in range(cols)] for _ in range(rows)]
        self.current_player = 'X'
        self.moves_count = 0
        self.max_moves = rows * cols
        self.game_over = False
        self.last_move = None
        self.dropping = False

        self.cell = max(52, min(72, 480 // max(rows, cols)))
        self.pad = 12
        self.border = 6
        board_w = self.cols * self.cell + 2 * self.pad + 2 * self.border
        board_h = self.rows * self.cell + 2 * self.pad + 2 * self.border
        win_w = max(460, board_w + 40)
        win_h = board_h + 220

        self.root = tk.Tk()
        self.root.title("四子棋 · Connect Four")
        self.root.geometry(f"{win_w}x{win_h}")
        self.root.resizable(False, False)
        self.root.configure(bg=BG)

        self.canvas = None
        self.hover_col = None
        self.create_widgets(board_w, board_h)
        self.draw_board()

    def create_widgets(self, board_w, board_h):
        tk.Label(
            self.root,
            text="四子棋",
            font=("Microsoft YaHei UI", 20, "bold"),
            bg=BG,
            fg=TITLE_FG,
        ).pack(pady=(16, 2))

        tk.Label(
            self.root,
            text="点击列落子 · 重力下落 · 横/纵/斜连四为胜",
            font=("Microsoft YaHei UI", 10),
            bg=BG,
            fg=SUBTITLE_FG,
        ).pack(pady=(0, 8))

        self.info_label = tk.Label(
            self.root,
            text="当前玩家: X",
            font=("Microsoft YaHei UI", 12),
            bg=BG,
            fg=INFO_FG,
        )
        self.info_label.pack(pady=2)

        self.moves_label = tk.Label(
            self.root,
            text=f"已落子: {self.moves_count}/{self.max_moves}",
            font=("Microsoft YaHei UI", 10),
            bg=BG,
            fg=SUBTITLE_FG,
        )
        self.moves_label.pack(pady=(0, 6))

        self.canvas = tk.Canvas(
            self.root,
            width=board_w,
            height=board_h,
            bg=BG,
            highlightthickness=0,
            cursor="hand2",
        )
        self.canvas.pack(pady=4)
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        self.canvas.bind("<Motion>", self.on_canvas_motion)
        self.canvas.bind("<Leave>", self.on_canvas_leave)

        control_frame = tk.Frame(self.root, bg=BG)
        control_frame.pack(pady=14)

        tk.Button(
            control_frame,
            text="重新开始",
            font=("Microsoft YaHei UI", 11),
            width=10,
            bg="#5C7A4A",
            fg="white",
            activebackground="#6E8F58",
            activeforeground="white",
            relief=tk.FLAT,
            bd=0,
            padx=8,
            pady=4,
            command=self.restart_game,
        ).grid(row=0, column=0, padx=10)

        tk.Button(
            control_frame,
            text="退出",
            font=("Microsoft YaHei UI", 11),
            width=10,
            bg="#8B5A4A",
            fg="white",
            activebackground="#A06B58",
            activeforeground="white",
            relief=tk.FLAT,
            bd=0,
            padx=8,
            pady=4,
            command=self.root.quit,
        ).grid(row=0, column=1, padx=10)

    # ------------------------------------------------------------------
    # 绘制
    # ------------------------------------------------------------------

    def board_origin(self):
        return self.border + self.pad, self.border + self.pad

    def cell_center(self, row, col):
        ox, oy = self.board_origin()
        return ox + col * self.cell + self.cell / 2, oy + row * self.cell + self.cell / 2

    def draw_board(self, anim_piece=None):
        """anim_piece: (row_frac, col, player) 用于下落动画。"""
        self.canvas.delete("all")
        w = int(self.canvas["width"])
        h = int(self.canvas["height"])

        self.canvas.create_rectangle(
            2, 2, w - 2, h - 2,
            fill=BOARD_BORDER, outline=BOARD_BORDER, width=0,
        )
        inner = self.border
        self.canvas.create_rectangle(
            inner, inner, w - inner, h - inner,
            fill=BOARD_WOOD, outline=GRID_LINE, width=1,
        )

        ox, oy = self.board_origin()
        for i in range(self.rows + 1):
            y = oy + i * self.cell
            self.canvas.create_line(
                ox, y, ox + self.cols * self.cell, y,
                fill=GRID_LINE, width=2,
            )
        for i in range(self.cols + 1):
            x = ox + i * self.cell
            self.canvas.create_line(
                x, oy, x, oy + self.rows * self.cell,
                fill=GRID_LINE, width=2,
            )

        if (
            self.hover_col is not None
            and not self.game_over
            and not self.dropping
            and not self.is_column_full(self.hover_col)
        ):
            x0 = ox + self.hover_col * self.cell
            self.canvas.create_rectangle(
                x0 + 2, oy + 2,
                x0 + self.cell - 2, oy + self.rows * self.cell - 2,
                outline=PREVIEW, width=2,
            )

        for r in range(self.rows):
            for c in range(self.cols):
                if self.board[r][c] == ' ':
                    self.draw_hole(r, c)
                else:
                    self.draw_disc(r, c, self.board[r][c])

        if anim_piece is not None:
            row_frac, col, player = anim_piece
            self.draw_disc_at(row_frac, col, player)

    def disc_bbox(self, cx, cy):
        m = self.cell * 0.32
        return cx - m, cy - m, cx + m, cy + m

    def draw_hole(self, row, col):
        cx, cy = self.cell_center(row, col)
        x0, y0, x1, y1 = self.disc_bbox(cx, cy)
        self.canvas.create_oval(x0, y0, x1, y1, fill=HOLE, outline=GRID_LINE, width=1)

    def draw_disc(self, row, col, player):
        cx, cy = self.cell_center(row, col)
        self.draw_disc_xy(cx, cy, player)

    def draw_disc_at(self, row_frac, col, player):
        ox, oy = self.board_origin()
        cx = ox + col * self.cell + self.cell / 2
        cy = oy + row_frac * self.cell + self.cell / 2
        self.draw_disc_xy(cx, cy, player)

    def draw_disc_xy(self, cx, cy, player):
        color = MARK_X if player == 'X' else MARK_O
        x0, y0, x1, y1 = self.disc_bbox(cx, cy)
        self.canvas.create_oval(x0, y0, x1, y1, fill=color, outline=GRID_LINE, width=2)
        # 高光，便于区分两色圆片
        hl = self.cell * 0.08
        self.canvas.create_oval(
            cx - self.cell * 0.16, cy - self.cell * 0.18,
            cx - self.cell * 0.16 + hl * 2, cy - self.cell * 0.18 + hl * 2,
            fill="#F2E8D8", outline="",
        )

    # ------------------------------------------------------------------
    # 交互
    # ------------------------------------------------------------------

    def pixel_to_col(self, x, y):
        ox, oy = self.board_origin()
        if x < ox or y < oy:
            return None
        col = int((x - ox) // self.cell)
        row = int((y - oy) // self.cell)
        if 0 <= row < self.rows and 0 <= col < self.cols:
            return col
        return None

    def on_canvas_motion(self, event):
        col = self.pixel_to_col(event.x, event.y)
        if col != self.hover_col:
            self.hover_col = col
            if not self.dropping:
                self.draw_board()

    def on_canvas_leave(self, _event):
        if self.hover_col is not None:
            self.hover_col = None
            if not self.dropping:
                self.draw_board()

    def on_canvas_click(self, event):
        if self.game_over or self.dropping:
            return
        col = self.pixel_to_col(event.x, event.y)
        if col is None:
            return
        self.on_click(col)

    def is_column_full(self, col):
        return self.board[0][col] != ' '

    def drop_row_in_column(self, col):
        for row in range(self.rows - 1, -1, -1):
            if self.board[row][col] == ' ':
                return row
        return None

    def on_click(self, col):
        if self.game_over or self.dropping:
            return

        if self.is_column_full(col):
            messagebox.showwarning("提示", f"第 {col} 列已满，请选择其他列！")
            return

        land_row = self.drop_row_in_column(col)
        player = self.current_player
        self.dropping = True
        self.animate_drop(0.0, land_row, col, player)

    def animate_drop(self, row_frac, land_row, col, player):
        if row_frac >= land_row:
            self.board[land_row][col] = player
            self.moves_count += 1
            self.last_move = (land_row, col)
            self.dropping = False
            self.draw_board()
            self.after_drop()
            return

        self.draw_board(anim_piece=(row_frac, col, player))
        next_frac = min(land_row, row_frac + 0.35)
        self.root.after(16, lambda: self.animate_drop(next_frac, land_row, col, player))

    def after_drop(self):
        if self.check_winner():
            self.game_over = True
            self.info_label.config(text=f"玩家 {self.current_player} 获胜！", fg="#B8860B")
            messagebox.showinfo("游戏结束", f"玩家 {self.current_player} 获胜！")
            return

        if self.is_board_full():
            self.game_over = True
            self.info_label.config(text="平局！", fg="#B8860B")
            messagebox.showinfo("游戏结束", "平局！棋盘已满！")
            return

        self.current_player = 'O' if self.current_player == 'X' else 'X'
        self.info_label.config(text=f"当前玩家: {self.current_player}", fg=INFO_FG)
        self.moves_label.config(text=f"已落子: {self.moves_count}/{self.max_moves}")

    # ------------------------------------------------------------------
    # 胜负判定（与控制台版相同思路）
    # ------------------------------------------------------------------

    def count_consecutive(self, row, col, dr, dc):
        player = self.board[row][col]
        count = 1
        r, c = row + dr, col + dc
        while 0 <= r < self.rows and 0 <= c < self.cols and self.board[r][c] == player:
            count += 1
            r += dr
            c += dc
        return count

    def check_line_in_direction(self, row, col, dr, dc):
        count = self.count_consecutive(row, col, dr, dc)
        count += self.count_consecutive(row, col, -dr, -dc) - 1
        return count >= self.win_length

    def check_winner(self):
        if self.last_move is None:
            return False
        row, col = self.last_move
        for dr, dc in self.DIRECTIONS:
            if self.check_line_in_direction(row, col, dr, dc):
                return True
        return False

    def is_board_full(self):
        return self.moves_count >= self.max_moves

    def restart_game(self):
        self.board = [[' ' for _ in range(self.cols)] for _ in range(self.rows)]
        self.current_player = 'X'
        self.moves_count = 0
        self.game_over = False
        self.last_move = None
        self.dropping = False
        self.hover_col = None
        self.draw_board()
        self.info_label.config(text="当前玩家: X", fg=INFO_FG)
        self.moves_label.config(text=f"已落子: {self.moves_count}/{self.max_moves}")

    def run(self):
        self.root.mainloop()


def main():
    app = ConnectFourGUI(rows=6, cols=7, win_length=4)
    app.run()


if __name__ == "__main__":
    main()
