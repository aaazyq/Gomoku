import copy


class Board:
    '''
    implement movements on the board
    '''

    def __init__(self, board):
        '''
        initialize Board class
        :param board: a list of 20*20
        '''
        self.board = board
        self.size = len(board)

    def candidates(self, old_pattern, role, last_point):
        '''
        search the most potential positions
        :param old_pattern:  current board pattern
        :param role: AI or Opponent
        :param last_point: the last move of opponent (x,y)
        :return: list contain point and respond new pattern, for example：［(1,1) {[3,2]: 1}］
        '''
        pos = []

        limit = (self.get_limit() + 2) * 2

        directions = self.sort_directions(last_point)
        iteration = 1
        while iteration < limit:
            pos = self.sort_steps(directions, iteration, last_point, old_pattern, role, pos)
            iteration += 1
        pos_list = sorted(pos, key=lambda item: item[1][0], reverse=True)
        pattern_list = [(p[0], p[1][1]) for p in pos_list]
        return pattern_list

    def get_limit(self):
        rows = [sum(self.board[i]) == 0 for i in range(self.size)]
        cols = [sum(self.board[:][j]) == 0 for j in range(self.size)]
        mid_rows = rows[rows.index(False) + 1:]
        mid_rows.reverse()

        if False in mid_rows:
            limit_rows = mid_rows.index(False)
        else:
            limit_rows = 0

        mid_cols = cols[cols.index(False) + 1:]
        mid_cols.reverse()
        if False in mid_cols:
            limit_cols = mid_cols.index(False)
        else:
            limit_cols = 0
        return max(limit_cols, limit_rows)

    def sort_directions(self, point):
        '''
        search directions with more room near opponent's last move
        :param point: last move (x,y)
        :return: sorted directions dic
        '''
        directions = dict()
        x, y = point
        if x > self.size - x - 1:
            directions["dx"] = (-1, 1)
        else:
            directions["dx"] = (1, -1)
        if y > self.size - y - 1:
            directions["dy"] = (-1, 1)
        else:
            directions["dy"] = (1, -1)
        return directions

    def sort_steps(self, directions, iteration, point, old_pattern, role, pos):
        '''
        for given iteration, search the empty points and score it
        :param directions: the sorted directions define in self.sort_directions
        :param iteration: the total number of steps
        :param point: (x,y) the last movement of opponent
        :param old_pattern: the current board pattern
        :param role: AI or opponent
        :param pos: list to save points which have been searched
        :return:
        '''
        x0, y0 = point

        for x1, y1 in [(x0 + iteration * directions["dx"][0], y0), (x0 + iteration * directions["dx"][1], y0),
                       (x0, y0 + iteration * directions["dy"][0]), (x0, y0 + iteration * directions["dy"][1])]:
            if 0 <= x1 < self.size and 0 <= y1 < self.size and self.board[x1][y1] == 0:
                # choice the position important to both AI and Opponent
                update_AI_pattern = Pattern(self.board).update(old_pattern, (x1, y1), role)
                update_OP_pattern = Pattern(self.board).update(old_pattern, (x1, y1), 3 - role)
                # score = Score(self.board).total_score(update_AI_pattern, role) + Score(self.board).total_score(
                    # update_OP_pattern, 3 - role)
                score = Score(self.board).total_score(update_AI_pattern, role)
                pos.append([(x1, y1), [score, update_AI_pattern]])

        step_x = 1
        while step_x < iteration:
            for dx in directions["dx"]:
                for dy in directions["dy"]:
                    x2 = step_x * dx + x0
                    y2 = (iteration - step_x) * dy + y0
                    if 0 <= x2 < self.size and 0 <= y2 < self.size and self.board[x2][y2] == 0:
                        # choice the position important to both AI and Opponent
                        update_AI_pattern = Pattern(self.board).update(old_pattern, (x2, y2), role)
                        update_OP_pattern = Pattern(self.board).update(old_pattern, (x2, y2), 3 - role)
                        # score = Score(self.board).total_score(update_AI_pattern, role) + Score(self.board).total_score(
                            # update_OP_pattern, 3 - role)
                        score = Score(self.board).total_score(update_AI_pattern, role)
                        pos.append([(x2, y2), [score, update_AI_pattern]])
            step_x += 1
        return pos


class Score:
    '''
    evaluate score for a given board
    board: 20*20 list represent a board
    point: chess position (x,y)
    rule: 0 empty ; 1 occupied by AI ; 2 occupied by opponent
    '''

    def __init__(self, board):
        self.board = board
        self.size = len(self.board)

    def checkWinner(self, check_pattern):
        AI_lens = [key[0] for key in check_pattern[1].keys()]
        if len(AI_lens) > 0 and max(AI_lens) >= 5:
            return 1
        OP_lens = [key[0] for key in check_pattern[2].keys()]
        if len(OP_lens) > 0 and max(OP_lens) >= 5:
            return 2
        return 0

    def total_score(self, total_pattern, role):
        '''
        return total score, which equals score of role minus score of opponent
        :param total_pattern: dict save AI pattern and opponent pattern
        :param role: AI or opponent
        :return: total score
        '''
        AI_score = self.get_score(total_pattern[role])
        opponent_score = self.get_score(total_pattern[3 - role])
        total_score = AI_score - 1.4 * opponent_score
        return total_score

    def get_score(self, score_pattern):
        '''
        keys of score dict are (length of chess in a line for specified direction, number of live nodes)
        :return: score of pattern
        '''
        score = 0
        # score_dic = {
        #     (1, 1): 1,
        #     (1, 2): 10,
        #     (2, 1): 10,
        #     (2, 2): 100,
        #     (3, 1, "S"): 100,
        #     (3, 2, "S"): 1000,
        #     (3, 1): 100,
        #     (3, 2): 1000,
        #     (4, 0, "S"): 1100,
        #     (4, 1, "S"): 1100,
        #     (4, 2, "S"): 100000,
        #     (4, 1): 1100,
        #     (4, 2): 100000}

        score_dic = {
            (1, 1): 1,
            (1, 2): 10,
            (2, 1): 10,
            (2, 2): 100,
            (3, 1, "S"): 100,
            (3, 2, "S"): 1000,
            (3, 1): 1000,
            (3, 2): 10000,
            (4, 0, "S"): 10000,
            (4, 1, "S"): 15000,
            (4, 2, "S"): 100000,
            (4, 1): 200000,
            (4, 2): 1000000}

        live3_count = 0
        for key in score_pattern.keys():
            length = key[0]
            if key == (3, 2) or key == (3, 1, "S"):
                live3_count += score_pattern[key]
            if length >= 5:
                score += 1000000
            else:
                score += score_dic[key] * score_pattern[key]
        if live3_count >= 2:
            score += 300
        return score


class Pattern:
    '''
    enumerate common pattern on board
    '''

    def __init__(self, board):
        self.board = board
        self.size = len(board)
        self.status = {"N": {"length": 0, "end": 0}, "S": {"length": [0, 0], "end": 0}}
        self.size = len(self.board)

    def get_total_pattern(self, role):
        '''
        get AI pattern and opponent pattern by search the whole board
        :param role: AI or Opponent
        :return:
        '''
        AI_pattern = self.get_pattern(role)
        opponent_pattern = self.get_pattern(3 - role)
        total_pattern = {role: AI_pattern, 3 - role: opponent_pattern}
        return total_pattern

    def get_pattern(self, role):
        '''
        get pattern(AI or Opponent) by search the whole board
        :param role: AI or Opponent
        :return: pattern
        '''
        role_pattern = dict()
        direct = (0, 1)
        for x in range(self.size):
            y = 0
            role_pattern = self.direct_search((x, y), direct, role, role_pattern)
        direct = (1, 0)
        for y in range(self.size):
            x = 0
            role_pattern = self.direct_search((x, y), direct, role, role_pattern)

        direct = (1, 1)
        for x in range(self.size):
            y = 0
            role_pattern = self.direct_search((x, y), direct, role, role_pattern)
        for y in range(1, self.size, 1):
            x = 0
            role_pattern = self.direct_search((x, y), direct, role, role_pattern)
        direct = (-1, 1)
        for x in range(self.size):
            y = 0
            role_pattern = self.direct_search((x, y), direct, role, role_pattern)
        for y in range(1, self.size, 1):
            x = self.size - 1
            role_pattern = self.direct_search((x, y), direct, role, role_pattern)

        return role_pattern

    def direct_search(self, point, direct, role, direct_pattern):
        '''
        search the whole board from different directions
        :param point: the start point, always located in the edge of board
        :param direct: one of the 8 directions on board, for example: (1,1)
        :param role: AI or Opponent
        :param direct_pattern: the dict to save point which have been searched
        :return: the updated pattern dict
        '''

        x, y = point
        dx, dy = direct
        state = copy.deepcopy(self.status)
        start = 3 - role
        while 0 <= x < self.size and 0 <= y < self.size:
            if self.board[x][y] == role:
                state["N"]["length"] += 1
            if self.board[x][y] == 0:
                if state["N"]["length"] > 0:
                    self.get_next_length((x, y), direct, role, state)
                    if start == 0:
                        state["N"]["end"] += 1
                        state["S"]["end"] += 1
                    state["N"]["end"] += 1
                    if (state["N"]["length"], state["N"]["0"]) in direct_pattern.keys():
                        direct_pattern[(state["N"]["length"], state["N"]["end"])] += 1
                    else:
                        direct_pattern[(state["N"]["length"], state["N"]["end"])] = 1
                    if state["S"]["length"] > 0 and state["S"]["length"] + state["N"]["length"] == 3:
                        if start == 0 or state["S"]["end"] == 1:
                            end = state["S"]["end"]
                            if start == 0:
                                end += 1
                            if end > 0:
                                if (3, end, "S") in direct_pattern.keys():
                                    direct_pattern[(3, end, "S")] += 1
                                else:
                                    direct_pattern[(3, end, "S")] = 1
                    if state["S"]["length"] > 0 and state["S"]["length"] + state["N"]["length"] == 4:
                        if start == 0 or state["S"]["end"] == 1:
                            end = state["S"]["end"]
                            if start == 0:
                                end += 1
                            if (4, end, "S") in direct_pattern.keys():
                                direct_pattern[(4, end, "S")] += 1
                            else:
                                direct_pattern[(4, end, "S")] = 1
                state = copy.deepcopy(self.status)
                start = 0
            if self.board[x][y] == 3 - role:
                if state["N"]["length"] > 0:
                    if start == 0:
                        state["N"]["end"] += 1
                    if state["N"]["end"] > 0:
                        if (state["N"]["length"], state["N"]["end"]) in direct_pattern.keys():
                            direct_pattern[(state["length"], state["end"])] += 1
                        else:
                            direct_pattern[(state["length"], state["end"])] = 1
                state = copy.deepcopy(self.status)
                start = 3 - role
            x += dx
            y += dy
        if state["N"]["length"] > 0:
            if start == 0:
                state["end"] += 1
            if state["N"]["end"] > 0:
                if (state["length"], state["end"]) in direct_pattern.keys():
                    direct_pattern[(state["length"], state["end"])] += 1
                else:
                    direct_pattern[(state["length"], state["end"])] = 1
        return direct_pattern

    def update(self, old_pattern, point, role):
        '''
        update the old pattern by search area near target point
        :param old_pattern: pattern dict contain AI(1) and Opponent Pattern(2)
        [{AI:{[length, number of live end]: count}}{Opponent:{[length, number of live end]:count}}]
        for example [{1:{[3, 2]:1}}{2:{[2,1]:1,[1,2]:1}}]
        :param point: the target point, for example(10,10)
        :param role: AI(1) or Opponent(2)
        :return: updated pattern
        '''
        update_pattern = copy.deepcopy(old_pattern)
        point_AI_pattern, point_OP_pattern = self.get_point(point, role)
        for key in [(1, 0), (1, 1), (0, 1), (-1, 1)]:
            dx, dy = key
            len_AI, end_AI = point_AI_pattern[(dx, dy)]["N"]["length"], point_AI_pattern[(dx, dy)]["N"]["end"]
            len_OP, end_OP = point_OP_pattern[(dx, dy)]["N"]["length"], point_OP_pattern[(dx, dy)]["N"]["end"]
            len_AI_N, end_AI_N = point_AI_pattern[(-dx, -dy)]["N"]["length"], point_AI_pattern[(-dx, -dy)]["N"]["end"]
            len_OP_N, end_OP_N = point_OP_pattern[(-dx, -dy)]["N"]["length"], point_OP_pattern[(-dx, -dy)]["N"]["end"]

            len_S_AI, end_S_AI = point_AI_pattern[(dx, dy)]["S"]["length"], point_AI_pattern[(dx, dy)]["S"]["end"]
            len_S_AI_N, end_S_AI_N = point_AI_pattern[(-dx, -dy)]["S"]["length"], point_AI_pattern[(-dx, -dy)]["S"][
                "end"]
            len_S_OP, end_S_OP = point_OP_pattern[(dx, dy)]["S"]["length"], point_OP_pattern[(dx, dy)]["S"]["end"]
            len_S_OP_N, end_S_OP_N = point_OP_pattern[(-dx, -dy)]["S"]["length"], point_OP_pattern[(-dx, -dy)]["S"][
                "end"]

            # update split pattern
            # update AI (Split 4)
            cond1 = sum(len_S_AI) == 1 and len_AI_N == 1
            cond2 = sum(len_S_AI) == 2 and len_AI_N == 0
            cond3 = sum(len_S_AI_N) == 1 and len_AI == 1
            cond4 = sum(len_S_AI_N) == 2 and len_AI == 0
            if cond1 or cond2:
                end = end_S_AI + end_AI_N
                if end > 0:
                    key = (3, end, "S")
                    if key in update_pattern[role].keys():
                        update_pattern[role][key] += 1
                    else:
                        update_pattern[role][key] = 1
            if cond3 or cond4:
                end = end_S_AI_N + end_AI
                if end > 0:
                    key = (3, end, "S")
                    if key in update_pattern[role].keys():
                        update_pattern[role][key] += 1
                    else:
                        update_pattern[role][key] = 1

            if len_AI_N + len_AI == 3 and (len_AI != 0 and len_AI_N != 0):
                end = end_AI + end_AI_N
                if end > 0:
                    update_pattern[role][(3, end, "S")] -= 1

            # update AI(Split 5)
            cond1 = sum(len_S_AI) == 1 and len_AI_N == 2
            cond2 = sum(len_S_AI) == 2 and len_AI_N == 1
            cond3 = sum(len_S_AI) == 3 and len_AI_N == 0
            cond4 = sum(len_S_AI_N) == 1 and len_AI == 2
            cond5 = sum(len_S_AI_N) == 2 and len_AI == 1
            cond6 = sum(len_S_AI_N) == 3 and len_AI == 0
            if cond1 or cond2 or cond3:
                end = end_S_AI + end_AI_N
                key = (4, end, "S")
                if key in update_pattern[role].keys():
                    update_pattern[role][key] += 1
                else:
                    update_pattern[role][key] = 1
            if cond4 or cond5 or cond6:
                end = end_S_AI_N + end_AI
                key = (4, end, "S")
                if key in update_pattern[role].keys():
                    update_pattern[role][key] += 1
                else:
                    update_pattern[role][key] = 1

            if len_AI_N + len_AI == 4 and (len_AI != 0 and len_AI_N != 0):
                end = end_AI + end_AI_N
                update_pattern[role][(4, end, "S")] -= 1

            # update opponent (Split 4)
            if len_OP + len_OP_N == 3 and len_OP != 0 and len_OP_N != 0:
                end = end_OP + end_OP_N
                if end > 0:
                    update_pattern[3 - role][(3, end, "S")] -= 1

            if sum(len_S_OP) == 3 and len_S_OP[0] > 0:
                end = end_S_OP + 1
                update_pattern[3 - role][(3, end, "S")] -= 1
                if end_S_OP > 0:
                    if (3, end_S_OP, "S") in update_pattern[3 - role].keys():
                        update_pattern[3 - role][(3, end_S_OP, "S")] += 1
                    else:
                        update_pattern[3 - role][(3, end_S_OP, "S")] = 1

            if sum(len_S_OP_N) == 3 and len_S_OP_N[0] > 0:
                end = end_S_OP_N + 1
                update_pattern[3 - role][(3, end, "S")] -= 1
                if end_S_OP_N > 0:
                    if (3, end_S_OP_N, "S") in update_pattern[3 - role].keys():
                        update_pattern[3 - role][(3, end_S_OP_N, "S")] += 1
                    else:
                        update_pattern[3 - role][(3, end_S_OP_N, "S")] = 1

            # update opponent (Split 5)
            if len_OP + len_OP_N == 4 and len_OP != 0 and len_OP_N != 0:
                end = end_OP + end_OP_N
                update_pattern[3 - role][(4, end, "S")] -= 1

            if sum(len_S_OP) == 4 and len_S_OP[0] > 0:
                end = end_S_OP + 1
                update_pattern[3 - role][(4, end, "S")] -= 1
                if (4, end_S_OP, "S") in update_pattern[3 - role].keys():
                    update_pattern[3 - role][(4, end_S_OP, "S")] += 1
                else:
                    update_pattern[3 - role][(4, end_S_OP, "S")] = 1

            if sum(len_S_OP_N) == 4 and len_S_OP_N[0] > 0:
                end = end_S_OP_N + 1
                update_pattern[3 - role][(4, end, "S")] -= 1
                if (4, end_S_OP_N, "S") in update_pattern[3 - role].keys():
                    update_pattern[3 - role][(4, end_S_OP_N, "S")] += 1
                else:
                    update_pattern[3 - role][(4, end_S_OP_N, "S")] = 1

            # update normal pattern
            if len_AI > 0:
                update_pattern[role][len_AI, end_AI + 1] -= 1

            elif len_OP > 0:
                if end_OP > 0:
                    if (len_OP, end_OP) in update_pattern[3 - role].keys():
                        update_pattern[3 - role][len_OP, end_OP] += 1
                    else:
                        update_pattern[3 - role][len_OP, end_OP] = 1

                update_pattern[3 - role][len_OP, end_OP + 1] -= 1

            if len_AI_N > 0:
                update_pattern[role][len_AI_N, end_AI_N + 1] -= 1

            elif len_OP_N > 0:
                if end_OP_N > 0:
                    if (len_OP_N, end_OP_N) in update_pattern[3 - role].keys():
                        update_pattern[3 - role][len_OP_N, end_OP_N] += 1
                    else:
                        update_pattern[3 - role][len_OP_N, end_OP_N] = 1
                update_pattern[3 - role][len_OP_N, end_OP_N + 1] -= 1
            next_length = len_AI + len_AI_N + 1
            next_end = end_AI + end_AI_N
            if next_end > 0 or next_length ==5:
                if (next_length, next_end) in update_pattern[role].keys():
                    update_pattern[role][next_length, next_end] += 1
                else:
                    update_pattern[role][next_length, next_end] = 1

        return update_pattern

    def get_point(self, point, role):
        '''
        get the AI and Opponent distribution info near the point
        :param point: for example (10,10)
        :param role: AI(1) or Opponent(2)
        :return: AI point pattern and Opponent point pattern
        '''
        point_AI_pattern = dict()
        point_OP_pattern = dict()
        for i in range(-1, 2, 1):
            for j in range(-1, 2, 1):
                if i != 0 or j != 0:
                    point_AI_pattern[(i, j)] = self.get_length(point, role, (i, j))
                    point_OP_pattern[(i, j)] = self.get_length(point, 3 - role, (i, j))
        return point_AI_pattern, point_OP_pattern

    def get_length(self, point, role, direction):
        '''
        get the AI or Opponent distribution info on one of the 8 directions
        :param point: target point, for example: (10,10)
        :param role: AI or Opponent
        :param direction: one of the 8 directions on the board
        :return: direction status dict
        '''
        dx, dy = direction
        x, y = point
        status = copy.deepcopy(self.status)
        while True:
            x += dx
            y += dy
            if 0 <= x < self.size and 0 <= y < self.size:
                if self.board[x][y] == role:
                    status["N"]["length"] += 1
                else:
                    if self.board[x][y] == 0:
                        status["N"]["end"] = 1
                        status = self.get_next_length((x, y), direction, role, status)
                        if status["S"]["length"][1] > 0:
                            status["S"]["length"][0] = copy.deepcopy(status["N"]["length"])
                            return status
                    return status
            else:
                return status

    def get_next_length(self, point, direction, role, status):
        dx, dy = direction
        x, y = point
        while True:
            x += dx
            y += dy
            if 0 <= x < self.size and 0 <= y < self.size:
                if self.board[x][y] == role:
                    status["S"]["length"][1] += 1
                else:
                    if self.board[x][y] == 0:
                        status["S"]["end"] = 1
                    return status
            else:
                return status


class Kill:
    '''
    implement method to judge the possibility to conduct a kill or to be killed in the future
    '''

    def __init__(self, board, max_depth):
        self.max_depth = max_depth
        self.board = board

    def kill(self, role, kill_pattern, last_point):
        return self.killer(role, kill_pattern, self.max_depth, last_point, 0)

    def check_kill(self, kill_pattern, role):
        '''
        check if the pattern satisfies the kill conditions
        :param kill_pattern: the current pattern to be checked
        :param role: AI or Opponent
        :return: True or False
        '''
        kills = {(4, 1): 0, (3, 2): 0, (3, 2, "S"): 0, (4, 0, "S"): 0, (4, 1, "S"): 0, (4, 2, "S"): 0}
        for key in kill_pattern[role].keys():
            length = key[0]
            if length == 5:
                return True, 3
            if key == (4, 2):
                return True, 2
            if key == (4, 2, "S"):
                return True, 2
            if key in kills.keys():
                kills[key] += kill_pattern[role][key]
        if (kills[(4, 1)] > 0 + kills[(4, 1, "S")] + kills[(4, 0, "S")] > 0) and kills[(4, 1, "S")] + kills[(4, 1)] + \
                kills[(3, 2)] + kills[(3, 2, "S")] + kills[(4, 0, "S")] >= 2:
            return True, 2
        elif kills[(3, 2)] >= 2 or kills[(3, 2, "S")] >= 2:
            return True, 1
        return False, 0

    def killer(self, role, kill_pattern, depth, last_point, kill_score):
        '''
        Judge if the role could conduct a kill
        :param role: AI or Opponent
        :param kill_pattern: the current pattern
        :param depth: the depth have reached
        :param last_point: the last move of opponent
        :return: True(kill successed) or False(kill failed)
        '''

        winner = Score(self.board).checkWinner(kill_pattern)
        if winner == role:
            return True

        elif winner == 3 - role:
            return False

        if depth == 0:
            return False

        # search the most potential positions
        frees = Board(self.board).candidates(kill_pattern, role, last_point)
        for point, next_pattern in frees[:20]:
            x, y = point

            # check if I could conduct a kill
            check, score_new = self.check_kill(next_pattern, role)
            if check and score_new > kill_score:
                # move to the position
                self.board[x][y] = role

                # check if the opponent could conduct a kill(for defense)
                my_kill = not self.killer(3 - role, next_pattern, depth - 1, (x, y), score_new)

                # move back
                self.board[x][y] = 0
                if my_kill:
                    return True
        return False
