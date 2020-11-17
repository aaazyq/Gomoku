import minMax as AI
import pisqpipe as pp
from pisqpipe import DEBUG_EVAL

pp.infotext = 'name="pbrain-pyrandom", author="Jan Stransky", version="1.0", country="Czech Republic", www="https://github.com/stranskyjan/pbrain-pyrandom"'

MAX_BOARD = 100


def brain_init():
    if pp.width < 5 or pp.height < 5:
        pp.pipeOut("ERROR size of the board")
        return
    if pp.width > MAX_BOARD or pp.height > MAX_BOARD:
        pp.pipeOut("ERROR Maximal board size is {}".format(MAX_BOARD))
        return
    pp.pipeOut("OK")


def brain_restart():
    for x in range(pp.width):
        for y in range(pp.height):
            AI.board[x, y] = 0
    pp.pipeOut("OK")


def isFree(x, y):
    return 0 <= x < pp.width and 0 <= y < pp.height and AI.board[x, y] == 0


def brain_my(x, y):
    if isFree(x, y):
        AI.board[x, y] = 1
    else:
        pp.pipeOut("ERROR my move [{},{}]".format(x, y))


def brain_opponents(x, y):
    if isFree(x, y):
        AI.board[x, y] = 2
    else:
        pp.pipeOut("ERROR opponents's move [{},{}]".format(x, y))


def brain_block(x, y):
    if isFree(x, y):
        AI.board[x, y] = 3
    else:
        pp.pipeOut("ERROR winning move [{},{}]".format(x, y))


def brain_takeback(x, y):
    if 0 <= x < pp.width and 0 <= y < pp.height and AI.board[x, y] != 0:
        AI.board[x, y] = 0
        return 0
    return 2


def brain_turn():
    if pp.terminateAI:
        return
    x, y = AI.board.min_max()
    pp.do_mymove(x, y)


def brain_end():
    pass


def brain_about():
    pp.pipeOut(pp.infotext)


if DEBUG_EVAL:
    import win32gui


    def brain_eval(x, y):
        # TODO check if it works as expected
        wnd = win32gui.GetForegroundWindow()
        dc = win32gui.GetDC(wnd)
        rc = win32gui.GetClientRect(wnd)
        c = str(AI.board[x, y])
        win32gui.ExtTextOut(dc, rc[2] - 15, 3, 0, None, c, ())
        win32gui.ReleaseDC(wnd, dc)

######################################################################
# A possible way how to debug brains.
# To test it, just "uncomment" it (delete enclosing """)
######################################################################
"""
# define a file for logging ...
DEBUG_LOGFILE = "/tmp/pbrain-pyrandom.log"
# ...and clear it initially
with open(DEBUG_LOGFILE,"w") as f:
	pass

# define a function for writing messages to the file
def logDebug(msg):
	with open(DEBUG_LOGFILE,"a") as f:
		f.write(msg+"\n")
		f.flush()

# define a function to get exception traceback
def logTraceBack():
	import traceback
	with open(DEBUG_LOGFILE,"a") as f:
		traceback.print_exc(file=f)
		f.flush()
	raise

# use logDebug wherever
# use try-except (with logTraceBack in except branch) to get exception info
# an example of problematic function
def brain_turn():
	logDebug("some message 1")
	try:
		logDebug("some message 2")
		1. / 0. # some code raising an exception
		logDebug("some message 3") # not logged, as it is after error
	except:
		logTraceBack()
"""
######################################################################

# "overwrites" functions in pisqpipe module
pp.brain_init = brain_init
pp.brain_restart = brain_restart
pp.brain_my = brain_my
pp.brain_opponents = brain_opponents
pp.brain_block = brain_block
pp.brain_takeback = brain_takeback
pp.brain_turn = brain_turn
pp.brain_end = brain_end
pp.brain_about = brain_about
if DEBUG_EVAL:
    pp.brain_eval = brain_eval


def main():
    pp.main()


def print_board(board):
    for i in range(20):
        for j in range(20):
            print(board[i, j]," ", end='')
            if j == 19:
                print("")


if __name__ == "__main__":
    pp.main()
    # # AI.board[0, 1] = 1
    # AI.board[9, 9] = 2
    # AI.board[9, 10] = 1
    # AI.board[10, 10] = 2
    # AI.board[11, 11] = 1
    # # AI.board[8, 9] = 2
    # # AI.board[7, 9] = 1
    # # AI.board[10, 9] = 2
    # # AI.board[10, 8] = 1
    # # AI.board[11, 9] = 2
    # # AI.board[12, 9] = 1
    # # AI.board[8, 12] = 2
    # # AI.board[9, 11] = 1
    # # AI.board[10, 12] = 2
    # # AI.board[9, 12] = 1
    # # AI.board[8, 11] = 2
    # # AI.board[8, 10] = 1
    # # AI.board[10, 13] = 2
    # # AI.board[10, 11] = 1
    # # AI.board[8, 13] = 2
    # # AI.board[12, 11] = 1
    # # AI.board[13, 11] = 2
    # # AI.board[12, 8] = 1
    # # AI.board[12, 10] = 2
    # # AI.board[5, 7] = 1
    # # AI.board[6, 8] = 2
    # # AI.board[13, 8] = 1
    # print_board(AI.board)
    # x, y = AI.board.min_max()
    # print(x, y)
    # # print(AI.board.get_key())
    # print("")
    # AI.board[x, y] = 2
    # # AI.board.move = (y, x)
    # # print_board(AI.board)
    #
    # AI.board[7, 9] = 1
    # print_board(AI.board)
    # x2, y2 = AI.board.min_max()
    # AI.board[x2, y2] = 2
    # # print(x2, y2)
    # # # AI.board.move = (x, y)
    # #
    # # AI.board[10, 8] = 1
    # # x, y = AI.board.min_max()
    # # AI.board[x, y] = 2
    # # print(x, y)
    # # # AI.board.move = (x, y)
    # #
    # # AI.board[12, 9] = 1
    # # x, y = AI.board.min_max()
    # # AI.board[x, y] = 2
    # # print(x, y)
    # # # AI.board.move = (x, y)
    # #
    # # AI.board[9, 11] = 1
    # # x, y = AI.board.min_max()
    # # AI.board[x, y] = 2
    # # print(x, y)
    # # # AI.board.move = (x, y)
    #
    # AI.board[10, 9] = 1
    # print_board(AI.board)
    #
    # for i in range(5):
    #     x, y = AI.board.min_max()
    #     AI.board[x, y] = 2
    #     print("2:", x, y)
    #
    #     x, y = AI.board.min_max()
    #     AI.board[x, y] = 1
    #     print("1:",x, y)
    # # AI.board.move = (x, y)
    #
    #
    # print_board(AI.board)
    # # print(AI.board.get_key())
