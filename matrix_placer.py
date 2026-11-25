"""
四子棋（Connect Four）— 控制台版

规则：
- 6 行 × 7 列棋盘
- 玩家 X 先手，双方轮流选择一列落子
- 棋子受重力影响，落到该列最低的空位
- 任一横、竖、斜连成 4 子即胜
- 棋盘填满仍无人获胜则为平局
"""


class ConnectFour:
    """四子棋核心逻辑：纵向重力落子 + 连四判定。"""

    # 四个检测方向：横、竖、主对角、副对角
    DIRECTIONS = [(0, 1), (1, 0), (1, 1), (1, -1)]

    def __init__(self, rows=6, cols=7, win_length=4):
        self.rows = rows
        self.cols = cols
        self.win_length = win_length
        self.board = [[' ' for _ in range(cols)] for _ in range(rows)]
        self.current_player = 'X'
        self.moves_count = 0
        self.max_moves = rows * cols
        self.last_move = None

    # ------------------------------------------------------------------
    # 显示
    # ------------------------------------------------------------------

    def display_board(self):
        print("\n" + "=" * 36)
        print("     四子棋（Connect Four）")
        print("=" * 36)

        print("     " + "   ".join(str(i) for i in range(self.cols)))
        print("   +" + "---+" * self.cols)

        for i, row in enumerate(self.board):
            cells = " | ".join(cell if cell != ' ' else '.' for cell in row)
            print(f" {i} | {cells} |")
            print("   +" + "---+" * self.cols)

        print(f"\n当前玩家: {self.current_player}")
        print(f"已落子数: {self.moves_count}/{self.max_moves}")
        print("输入列号即可落子（棋子会落到该列最低空位）")
        print()

    # ------------------------------------------------------------------
    # 输入与落子
    # ------------------------------------------------------------------

    def is_valid_input(self, coord_str):
        """解析列号，返回 (ok, 列号或错误信息)。"""
        if not coord_str or not coord_str.strip():
            return False, "输入不能为空"

        parts = coord_str.replace(',', ' ').split()
        if len(parts) != 1:
            return False, f"请输入一个列号（0-{self.cols - 1}）"

        try:
            col = int(parts[0])
        except ValueError:
            return False, "请输入有效的数字"

        if not (0 <= col < self.cols):
            return False, f"列号超出范围，请输入 0-{self.cols - 1} 之间的数字"

        return True, col

    def is_column_full(self, col):
        return self.board[0][col] != ' '

    def drop_row_in_column(self, col):
        """返回该列重力下落后的行号；列满则返回 None。"""
        for row in range(self.rows - 1, -1, -1):
            if self.board[row][col] == ' ':
                return row
        return None

    def place_piece(self, row, col):
        self.board[row][col] = self.current_player
        self.moves_count += 1
        self.last_move = (row, col)

    def switch_player(self):
        self.current_player = 'O' if self.current_player == 'X' else 'X'

    # ------------------------------------------------------------------
    # 胜负判定（以最近一步为中心，向四个方向数连子）
    # ------------------------------------------------------------------

    def count_consecutive(self, row, col, dr, dc):
        """从 (row,col) 沿 (dr,dc) 方向统计连续同色棋子数（含自身）。"""
        player = self.board[row][col]
        count = 1
        r, c = row + dr, col + dc
        while 0 <= r < self.rows and 0 <= c < self.cols and self.board[r][c] == player:
            count += 1
            r += dr
            c += dc
        return count

    def check_line_in_direction(self, row, col, dr, dc):
        """某一方向（正反两侧）的连子是否达到获胜长度。"""
        count = self.count_consecutive(row, col, dr, dc)
        count += self.count_consecutive(row, col, -dr, -dc) - 1  # 自身只算一次
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

    # ------------------------------------------------------------------
    # 游戏主循环
    # ------------------------------------------------------------------

    def play(self):
        print("\n欢迎来到 四子棋（Connect Four）！")
        print(f"棋盘 {self.rows} 行 × {self.cols} 列，连成 {self.win_length} 子获胜")
        print("玩家 X 先行，双方轮流选择一列落子")
        print("棋子会因重力落到该列最低的空位")
        print(f"输入格式：列号（如：3）")
        print("输入 'q' 退出游戏\n")

        while True:
            self.display_board()

            coord_str = input(f"玩家 {self.current_player} 请输入列号: ").strip()

            if coord_str.lower() == 'q':
                print("\n游戏结束，感谢游玩！")
                break

            is_valid, result = self.is_valid_input(coord_str)
            if not is_valid:
                print(f"\n错误: {result}")
                input("按回车继续...")
                continue

            col = result
            if self.is_column_full(col):
                print(f"\n错误: 第 {col} 列已满，请选择其他列")
                input("按回车继续...")
                continue

            row = self.drop_row_in_column(col)
            self.place_piece(row, col)

            if self.check_winner():
                self.display_board()
                print(f"\n🎉 玩家 {self.current_player} 获胜！")
                break

            if self.is_board_full():
                self.display_board()
                print("\n平局！棋盘已满！")
                break

            self.switch_player()


def main():
    game = ConnectFour(rows=6, cols=7, win_length=4)
    game.play()

    while True:
        again = input("\n是否再来一局？(y/n): ").strip().lower()
        if again == 'y':
            game = ConnectFour(rows=6, cols=7, win_length=4)
            game.play()
        elif again == 'n':
            print("感谢游玩，再见！")
            break
        else:
            print("请输入 y 或 n")


if __name__ == "__main__":
    main()
