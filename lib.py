import copy

from consts import SUDOKU_VALUES, SUDOKU_MAX, OPTION_COUNT_CACHE


class SudokuEmpty:
    def __init__(self):
        self.data = list(range(81))
        self.pos = 81

    def remove(self, index):
        self.pos -= 1
        data = self.data
        data[index], data[self.pos] = data[self.pos], data[index]


class Solver:
    def __init__(self, sudoku):
        self.to_explore = SudokuEmpty()
        self.options = [SUDOKU_MAX for _ in range(81)]
        for (i, item) in enumerate(sudoku):
            if item != 0:
                self.options[i] = SUDOKU_VALUES[item - 1]
                self.apply_number(i)

    def hidden_singles(self, square):
        options = self.options
        value = options[square]
        options[square] = 0
        row_start = square // 9 * 9
        column_start = square % 9
        box_start = square // 3 % 3 * 3 + square // 27 * 27
        needed = (SUDOKU_MAX
                  - ((options[row_start + 8]
                      | options[row_start + 7]
                      | options[row_start + 6]
                      | options[row_start + 5]
                      | options[row_start + 4]
                      | options[row_start + 3]
                      | options[row_start + 2]
                      | options[row_start + 1]
                      | options[row_start])
                     & (options[column_start + 72]
                        | options[column_start + 63]
                        | options[column_start + 54]
                        | options[column_start + 45]
                        | options[column_start + 36]
                        | options[column_start + 27]
                        | options[column_start + 18]
                        | options[column_start + 9]
                        | options[column_start])
                     & (options[box_start + 20]
                        | options[box_start + 19]
                        | options[box_start + 18]
                        | options[box_start + 11]
                        | options[box_start + 10]
                        | options[box_start + 9]
                        | options[box_start + 2]
                        | options[box_start + 1]
                        | options[box_start])))
        option_count = OPTION_COUNT_CACHE[needed]
        if option_count == 0:
            self.options[square] = value
            return True
        elif option_count == 1:
            if value & needed != 0:
                self.options[square] = value & needed
                return True
            else:
                return False
        else:
            return False

    def apply_number(self, square):
        options = self.options
        value = options[square]
        not_value = SUDOKU_MAX - value
        column_start = square % 9
        row_start = square - column_start
        box_start = square // 3 % 3 * 3 + square // 27 * 27
        options[row_start + 8] &= not_value
        options[row_start + 7] &= not_value
        options[row_start + 6] &= not_value
        options[row_start + 5] &= not_value
        options[row_start + 4] &= not_value
        options[row_start + 3] &= not_value
        options[row_start + 2] &= not_value
        options[row_start + 1] &= not_value
        options[row_start] &= not_value

        options[column_start + 72] &= not_value
        options[column_start + 63] &= not_value
        options[column_start + 54] &= not_value
        options[column_start + 45] &= not_value
        options[column_start + 36] &= not_value
        options[column_start + 27] &= not_value
        options[column_start + 18] &= not_value
        options[column_start + 9] &= not_value
        options[column_start] &= not_value

        options[box_start + 20] &= not_value
        options[box_start + 19] &= not_value
        options[box_start + 18] &= not_value
        options[box_start + 11] &= not_value
        options[box_start + 10] &= not_value
        options[box_start + 9] &= not_value
        options[box_start + 2] &= not_value
        options[box_start + 1] &= not_value
        options[box_start] &= not_value
        options[square] = value

    def process(self, routes):
        values = []
        while 1:
            min_length = 20
            min_pos = 0
            min_pos_x = 0
            x = 0
            while x < self.to_explore.pos:
                pos = self.to_explore.data[x]
                if not self.hidden_singles(pos):
                    return False
                option = self.options[pos]
                length = OPTION_COUNT_CACHE[option]
                if length < min_length:
                    if length == 0:
                        return False
                    elif length == 1:
                        for (i, item) in enumerate(SUDOKU_VALUES):
                            if option == item:
                                self.apply_number(pos)
                                self.to_explore.remove(x)
                                break
                    else:
                        min_length = length
                        min_pos = pos
                        min_pos_x = x
                        x += 1

                else:
                    x += 1

            if min_length != 20:
                values.clear()
                options = self.options[min_pos]
                for (i, item) in enumerate(SUDOKU_VALUES):
                    if options & item != 0:
                        values.append(i + 1)
                if not values:
                    return False

                self.to_explore.remove(min_pos_x)
                item = values.pop()
                for value in values:
                    clone = copy.deepcopy(self)
                    clone.options[min_pos] = SUDOKU_VALUES[value - 1]
                    clone.apply_number(min_pos)
                    routes.append(clone)
                self.options[min_pos] = SUDOKU_VALUES[item - 1]
                self.apply_number(min_pos)
            else:
                return True

    def get_result(self):
        solution = [0 for _ in range(81)]
        for (i, option) in enumerate(self.options):
            for (x, value) in enumerate(SUDOKU_VALUES):
                if option == value:
                    solution[i] = x + 1
                    break
        return solution


def solve(sudoku):
    routes = [Solver(sudoku)]
    while routes:
        route = routes.pop()
        result = route.process(routes)
        if result:
            return route.get_result()
    raise Exception("Empty routes, but still unsolved")
