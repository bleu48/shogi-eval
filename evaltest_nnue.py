# NNUEを読むテスト 2019.2.10
import struct
import numpy
import shogi

SQUARES_R90=[0]*81
for square in shogi.SQUARES:
    SQUARES_R90[square]=shogi.SQUARES_L90.index(square)

# material = [0,90,315,405,495,540,855,990,15000,
#     540,540,540,540,945,1395]

nn_data = open("eval/nn.bin", "rb").read()

i=struct.unpack_from("<I", nn_data, 0)[0]
print(f'Version: {i:#x}')
h=struct.unpack_from("<I", nn_data, 4)[0]
print(f'Hash: {h:#x}')

i=struct.unpack_from("<I", nn_data, 8)[0]
print(f'string size: {i}')
s=struct.unpack_from("<"+str(i)+"s", nn_data, 12)[0]
print("model string:",s)

h=struct.unpack_from("<I", nn_data, 12+i)[0]
print(f'Hash: {h:#x}')

bias=struct.unpack_from("<"+str(256)+"h", nn_data, 16+i)
# print('bias: ')
# print(bias)
bias1 =  numpy.array( bias)
weight=struct.unpack_from("<"+str(256*125388)+"h", nn_data, 16+i+256*2)
# print(f'weight: {weight}')
# weight1 =  numpy.array( weight).reshape(81,1548,256)
# weight1s = numpy.array( weight).reshape(256,125388)
weight1s = numpy.array(weight).reshape(125388,256).T

# print(4+4+4+178 +4+ 2*(256+256*125388) +4+ 4*32+32*512 + 4*32+32*32 + 4*1+1*32 )

h=struct.unpack_from("<I", nn_data, 16+i+2*(256+256*125388))[0]
print(f'Hash: {h:#x}')

bias=struct.unpack_from("<"+str(32)+"i", nn_data, 16+i+2*(256+256*125388)+4)
# print('bias: ')
# print(bias)
bias2 =  numpy.array( bias)
weight=struct.unpack_from("<"+str(512*32)+"b", nn_data, 16+i+2*(256+256*125388)+4 + 4*32)
weight2 = numpy.array( weight).reshape(32,512)
# print(f'weight: {weight}')
# print(f'weight1: {weight1}')

bias=struct.unpack_from("<"+str(32)+"i", nn_data, 16+i+2*(256+256*125388)+4+ 4*32+32*512)
# print('bias: ')
# print(bias)
bias3 =  numpy.array( bias)
weight=struct.unpack_from("<"+str(32*32)+"b", nn_data, 16+i+2*(256+256*125388)+4+ 4*32+32*512 + 4*32)
# print(f'weight: {weight}')
weight3 = numpy.array( weight).reshape(32,32)

bias=struct.unpack_from("<"+str(1)+"i", nn_data, 16+i+2*(256+256*125388)+4+ 4*32+32*512 + 4*32+32*32)
# print('bias: ')
# print(bias)
bias4 = bias[0]
# print(bias4)
weight=struct.unpack_from("<"+str(32*1)+"b", nn_data, 16+i+2*(256+256*125388)+4+ 4*32+32*512 + 4*32+32*32 + 4*1)
# print(f'weight: {weight}')
weight4 = numpy.array( weight) #.reshape(1,32)


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

def fv40(sfen):
    # board = shogi.Board('lnsgkgsnl/1r5b1/ppppppppp/9/9/9/PPPPPPPPP/1B5R1/LNSGKGSNL b - 1')
    # board = shogi.Board('9/9/9/9/9/k8/9/9/1R2K4 b Gr2b3g4s4n4l18p 1')
    board = shogi.Board(sfen)
    # print(board.kif_str())
    # eval_mat=0
    pindex=[]
    qindex=[]
    for square in shogi.SQUARES:
        piece = board.piece_at(square)
        index = 0
        index2 = 0
        if piece and piece.piece_type != 8:
            if piece.piece_type < 7:
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
            # if piece.color == shogi.BLACK:
            #     eval_mat += material[piece.piece_type]
            # else:
            #     eval_mat -= material[piece.piece_type]
                
    # print(board.pieces_in_hand)
    for color in shogi.COLORS:
        for piece_type, piece_count in board.pieces_in_hand[color].items():
            index = BonaPiece[color + (piece_type - 1) * 2]
            index2 = BonaPiece[1 - color + (piece_type - 1) * 2]
            for i in range(piece_count):
                # print(index+i)
                pindex.append(index+i)
                qindex.append(index2+i)
            # if color == shogi.BLACK:
            #     eval_mat += material[piece_type] * piece_count
            # else:
            #     eval_mat -= material[piece_type] * piece_count

    # print(pindex,len(pindex))
    if board.turn==shogi.BLACK:
        return SQUARES_R90[board.king_squares[0]], 80-SQUARES_R90[board.king_squares[1]], pindex, qindex
    else:
        return 80-SQUARES_R90[board.king_squares[1]], SQUARES_R90[board.king_squares[0]], qindex, pindex

def eval(sfen):
    k0, k1, fv38, fv38q = fv40(sfen)

    # print(k0,k1,fv38,fv38q)

    # x=numpy.zeros(256)
    # for i in range(256):
    #     x[i]=bias1[i]
    #     for j in range(38):
    #         # x[i] += weight1[k0,fv38[j],i]
    #         x[i] += weight1s[k0*1548+fv38[j],i]
    # # print(x)
    # x2=numpy.zeros(256)
    # for i in range(256):
    #     x2[i]=bias1[i]
    #     for j in range(38):
    #         # x2[i] += weight1[80-k1,fv38q[j],i]
    #         x2[i] += weight1s[(80-k1)*1548+fv38q[j],i]
    # # print(x2)

    # x=numpy.zeros(256)
    # for i in range(256):
    #     x[i]=bias1[i]
    #     for j in range(38):
    #         x[i] += weight1s[i,k0*1548+fv38[j]]

    # print(x)

    xx=numpy.zeros(125388)
    for j in range(38):
        xx[k0*1548+fv38[j]] = 1
    x=bias1+weight1s.dot(xx) # 手番
    # print(x)

    xx=numpy.zeros(125388)
    for j in range(38):
        xx[k1*1548+fv38q[j]] = 1
    x2=bias1+weight1s.dot(xx) # 非手番
    x=numpy.append(x,x2)
    # print(x2)
    # if turn==shogi.BLACK:
    #     x=numpy.append(x,x2)
    # else:
    #     x=numpy.append(x2,x)

    # x=numpy.where(x<0,0,x // 64)
    x=numpy.where(x<0,0,x)
    x=numpy.where(x>127,127,x)
    # print(x)
    x=bias2+weight2.dot(x)
    # print(x)
    x=numpy.where(x<0,0,x // 64)
    x=numpy.where(x>127,127,x)
    # print(x)
    x=bias3+weight3.dot(x)
    # print(x)
    x=numpy.where(x<0,0,x // 64)
    x=numpy.where(x>127,127,x)
    # print(x)
    x=bias4+weight4.dot(x)
    # print(x,e_mat)
    # x=numpy.where(x<0,0,x // 64)
    # x=numpy.where(x>127,127,x)
    return (x // 16)

def main():
    sfen='lnsgkgsnl/1r5b1/ppppppppp/9/9/9/PPPPPPPPP/1B5R1/LNSGKGSNL b - 1'
    print(sfen,eval(sfen))
    # 40 orqha
    # 15 illqha2.1
    sfen='lnsgkgsnl/1r5b1/ppppppppp/9/9/9/PPPPPPPPP/1B5R1/LNSGKGSNL w - 1'
    print(sfen,eval(sfen))
    # 40 orqha
    sfen ='l6nl/5+P1gk/2np1S3/p1p4Pp/3P2Sp1/1PPb2P1P/P5GS1/R8/LN4bKL w RGgsn5p 1'
    print(sfen,eval(sfen))
    # -873 orqha
    # -875 illqha2.1
    sfen ='l6nl/5+P1gk/2np1S3/p1p4Pp/3P2Sp1/1PPb2P1P/P5GS1/R8/LN4bKL b RGgsn5p 1'
    print(sfen,eval(sfen))
    # 1952 orqha
    # 2096 illqha2.1

if __name__ == '__main__':
    main()

