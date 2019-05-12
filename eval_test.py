import numpy as np
import itertools
import shogi

SQUARES_R90=[0]*81
for square in shogi.SQUARES:
    SQUARES_R90[square]=shogi.SQUARES_L90.index(square)

material = [0,90,315,405,495,540,855,990,15000,
    540,540,540,540,945,1395]

def eval_init():
    with open('eval/KK_synthesized.bin', 'rb') as f:
        data = np.fromfile(f, dtype='int32')
    kk_array = data.reshape(81, 81, 2)
    # print(kk_array[44][36] / 32)
    # 44 = ５九玉
    # 36 = ５一玉
    # 35+ 90+ 81 * 8 = ４九金
    # 53+ 90+ 81 * 8 = ６九金

    with open('eval/KKP_synthesized.bin', 'rb') as f:
        data = np.fromfile(f, dtype='int32')
    kkp_array = data.reshape(81, 81, 1548, 2)
    # print(kkp_array[44][36][35+ 90+ 81*8] / 32)
    # print(kkp_array[44][36][53+ 90+ 81*8] / 32)

    with open('eval/KPP_synthesized.bin', 'rb') as f:
        data = np.fromfile(f, dtype='int16')
    kpp_array = data.reshape(81, 1548, 1548, 2)
    # print(kpp_array[44][35+ 90+ 81*8][53+ 90+ 81*8] / 32)
    
    return kk_array, kkp_array, kpp_array

BONA_PIECE_ZERO = 0
BonaPiece=[
    BONA_PIECE_ZERO + 1,#//0//0+1
    20,#//f_hand_pawn + 19,//19+1
    39,#//e_hand_pawn + 19,//38+1
    44,#//f_hand_lance + 5,//43+1
    49,#//e_hand_lance + 5,//48+1
    54,#//f_hand_knight + 5,//53+1
    59,#//e_hand_knight + 5,//58+1
    64,#//f_hand_silver + 5,//63+1
    69,#//e_hand_silver + 5,//68+1
    74,#//f_hand_gold + 5,//73+1
    79,#//e_hand_gold + 5,//78+1
    82,#//f_hand_bishop + 3,//81+1
    85,#//e_hand_bishop + 3,//84+1
    88,#//f_hand_rook + 3,//87+1
    90,#//e_hand_rook + 3,//90
    # f_pawn = fe_hand_end,
    90+81,# e_pawn = f_pawn + 81,
    90+81*2,# f_lance = e_pawn + 81,
    90+81*3,# e_lance = f_lance + 81,
    90+81*4,# f_knight = e_lance + 81,
    90+81*5,# e_knight = f_knight + 81,
    90+81*6,# f_silver = e_knight + 81,
    90+81*7,# e_silver = f_silver + 81,
    90+81*8,# f_gold = e_silver + 81,
    90+81*9,# e_gold = f_gold + 81,
    90+81*10,# f_bishop = e_gold + 81,
    90+81*11,# e_bishop = f_bishop + 81,
    90+81*12,# f_horse = e_bishop + 81,
    90+81*13,# e_horse = f_horse + 81,
    90+81*14,# f_rook = e_horse + 81,
    90+81*15,# e_rook = f_rook + 81,
    90+81*16,# f_dragon = e_rook + 81,
    90+81*17,# e_dragon = f_dragon + 81,
    90+81*18,# fe_old_end = e_dragon + 81,
]
# print(BonaPiece)

def fv40(sfen):
    # board = shogi.Board('lnsgkgsnl/1r5b1/ppppppppp/9/9/9/PPPPPPPPP/1B5R1/LNSGKGSNL b - 1')
    # board = shogi.Board('9/9/9/9/9/k8/9/9/1R2K4 b Gr2b3g4s4n4l18p 1')
    board = shogi.Board(sfen)
    # print(board.kif_str())
    eval_mat=0
    pindex=[]
    qindex=[]
    for square in shogi.SQUARES:
        piece = board.piece_at(square)
        index = 0
        index2 = 0
        if piece and piece.piece_type != 8:
            if int(piece.piece_type) < 7:
                index = 12 + piece.color + piece.piece_type * 2
                index2 = 12 + 1 - piece.color + piece.piece_type * 2
            elif piece.piece_type in {9, 10, 11, 12}:
                index = 12 + piece.color + 5 * 2
                index2 = 12 + 1 - piece.color + 5 * 2
            elif piece.piece_type == 7:
                index = 12 + piece.color + 8 * 2
                index2 = 12 + 1 - piece.color + 8 * 2
            elif piece.piece_type == 13:
                index = 12 + piece.color + 7 * 2
                index2 = 12 + 1 - piece.color + 7 * 2
            elif piece.piece_type == 14:
                index = 12 + piece.color + 9 * 2
                index2 = 12 + 1 - piece.color + 9 * 2
    #        print(SQUARES_R90[square], piece.color, piece.piece_type,index,BonaPiece[index])
            # print(SQUARES_R90[square]+BonaPiece[index])
            pindex.append(SQUARES_R90[square]+BonaPiece[index])
            qindex.append(80-SQUARES_R90[square]+BonaPiece[index2])
            if piece.color == shogi.BLACK:
                eval_mat += material[piece.piece_type]
            else:
                eval_mat -= material[piece.piece_type]
                
    # print(board.pieces_in_hand)
    for color in shogi.COLORS:
        for piece_type, piece_count in board.pieces_in_hand[color].items():
            index = BonaPiece[color + (piece_type - 1) * 2]
            index2 = BonaPiece[1 - color + (piece_type - 1) * 2]
            for i in range(piece_count):
                # print(index+i)
                pindex.append(index+i)
                qindex.append(index2+i)
            if color == shogi.BLACK:
                eval_mat += material[piece_type] * piece_count
            else:
                eval_mat -= material[piece_type] * piece_count

    # print(pindex,len(pindex))
    return SQUARES_R90[board.king_squares[0]], SQUARES_R90[board.king_squares[1]], pindex, qindex, eval_mat, board.turn

def eval(sfen,kk,kkp,kpp):
    k0, k1, fv38, fv38q, e_mat, turn = fv40(sfen)
    # print(k0,k1,fv38,fv38q)
    # print('e_mat=',e_mat)
    # print('kk=',kk[k0][k1])

    kkp_sum=[0,0]
    for i in fv38:
        kkp_sum += kkp[k0][k1][i]
        # print('kkp=',kkp[k0][k1][i]," p=",i)

    kpp_sum0=[0, 0]
    kpp_sum1=[0, 0]
    for i,j in itertools.combinations(fv38, 2):
        kpp_sum0 += kpp[k0][i][j]
        # print('kpp=',kpp[k0][i][j]," p=",i,j)
    for i,j in itertools.combinations(fv38q, 2):
        kpp_sum1 += kpp[80-k1][i][j]
        # print('kpp=',kpp[k1][i][j]," p=",i,j)
    # print('kkp_sum=',kkp_sum)
    # print('kpp_sum0=',kpp_sum0)
    # print('kpp_sum1=',kpp_sum1)
    eval = e_mat
    if turn == shogi.BLACK:
        eval += (kk[k0][k1][0]+kk[k0][k1][1])/32
        eval += (kkp_sum[0]+kkp_sum[1])/32
        eval += (kpp_sum0[0]+kpp_sum0[1])/32
        eval += (-kpp_sum1[0]+kpp_sum1[1])/32
    else:
        eval += (kk[k0][k1][0]-kk[k0][k1][1])/32
        eval += (kkp_sum[0]-kkp_sum[1])/32
        eval += (kpp_sum0[0]-kpp_sum0[1])/32
        eval += (-kpp_sum1[0]-kpp_sum1[1])/32
    # print(eval)
    return eval

def main():
    kk,kkp,kpp=eval_init()
    sfen='lnsgkgsnl/1r5b1/ppppppppp/9/9/9/PPPPPPPPP/1B5R1/LNSGKGSNL b - 1'
    print(sfen,eval(sfen,kk,kkp,kpp))
    sfen ='l6nl/5+P1gk/2np1S3/p1p4Pp/3P2Sp1/1PPb2P1P/P5GS1/R8/LN4bKL w RGgsn5p 1'
    print(sfen,eval(sfen,kk,kkp,kpp))

if __name__ == '__main__':
    main()
