import importlib.util
import os
import tempfile
import unittest
from pathlib import Path
os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
spec = importlib.util.spec_from_file_location("game", Path(__file__).resolve().parents[1] / "Tetris-New.py")
game = importlib.util.module_from_spec(spec)
spec.loader.exec_module(game)

class GameTests(unittest.TestCase):
    def test_seven_bag(self):
        gen = game.PieceGenerator()
        for _ in range(2):
            self.assertEqual({gen.next_piece().shape_id for _ in range(7)}, set(range(7)))

    def test_rotation(self):
        p = game.Piece(0)
        self.assertEqual(p.rotated_shape(), [[1], [1], [1], [1]])

    def test_board_boundary(self):
        board = game.Board()
        p = game.Piece(0)
        self.assertTrue(board.valid(p))
        p.x = -1
        self.assertFalse(board.valid(p))

    def test_lock(self):
        board = game.Board()
        p = game.Piece(3)
        self.assertTrue(board.lock(p))
        self.assertEqual(sum(cell is not None for row in board.grid for cell in row), 4)
        self.assertFalse(board.valid(p))

    def test_clear_lines(self):
        board = game.Board()
        board.grid[-1] = [game.COLORS[0]] * game.COLS
        self.assertEqual(board.clear_lines(), 1)
        self.assertEqual(len(board.grid), game.ROWS)
        self.assertTrue(all(cell is None for row in board.grid for cell in row))

    def test_records(self):
        original = game.SAVE_FILE
        self.addCleanup(setattr, game, "SAVE_FILE", original)
        with tempfile.TemporaryDirectory() as tmp:
            game.SAVE_FILE = Path(tmp) / "records.json"
            self.assertEqual(game.load_record(), 0)
            self.assertTrue(game.save_record(123))
            self.assertEqual(game.load_record(), 123)
            game.SAVE_FILE.write_text("invalid")
            self.assertEqual(game.load_record(), 0)
