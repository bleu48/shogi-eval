# 電竜戦 1file match用サンプル４ ©2023 Seiji SHIBA
# NNUE型評価関数とネガアルファ法固定深さ探索の実装例
# import numpy as np
from numpy import array, append
# import cshogi
from cshogi import Board, move_to_usi, BKING, WKING, COLORS, HAND_PIECES, BLACK
# import struct
from struct import unpack_from
from time import time

nn_data = open("eval/nn.bin", "rb").read()
i = 178 # NNUE型の評価関数の特徴表示文字列長（デフォルト値）
bias1 =  array( unpack_from("<"+str(256)+"h", nn_data, 16+i) )
weight1 = array( unpack_from("<"+str(256*125388)+"h", nn_data, 16+i+256*2) ).reshape(125388,256)
bias2 =  array( unpack_from("<"+str(32)+"i", nn_data, 16+i+2*(256+256*125388)+4) )
weight2 = array( unpack_from("<"+str(512*32)+"b", nn_data, 16+i+2*(256+256*125388)+4 + 4*32) ).reshape(32,512)
bias3 =  array( unpack_from("<"+str(32)+"i", nn_data, 16+i+2*(256+256*125388)+4+ 4*32+32*512) )
weight3 = array( unpack_from("<"+str(32*32)+"b", nn_data, 16+i+2*(256+256*125388)+4+ 4*32+32*512 + 4*32) ).reshape(32,32)
bias4 = unpack_from("<"+str(1)+"i", nn_data, 16+i+2*(256+256*125388)+4+ 4*32+32*512 + 4*32+32*32)[0]
weight4 = array( unpack_from("<"+str(32*1)+"b", nn_data, 16+i+2*(256+256*125388)+4+ 4*32+32*512 + 4*32+32*32 + 4*1) )

BonaPiece_c=[1, 90, 252, 414, 576, 900, 1224, 738, 0, 738, 738, 738, 738, 1062, 1386, 0, 0, 171, 333, 495, 657, 981, 1305, 819, 0, 819, 819, 819, 819, 1143, 1467, 0, 0]
BonaPiece_h=[[1, 39, 49, 59, 69, 79, 85], [20, 44, 54, 64, 74, 82, 88]] # NNUEのPベクトル計算用のテーブル

def fv40(board): # KおよびPの特徴ベクトル
    pindex, qindex = [], []
    bp = board.pieces
    k0 = next(square for square, piece in enumerate(bp) if piece == BKING) # 先手玉はひとつしかないのでこれで十分
    k1 = next(square for square, piece in enumerate(bp) if piece == WKING)
    bp[k0] = 0; bp[k1] = 0
    for square, piece in enumerate(bp):
        if piece > 0:
            pindex.append(BonaPiece_c[piece] + square) # NNUEにおけるPベクトル
            qindex.append(BonaPiece_c[piece ^ 16] + 80-square) # 盤面を回したときのPベクトル

    pieces_in_hand = board.pieces_in_hand
    for color in COLORS:
        for piece in HAND_PIECES:
            if (piece_count := pieces_in_hand[color][piece]):
                index = BonaPiece_h[color][piece] # NNUEにおけるPベクトル
                index2 = BonaPiece_h[color ^ 1][piece] # 盤面を回したときのPベクトル
                for i in range(piece_count):
                    pindex.append(index + i)
                    qindex.append(index2 + i)

    if board.turn == BLACK:
        return k0, 80-k1, pindex, qindex # 先手番視点
    else:
        return 80-k1, k0, qindex, pindex # 後手番視点

def eval(board): # NNUE型の評価関数（キャッシュや差分更新など無し）
    k0, k1, fv38, fv38q = fv40(board) # 特徴ベクトルの取得
    x = bias1.copy() # 手番側特徴
    for j in fv38:
        x += weight1[k0*1548 + j] # 手番側一層目
    x2 = bias1.copy() # 相手番特徴
    for j in fv38q:
        x2 += weight1[k1*1548 + j] # 相手番一層目
    x = append(x,x2).clip(0,127) # 結合してクリップ（Clipped ReLU）
    x = ((bias2 + weight2.dot(x)) // 64).clip(0, 127) #二層目
    x = ((bias3 + weight3.dot(x)) // 64).clip(0, 127) #三層目
    x = bias4 + weight4.dot(x) #四層目
    return (x // 16)

MIN_VALUE = -32000
MAX_VALUE = 32000
SEARCH_DEPTH = 4

# 参考：ネガアルファ法 http://www.nct9.ne.jp/m_hiroi/light/pyalgo25.html
def negaalpha(depth, board, alpha, beta):
    global nodes, start
    if board.is_game_over(): # 負け局面は即リターン
        return -30000, "resign"
    if board.is_nyugyoku(): # 勝ち局面も即リターン
        return 30000, "win"
    if m := board.mate_move(3): # 三手詰みも即リターン
        return 30000, move_to_usi(m)
    if depth <= 0: # 残り探索深さがなくなれば評価値を返す
        # global nodes
        nodes += 1 # 評価した局面数をカウント
        v = eval(board)
        return v, ""
    #
    value = alpha # MIN_VALUEでもいいんだけど
    move = 0 # 以下のループが全部すり抜けたとき用の初期化
    pvm = ""
    legal_moves = list(board.legal_moves) # いわゆる合法手リスト
    legal_moves = sorted(legal_moves, reverse=True, key=lambda x:x & 0b111100000100001110000000) # 取る駒，成るフラグ，打ち駒の部分をフィルタして逆ソート
    for m in legal_moves:
        board.push(m)
        if draw := board.is_draw():
            v = [0,0,-28000,28000,-28000,28000][draw]
            pv = ["","rep_draw","rep_win","rep_lose","rep_sup","rep_inf"][draw]
        else:
            v, pv = negaalpha(depth - 1, board, -beta, -value) # depthを一つ減らしてαβを符号を変えて入れ替えるのがミソ
            v = -v
        board.pop() # 将棋はループ用に手戻しするが，ゲームによっては盤面コピーして毎回捨てるほうが速い場合も
        if value < v: # ネガマックス法 : 大きな値を選ぶ
            value = v
            move = m
            pvm = pv
            if depth == SEARCH_DEPTH:
                lap_time = time() - start + 1e-6
                print('info nps {} time {} nodes {} score cp {} pv {}'.format(
                    int(nodes / lap_time), int(lap_time * 1000), nodes, value, move_to_usi(move)+" "+pvm), flush=True)
        if value >= beta: break # ネガアルファ法 : 規定値外があれば打ち切る
    return value, move_to_usi(move)+" "+pvm

board = Board()

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
            print('info score mate 1 pv {}'.format(m:=move_to_usi(matemove)))
            return m
    global nodes, start
    nodes, start = 0, time()
    value, move = negaalpha(SEARCH_DEPTH, board, MIN_VALUE, MAX_VALUE)
    lap_time = time() - start + 1.0e-6 # ０除算エラー対策で微小値を足してある
    print("info time", int(lap_time * 1000), "depth", SEARCH_DEPTH, "nodes", nodes, "nps", int(nodes / lap_time), "score cp", int(value), "pv", move)
    return move.split()[0]

while True:
    cmd = input().split(' ', 1)
    if cmd[0] == 'usi':
        print('id name this is sample4-5a')
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
