import operator

import utils


class MinMax:
    '''
    Implement minMax algorithm
    '''

    def __init__(self, board_MinMax):
        '''
        configure parameters
        :param board 20*20 list
        '''
        self.board = board_MinMax
        self.size = len(board_MinMax)
        self.max_depth = 2
        self.kill_depth = 10
        self.last_point = (int(self.size / 2), int(self.size / 2))
        self.role = 1
        self.move = (0, 0)
        self.Kill = utils.Kill(self.board, self.kill_depth)
        self.Score = utils.Score(self.board)
        self.Pattern = utils.Pattern(self.board)
        self.Board_ = utils.Board(self.board)
        self.pattern = self.Pattern.get_total_pattern(self.role)
        self.transposition_table = dict()

    def __getitem__(self, point):
        '''
        class could be called from outside
        :param point:
        :return:
        '''
        i, j = point
        return self.board[j][i]

    def __setitem__(self, point, role):
        '''
        class.board value could be set from outside
        :param point:  coordinate(x,y) convert to list[y][x]
        :param role: AI or opponent
        :return:
        '''
        i, j = point
        self.board[j][i] = role
        self.pattern = self.Pattern.update(self.pattern, (j, i), role)
        self.role = 3 - role
        self.last_point = (j, i)
        # print("last_point" + str(self.last_point))

    def min_max(self):
        # If the board is empty, return the coordinate in the center of the board
        if operator.eq(self.board, [[0 for _ in range(self.size)] for _ in range(self.size)]):
            self.move = int(self.size / 2 - 1), int(self.size / 2 - 1)
            return self.move[1], self.move[0]

        # Implememt negative_max algorithm
        self.negamax(self.max_depth, alpha=-float("inf"), beta=float("inf"), role=self.role,
                     pattern=self.pattern, last_point=self.last_point)
        return self.move[1], self.move[0]

    def negamax(self, depth, alpha, beta, role, pattern, last_point):
        '''
        implemet negative_max method, which have the same rule as the Min_Max method
        :param depth: define max_depth of min_max search, must be odd, for example: 5
        :param alpha: the alpha value for alpha beta pruning
        :param beta: the beta value for alpha beta pruning
        :param role: AI (role)or Opponent(3-role)
        :param pattern: A dict save the board pattern message
        :param last_point: the last move position of opponent
        :return: in the end of alpha_beta search, return nothing, but define self.move during search process
        '''
        if depth == 0:
            return self.Score.total_score(pattern, role)

        # search the most potential positions
        free = self.Board_.candidates(pattern, role, last_point)
        candidates = []
        count = 0
        if depth == self.max_depth:
            while len(candidates) < 3 and count < 10 and count < len(free):
                point, new_pattern = free[count]
                x, y = point
                self.board[x][y] = role
                kill_opponent = self.Kill.kill(3 - role, new_pattern, point)
                self.board[x][y] = 0
                if not kill_opponent:
                    candidates.append(free[count])
                count += 1
        else:
            candidates = free[:2]
        # if have no candidates to defend, return first point directly
        if len(candidates) == 0:
            candidates = free[:1]

        iteration = 0
        value = -99999
        for point, new_pattern in candidates:
            x, y = point
            self.board[x][y] = role
            # print(iteration)
            v_new = -self.negamax(depth - 1, -beta, -alpha, 3 - role, new_pattern, (x, y))
            if v_new > value:
                value = v_new
            self.board[x][y] = 0
            alpha_old =  alpha
            alpha = max(alpha, value)

            # do alpha_beta pruning
            if value > alpha_old:
                if depth == self.max_depth:
                    self.move = (x, y)
            if alpha >= beta:
                break
        return value

    def get_key(self):
        key = ""
        for x in range(self.size):
            for y in range(self.size):
                if self.board[x][y]=="1":
                    key += "1"
                elif self.board[x][y]=="2":
                    key += "2"
                else:
                    key += "0"
        return key


board_initialize = [[0 for _ in range(20)] for _ in range(20)]
board = MinMax(board_initialize)

class TTEntry:
    def __init__(self, value=0, depth=0, flag=""):
        self.value = value
        self.depth = depth
        self.flag = flag

