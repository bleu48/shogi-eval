
import random
import cshogi

board = cshogi.Board()

def position(sfen, usi_moves):
    if sfen == 'startpos':
        board.reset()
    elif sfen[:5] == 'sfen ':
        board.set_sfen(sfen[5:])
    for usi_move in usi_moves:
        board.push_usi(usi_move)

def go():
    if board.is_game_over():
        return 'resign'
    if board.is_nyugyoku():
        return 'win'
    legal_moves = list(board.legal_moves)
    # move = np.random.choice(legal_moves)
    move = random.choice(legal_moves)
    return cshogi.move_to_usi(move)

while True:
    cmd = input().split(' ', 1)
    if cmd[0] == 'usi':
        print('id name this is a sample')
        print('usiok', flush=True)
    elif cmd[0] == 'isready':
        print('readyok', flush=True)
    elif cmd[0] == 'position':
        pos = cmd[1].split('moves')
        position(pos[0].strip(), pos[1].split() if len(pos) > 1 else [])
    elif cmd[0] == 'go':
        print('bestmove ' + go(), flush=True)
    elif cmd[0] == 'stop':
        print('bestmove resign' , flush=True)
    elif cmd[0] == 'quit':
        break
