
import numpy as np
import cshogi
import random

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
    if not board.is_check():
        if (matemove:=board.mate_move_in_1ply()):
            print('info score mate 1 pv {}'.format(cshogi.move_to_usi(matemove)))
            return cshogi.move_to_usi(matemove)
    legal_moves = list(board.legal_moves)
    random.shuffle(legal_moves)
    move = max(legal_moves, key=lambda x:x & 0b111100000100000000000000) # 取る駒，成るフラグ，打ち駒の部分をフィルタして最大値を取る
    return cshogi.move_to_usi(move)

while True:
    cmd = input().split(' ', 1)
    if cmd[0] == 'usi':
        print('id name this is sample1-1')
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
