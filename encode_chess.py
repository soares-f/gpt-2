import chess
import ring


def next_board(b, move):
  b = b.copy()
  b.push(move)
  return b


@ring.lru(maxsize=1000)
def as_board(x):
  if isinstance(x, str):
    epd = x.split(' ', 1)[1]
    return chess.Board(epd)
  assert isinstance(x, chess.Board)
  return x


def diff_board(b1, b2):
  for move in list(b1.legal_moves):
    b1.push(move)
    try:
      if b1.epd() == b2.epd():
        return move.uci()
    finally:
      b1.pop()
  # result = [move for move in b1.legal_moves if next_board(b1, move) == b2]
  # if len(result) > 0:
  #   assert len(result) == 1
  #   move = result[0]
  #   return move.uci()


def annotate_pieces(board):
  annotated = []
  for y, rank in enumerate(str(board).splitlines()):
    for x, piece in enumerate(rank.split()):
      #print(x, piece, y, rank)
      X = 'a b c d e f g h'.split()[x]
      Y = '8 7 6 5 4 3 2 1'.split()[y]
      #yield piece + ' @ ' + X + Y
      annotated.append([X + Y, piece])
  return annotated


def annotate_uci(coords, uci):
  assert len(uci) in [4, 5]
  x0, y0, x1, y1, *promote = uci
  src = x0+y0
  dst = x1+y1
  return [src, coords[src], dst, coords[dst]] + promote


def render_uci(coords, uci):
  return spc(annotate_uci(coords, uci))


def spc(x):
  if isinstance(x, list):
    return ' '.join([spc(y) for y in x])
  return x


def render_board(b, b2=None, show_moves=True):
  assert isinstance(b, str)
  won = b.split(' ', 1)[0]
  if won == '1/2-1/2': won = '1 1'
  elif won == '1-0': won = '1 0'
  elif won == '0-1': won = '0 1'
  else: raise ValueError("Unknown won state: %s" % won)
  board = as_board(b)
  state = board.epd().split(' ', 1)[1]
  side, castling, en_passant, *operations = state.split(' ')
  assert side in ['b', 'w']
  side = '1' if side == 'w' else '0'
  assert len(operations) == 0
  castling += '.' * (4 - len(castling))
  castling = [x for x in castling]
  #pieces = str(board).replace('\n', ' ')
  pieces = annotate_pieces(board)
  coords = dict(pieces)
  if b2 is None:
    raise NotImplementedError()
    #return state + pieces + ' !\n'
  else:
    board2 = as_board(b2)
    #result = [state]
    result = []
    result += [won]
    result += [side]
    result += castling
    result += [en_passant]
    result += ['<']
    result += [spc(pieces)]
    result += ['>']
    if show_moves:
      result += ['? ' + render_uci(coords, uci) for uci in sorted([move.uci() for move in list(board.legal_moves)])]
    result += [':']
    next_move_uci = diff_board(board, board2)
    assert next_move_uci is not None
    result += [render_uci(coords, next_move_uci)]
    return ' '.join(result)
    
vocab = [
    '<|endoftext|>',
    'a1', 'a2', 'a3', 'a4', 'a5', 'a6', 'a7', 'a8',
    'b1', 'b2', 'b3', 'b4', 'b5', 'b6', 'b7', 'b8',
    'c1', 'c2', 'c3', 'c4', 'c5', 'c6', 'c7', 'c8',
    'd1', 'd2', 'd3', 'd4', 'd5', 'd6', 'd7', 'd8',
    'e1', 'e2', 'e3', 'e4', 'e5', 'e6', 'e7', 'e8',
    'f1', 'f2', 'f3', 'f4', 'f5', 'f6', 'f7', 'f8',
    'g1', 'g2', 'g3', 'g4', 'g5', 'g6', 'g7', 'g8',
    'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'h7', 'h8',
    '.', '_',
    'B', 'K', 'N', 'P', 'Q', 'R',
    'b', 'k', 'n', 'p', 'q', 'r',
    '1', '-', '0',
    ':', '?',
    '<', '>',
    ]

encoder = {v: k for k, v in enumerate(vocab)}

def render_game(lines, show_moves=True):
  return [render_board(lines[i], lines[i+1], show_moves=show_moves)
      for i, line in enumerate(lines) if i < len(lines) - 1]

if __name__ == '__main__':
  import sys
  import tflex_utils
  lines = []
  args = sys.argv[1:]
  with open(args[0]) as infile:
    for i, line in tflex_utils.for_each_line(infile):
      if len(lines) > 0 and len(line.strip()) == 0:
        for oline in render_game(lines):
          print(oline)
        print('<|endoftext|>')
        lines = []
      else:
        lines.append(line)
    if len(lines) > 0:
      for oline in render_game(lines):
        print(oline)


