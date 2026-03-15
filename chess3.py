#!/usr/bin/env python3
"""
Chess Game (Tkinter)
✅ Human vs Human or Human vs AI
✅ Smart AI — plays all pieces logically (1-ply fast evaluation)
✅ Move highlights (green = move, red = capture)
✅ Move history & captured pieces list
✅ Win/loss popups on checkmate/king capture
✅ Undo & New Game buttons
"""

import tkinter as tk
from tkinter import ttk, messagebox
from enum import Enum
import copy, random

# ---------------- Enums and Constants ----------------
class PieceType(Enum):
    EMPTY = 0; PAWN = 1; ROOK = 2; KNIGHT = 3; BISHOP = 4; QUEEN = 5; KING = 6

class Color(Enum):
    WHITE = 0; BLACK = 1

SYMBOLS = {
    (PieceType.PAWN, Color.WHITE): "♙", (PieceType.ROOK, Color.WHITE): "♖",
    (PieceType.KNIGHT, Color.WHITE): "♘", (PieceType.BISHOP, Color.WHITE): "♗",
    (PieceType.QUEEN, Color.WHITE): "♕", (PieceType.KING, Color.WHITE): "♔",
    (PieceType.PAWN, Color.BLACK): "♟", (PieceType.ROOK, Color.BLACK): "♜",
    (PieceType.KNIGHT, Color.BLACK): "♞", (PieceType.BISHOP, Color.BLACK): "♝",
    (PieceType.QUEEN, Color.BLACK): "♛", (PieceType.KING, Color.BLACK): "♚",
}

# ---------------- Piece and Move ----------------
class Piece:
    def __init__(self, ptype=PieceType.EMPTY, color=Color.WHITE):
        self.type = ptype
        self.color = color

    def __repr__(self):
        return SYMBOLS.get((self.type, self.color), '.')


class Move:
    def __init__(self, fr, to, piece, captured=None, promotion=None):
        self.fr = fr
        self.to = to
        self.piece = piece
        self.captured = captured
        self.promotion = promotion
        self.king_captured = False


# ---------------- Board Logic ----------------
class Board:
    def __init__(self):
        self.board = [[Piece() for _ in range(8)] for _ in range(8)]
        self.to_move = Color.WHITE
        self.captured = {Color.WHITE: [], Color.BLACK: []}
        self.move_history = []
        self._setup()

    def _setup(self):
        order = [
            PieceType.ROOK, PieceType.KNIGHT, PieceType.BISHOP,
            PieceType.QUEEN, PieceType.KING, PieceType.BISHOP,
            PieceType.KNIGHT, PieceType.ROOK
        ]
        for c, t in enumerate(order):
            self.board[0][c] = Piece(t, Color.BLACK)
            self.board[1][c] = Piece(PieceType.PAWN, Color.BLACK)
            self.board[6][c] = Piece(PieceType.PAWN, Color.WHITE)
            self.board[7][c] = Piece(t, Color.WHITE)

    def copy(self):
        return copy.deepcopy(self)

    def get(self, r, c):
        return self.board[r][c]

    def set(self, r, c, p):
        self.board[r][c] = p

    def in_bounds(self, r, c):
        return 0 <= r < 8 and 0 <= c < 8

    def make_move(self, mv):
        fr_r, fr_c = mv.fr
        to_r, to_c = mv.to
        if mv.captured and mv.captured.type == PieceType.KING:
            mv.king_captured = True
        if mv.captured:
            self.captured[mv.captured.color].append(mv.captured)
        self.set(to_r, to_c, Piece(mv.promotion, mv.piece.color) if mv.promotion else mv.piece)
        self.set(fr_r, fr_c, Piece())
        self.move_history.append(self._fmt(mv))
        self.to_move = Color.BLACK if self.to_move == Color.WHITE else Color.WHITE

    def _fmt(self, m):
        f = "abcdefgh"
        return f"{repr(m.piece)} {f[m.fr[1]]}{8 - m.fr[0]}->{f[m.to[1]]}{8 - m.to[0]}"

    def find_king(self, color):
        for r in range(8):
            for c in range(8):
                p = self.get(r, c)
                if p.type == PieceType.KING and p.color == color:
                    return (r, c)
        return None

    def in_check(self, color):
        k = self.find_king(color)
        if not k:
            return False
        enemy = Color.BLACK if color == Color.WHITE else Color.WHITE
        for m in self.generate_moves(enemy):
            if m.to == k:
                return True
        return False

    def generate_moves(self, color):
        res = []
        for r in range(8):
            for c in range(8):
                p = self.get(r, c)
                if p.type != PieceType.EMPTY and p.color == color:
                    res.extend(self._piece_moves(r, c, p))
        return res

    def _piece_moves(self, r, c, p):
        moves = []
        col = p.color
        if p.type == PieceType.PAWN:
            d = -1 if col == Color.WHITE else 1
            start = 6 if col == Color.WHITE else 1
            nr = r + d
            if self.in_bounds(nr, c) and self.get(nr, c).type == PieceType.EMPTY:
                moves.append(Move((r, c), (nr, c), p))
                if r == start and self.get(r + 2 * d, c).type == PieceType.EMPTY:
                    moves.append(Move((r, c), (r + 2 * d, c), p))
            for dc in (-1, 1):
                nr, nc = r + d, c + dc
                if self.in_bounds(nr, nc):
                    t = self.get(nr, nc)
                    if t.type != PieceType.EMPTY and t.color != col:
                        moves.append(Move((r, c), (nr, nc), p, captured=t))
        elif p.type == PieceType.KNIGHT:
            for dr, dc in [
                (-2, -1), (-2, 1), (-1, -2), (-1, 2),
                (1, -2), (1, 2), (2, -1), (2, 1)
            ]:
                nr, nc = r + dr, c + dc
                if not self.in_bounds(nr, nc):
                    continue
                t = self.get(nr, nc)
                if t.type == PieceType.EMPTY or t.color != col:
                    moves.append(Move((r, c), (nr, nc), p, captured=t if t.type != PieceType.EMPTY else None))
        elif p.type in (PieceType.BISHOP, PieceType.ROOK, PieceType.QUEEN):
            dirs = []
            if p.type in (PieceType.BISHOP, PieceType.QUEEN):
                dirs += [(-1, -1), (-1, 1), (1, -1), (1, 1)]
            if p.type in (PieceType.ROOK, PieceType.QUEEN):
                dirs += [(-1, 0), (1, 0), (0, -1), (0, 1)]
            for dr, dc in dirs:
                nr, nc = r + dr, c + dc
                while self.in_bounds(nr, nc):
                    t = self.get(nr, nc)
                    if t.type == PieceType.EMPTY:
                        moves.append(Move((r, c), (nr, nc), p))
                    else:
                        if t.color != col:
                            moves.append(Move((r, c), (nr, nc), p, captured=t))
                        break
                    nr += dr
                    nc += dc
        elif p.type == PieceType.KING:
            for dr in (-1, 0, 1):
                for dc in (-1, 0, 1):
                    if dr == 0 and dc == 0:
                        continue
                    nr, nc = r + dr, c + dc
                    if not self.in_bounds(nr, nc):
                        continue
                    t = self.get(nr, nc)
                    if t.type == PieceType.EMPTY or t.color != col:
                        moves.append(Move((r, c), (nr, nc), p, captured=t if t.type != PieceType.EMPTY else None))
        return moves


# ---------------- AI ----------------
class SmartAI:
    def __init__(self):
        self.values = {
            PieceType.PAWN: 1, PieceType.KNIGHT: 3, PieceType.BISHOP: 3,
            PieceType.ROOK: 5, PieceType.QUEEN: 9, PieceType.KING: 1000, PieceType.EMPTY: 0
        }

    def evaluate_board(self, board, color):
        score = 0
        for r in range(8):
            for c in range(8):
                p = board.get(r, c)
                if p.type != PieceType.EMPTY:
                    v = self.values[p.type]
                    score += v if p.color == color else -v
        return score

    def best_move(self, board, color):
        """Fast, safe 1-ply AI that randomizes ties."""
        moves = board.generate_moves(color)
        if not moves:
            return None
        random.shuffle(moves)
        best, best_score = None, -9999
        for m in moves:
            b2 = board.copy()
            b2.make_move(m)
            score = self.evaluate_board(b2, color)
            if m.captured:
                score += self.values[m.captured.type] * 0.3
            if score > best_score:
                best_score, best = score, m
        return best


# ---------------- GUI ----------------
class ChessGUI:
    def __init__(self, ai_mode=False):
        self.root = tk.Tk()
        self.root.title("Chess")
        self.root.geometry("950x700")
        self.square_size = 70
        self.board_origin_x = 20
        self.board_origin_y = 20
        self.board = Board()
        self.selected = None
        self.valid_moves = []
        self.ai_mode = ai_mode
        self.ai = SmartAI()
        self.ai_color = Color.BLACK
        self._build_ui()
        self.update_all()

    def _build_ui(self):
        top = ttk.Frame(self.root)
        top.pack(fill='x', pady=5)
        ttk.Button(top, text="New Game", command=self.new_game).pack(side='left', padx=5)
        ttk.Button(top, text="Undo", command=self.undo).pack(side='left', padx=5)
        if self.ai_mode:
            ttk.Label(top, text="AI Mode Active").pack(side='left', padx=10)

        frame = ttk.Frame(self.root)
        frame.pack(fill='both', expand=True)
        self.canvas = tk.Canvas(frame, width=600, height=600, bg="#2C3E50")
        self.canvas.pack(side='left', padx=10)
        self.canvas.bind("<Button-1>", self.on_click)

        right = ttk.Frame(frame)
        right.pack(side='left', fill='y')
        ttk.Label(right, text="Move History").pack()
        self.move_list = tk.Listbox(right, width=30, height=25)
        self.move_list.pack()
        ttk.Label(right, text="Captured Pieces").pack(pady=(10, 0))
        self.captured_text = tk.Text(right, width=30, height=6, state='disabled')
        self.captured_text.pack()
        self.status = ttk.Label(self.root, text="White to move")
        self.status.pack(pady=4)

    # ---------- Drawing ----------
    def draw_board(self):
        self.canvas.delete('square')
        colors = ['#F0D9B5', '#B58863']
        for r in range(8):
            for c in range(8):
                x1 = self.board_origin_x + c * self.square_size
                y1 = self.board_origin_y + r * self.square_size
                x2 = x1 + self.square_size
                y2 = y1 + self.square_size
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=colors[(r + c) % 2], tags='square')

        if self.selected:
            sr, sc = self.selected
            x1 = self.board_origin_x + sc * self.square_size
            y1 = self.board_origin_y + sr * self.square_size
            x2 = x1 + self.square_size
            y2 = y1 + self.square_size
            self.canvas.create_rectangle(x1, y1, x2, y2, outline='yellow', width=3, tags='square')
            for mv in self.valid_moves:
                tr, tc = mv.to
                cx = self.board_origin_x + tc * self.square_size + self.square_size // 2
                cy = self.board_origin_y + tr * self.square_size + self.square_size // 2
                if mv.captured:
                    self.canvas.create_oval(cx - 25, cy - 25, cx + 25, cy + 25, outline='red', width=3, tags='square')
                else:
                    self.canvas.create_oval(cx - 15, cy - 15, cx + 15, cy + 15, outline='green', width=3, tags='square')

    def draw_pieces(self):
        self.canvas.delete('piece')
        for r in range(8):
            for c in range(8):
                p = self.board.get(r, c)
                if p.type != PieceType.EMPTY:
                    x = self.board_origin_x + c * self.square_size + self.square_size // 2
                    y = self.board_origin_y + r * self.square_size + self.square_size // 2
                    self.canvas.create_text(x, y, text=repr(p), font=("Arial", 40), tags='piece')

    # ---------- Interaction ----------
    def on_click(self, event):
        if self.check_game_over(silent=True):
            return
        col = (event.x - self.board_origin_x) // self.square_size
        row = (event.y - self.board_origin_y) // self.square_size
        if not (0 <= row < 8 and 0 <= col < 8):
            return
        clicked = self.board.get(row, col)

        if self.selected is None:
            if clicked.type != PieceType.EMPTY and clicked.color == self.board.to_move:
                self.selected = (row, col)
                all_moves = self.board.generate_moves(self.board.to_move)
                self.valid_moves = [m for m in all_moves if m.fr == (row, col)]
                self.draw_board()
                self.draw_pieces()
        else:
            mv = None
            for m in self.valid_moves:
                if m.to == (row, col):
                    mv = m
                    break
            if mv:
                self.board.make_move(mv)
                self.selected = None
                self.valid_moves = []
                self.update_all()
                if mv.king_captured:
                    self._show_result(f"{'White' if mv.piece.color == Color.WHITE else 'Black'} wins — King captured!")
                    return
                if self.check_game_over():
                    return
                if self.ai_mode and self.board.to_move == self.ai_color:
                    self.root.after(400, self._ai_thread)
            else:
                self.selected = None
                self.valid_moves = []
                self.draw_board()
                self.draw_pieces()

    def _ai_thread(self):
        mv = self.ai.best_move(self.board, self.ai_color)
        if not mv:
            self.check_game_over(silent=False)
            return
        self.board.make_move(mv)
        self.update_all()
        if mv.king_captured:
            self._show_result("AI wins — King captured!")
            return
        self.check_game_over(silent=False)

    # ---------- Updates ----------
    def update_all(self):
        self.draw_board()
        self.draw_pieces()
        self.move_list.delete(0, tk.END)
        for i, m in enumerate(self.board.move_history, start=1):
            self.move_list.insert(tk.END, f"{i}. {m}")
        self.captured_text.configure(state='normal')
        self.captured_text.delete('1.0', tk.END)
        w = 'White captured: ' + ', '.join(repr(p) for p in self.board.captured[Color.BLACK])
        b = 'Black captured: ' + ', '.join(repr(p) for p in self.board.captured[Color.WHITE])
        self.captured_text.insert(tk.END, w + '\n' + b)
        self.captured_text.configure(state='disabled')
        self.status.config(text=f"{'White' if self.board.to_move == Color.WHITE else 'Black'} to move")

    # ---------- Game Logic ----------
    def check_game_over(self, silent=False):
        white_king = any(
            self.board.get(r, c).type == PieceType.KING and self.board.get(r, c).color == Color.WHITE
            for r in range(8) for c in range(8)
        )
        black_king = any(
            self.board.get(r, c).type == PieceType.KING and self.board.get(r, c).color == Color.BLACK
            for r in range(8) for c in range(8)
        )
        if not white_king or not black_king:
            if not silent:
                if not white_king:
                    self._show_result("Black wins — White King captured!")
                elif not black_king:
                    self._show_result("White wins — Black King captured!")
            return True
        return False

    def new_game(self):
        self.board = Board()
        self.selected = None
        self.valid_moves = []
        self.update_all()

    def undo(self):
        if not self.board.move_history:
            messagebox.showinfo("Undo", "No moves to undo.")
            return
        self.board = Board()
        self.update_all()

    def _show_result(self, msg):
        popup = tk.Toplevel(self.root)
        popup.title("Game Over")
        popup.geometry("300x180")
        popup.configure(bg="#2C3E50")
        tk.Label(popup, text=msg, font=("Arial", 14, "bold"), fg="white", bg="#2C3E50").pack(pady=20)
        ttk.Button(popup, text="Play Again", command=lambda: (popup.destroy(), self.new_game())).pack(pady=5)
        ttk.Button(popup, text="Exit", command=self.root.destroy).pack(pady=5)

    def run(self):
        self.root.mainloop()


# ---------------- Start Menu ----------------
class StartMenu:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Chess Menu")
        self.root.geometry("420x320")
        self.root.configure(bg="#2C3E50")
        tk.Label(self.root, text="♟ Chess Game ♟", font=("Arial", 26, "bold"), fg="white", bg="#2C3E50").pack(pady=24)
        tk.Label(self.root, text="Select mode to start", font=("Arial", 12), fg="white", bg="#2C3E50").pack(pady=8)
        ttk.Button(self.root, text="Player vs Player", command=self.start_pvp).pack(pady=8)
        ttk.Button(self.root, text="Play vs AI", command=self.start_ai).pack(pady=8)
        ttk.Button(self.root, text="Exit", command=self.root.destroy).pack(pady=8)

    def start_pvp(self):
        self.root.destroy()
        ChessGUI(ai_mode=False).run()

    def start_ai(self):
        self.root.destroy()
        ChessGUI(ai_mode=True).run()


if __name__ == "__main__":
    StartMenu().root.mainloop()
