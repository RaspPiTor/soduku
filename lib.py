import copy

SUDOKU_VALUES = [1, 2, 4, 8, 16, 32, 64, 128, 256]
SUDOKU_MAX = 511
OPTION_COUNT_CACHE = [
    0, 1, 1, 2, 1, 2, 2, 3, 1, 2, 2, 3, 2, 3, 3, 4, 1, 2, 2, 3, 2, 3, 3, 4, 2,
    3, 3, 4, 3, 4, 4, 5, 1, 2, 2, 3, 2, 3, 3, 4, 2, 3, 3, 4, 3, 4, 4, 5, 2, 3,
    3, 4, 3, 4, 4, 5, 3, 4, 4, 5, 4, 5, 5, 6, 1, 2, 2, 3, 2, 3, 3, 4, 2, 3, 3,
    4, 3, 4, 4, 5, 2, 3, 3, 4, 3, 4, 4, 5, 3, 4, 4, 5, 4, 5, 5, 6, 2, 3, 3, 4,
    3, 4, 4, 5, 3, 4, 4, 5, 4, 5, 5, 6, 3, 4, 4, 5, 4, 5, 5, 6, 4, 5, 5, 6, 5,
    6, 6, 7, 1, 2, 2, 3, 2, 3, 3, 4, 2, 3, 3, 4, 3, 4, 4, 5, 2, 3, 3, 4, 3, 4,
    4, 5, 3, 4, 4, 5, 4, 5, 5, 6, 2, 3, 3, 4, 3, 4, 4, 5, 3, 4, 4, 5, 4, 5, 5,
    6, 3, 4, 4, 5, 4, 5, 5, 6, 4, 5, 5, 6, 5, 6, 6, 7, 2, 3, 3, 4, 3, 4, 4, 5,
    3, 4, 4, 5, 4, 5, 5, 6, 3, 4, 4, 5, 4, 5, 5, 6, 4, 5, 5, 6, 5, 6, 6, 7, 3,
    4, 4, 5, 4, 5, 5, 6, 4, 5, 5, 6, 5, 6, 6, 7, 4, 5, 5, 6, 5, 6, 6, 7, 5, 6,
    6, 7, 6, 7, 7, 8, 1, 2, 2, 3, 2, 3, 3, 4, 2, 3, 3, 4, 3, 4, 4, 5, 2, 3, 3,
    4, 3, 4, 4, 5, 3, 4, 4, 5, 4, 5, 5, 6, 2, 3, 3, 4, 3, 4, 4, 5, 3, 4, 4, 5,
    4, 5, 5, 6, 3, 4, 4, 5, 4, 5, 5, 6, 4, 5, 5, 6, 5, 6, 6, 7, 2, 3, 3, 4, 3,
    4, 4, 5, 3, 4, 4, 5, 4, 5, 5, 6, 3, 4, 4, 5, 4, 5, 5, 6, 4, 5, 5, 6, 5, 6,
    6, 7, 3, 4, 4, 5, 4, 5, 5, 6, 4, 5, 5, 6, 5, 6, 6, 7, 4, 5, 5, 6, 5, 6, 6,
    7, 5, 6, 6, 7, 6, 7, 7, 8, 2, 3, 3, 4, 3, 4, 4, 5, 3, 4, 4, 5, 4, 5, 5, 6,
    3, 4, 4, 5, 4, 5, 5, 6, 4, 5, 5, 6, 5, 6, 6, 7, 3, 4, 4, 5, 4, 5, 5, 6, 4,
    5, 5, 6, 5, 6, 6, 7, 4, 5, 5, 6, 5, 6, 6, 7, 5, 6, 6, 7, 6, 7, 7, 8, 3, 4,
    4, 5, 4, 5, 5, 6, 4, 5, 5, 6, 5, 6, 6, 7, 4, 5, 5, 6, 5, 6, 6, 7, 5, 6, 6,
    7, 6, 7, 7, 8, 4, 5, 5, 6, 5, 6, 6, 7, 5, 6, 6, 7, 6, 7, 7, 8, 5, 6, 6, 7,
    6, 7, 7, 8, 6, 7, 7, 8, 7, 8, 8, 9
    ] # Basically just .count_ones()


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

    def scan(self):
        def generate_masks_from_intersections(isec, only):
            only[0] |= isec[0] & (SUDOKU_MAX - ((isec[1] | isec[2]) & (isec[3] | isec[6])))
            only[1] |= isec[1] & (SUDOKU_MAX - ((isec[0] | isec[2]) & (isec[4] | isec[7])))
            only[2] |= isec[2] & (SUDOKU_MAX - ((isec[0] | isec[1]) & (isec[5] | isec[8])))

            only[3] |= isec[3] & (SUDOKU_MAX - ((isec[4] | isec[5]) & (isec[0] | isec[6])))
            only[4] |= isec[4] & (SUDOKU_MAX - ((isec[3] | isec[5]) & (isec[1] | isec[7])))
            only[5] |= isec[5] & (SUDOKU_MAX - ((isec[3] | isec[4]) & (isec[2] | isec[8])))

            only[6] |= isec[6] & (SUDOKU_MAX - ((isec[7] | isec[8]) & (isec[0] | isec[3])))
            only[7] |= isec[7] & (SUDOKU_MAX - ((isec[6] | isec[8]) & (isec[1] | isec[4])))
            only[8] |= isec[8] & (SUDOKU_MAX - ((isec[6] | isec[7]) & (isec[2] | isec[5])))
            resultant_mask = [
                SUDOKU_MAX - (only[1] | only[2] | only[3] | only[6]),
                SUDOKU_MAX - (only[0] | only[2] | only[4] | only[7]),
                SUDOKU_MAX - (only[0] | only[1] | only[5] | only[8]),
                SUDOKU_MAX - (only[0] | only[4] | only[5] | only[6]),
                SUDOKU_MAX - (only[1] | only[3] | only[5] | only[7]),
                SUDOKU_MAX - (only[2] | only[3] | only[4] | only[8]),
                SUDOKU_MAX - (only[0] | only[3] | only[7] | only[8]),
                SUDOKU_MAX - (only[1] | only[4] | only[6] | only[8]),
                SUDOKU_MAX - (only[2] | only[5] | only[6] | only[7])]
            return (resultant_mask, only)
        sudoku = self.options
        sudoku_check = SUDOKU_MAX
        for floor_number in (x * 27 for x in range(3)):
            only = [0] * 9
            intersections = [0] * 9
            for i in range(9):
                intersections[i] = (sudoku[floor_number + i * 3]
                    | sudoku[floor_number + i * 3 + 1]
                    | sudoku[floor_number + i * 3 + 2])
                only[i] = intersections[i] * (OPTION_COUNT_CACHE[intersections[i]] <= 3)
            (resultant_mask, only) = generate_masks_from_intersections(intersections, only.copy())

            temp_total = 0
            for (i, (row, only_row)) in enumerate(zip(resultant_mask, only)):
                temp_total |= row
                row = row & [SUDOKU_MAX, only_row][(OPTION_COUNT_CACHE[only_row] == 3)]
                sudoku[floor_number + i * 3] &= row
                sudoku[floor_number + i * 3 + 1] &= row
                sudoku[floor_number + i * 3 + 2] &= row

                sudoku_check *= OPTION_COUNT_CACHE[only_row] <= 3
            sudoku_check &= temp_total
        if sudoku_check != SUDOKU_MAX:
            return False
        for tower_number in (x * 3 for x in range(3)):
            only = [0] * 9
            intersections = [0] * 9
            for column in range(3):
                for layer in range(3):
                    i = column * 3 + layer
                    intersections[i] = (sudoku[tower_number + layer * 27 + column]
                        | sudoku[tower_number + layer * 27 + column + 9]
                        | sudoku[tower_number + layer * 27 + column + 18])
                    only[i] = intersections[i] * (OPTION_COUNT_CACHE[intersections[i]] <= 3)
            (resultant_mask, only) = generate_masks_from_intersections(intersections, only.copy())

            temp_total = 0

            for column_number in range(3):
                for layer in range(3):
                    i = column_number * 3 + layer
                    column = resultant_mask[i]
                    only_column = only[i]
                    temp_total |= column
                    column = column & [SUDOKU_MAX, only_column][(OPTION_COUNT_CACHE[only_column] == 3)]
                    sudoku[tower_number + layer * 27 + column_number] &= column
                    sudoku[tower_number + layer * 27 + column_number + 9] &= column
                    sudoku[tower_number + layer * 27 + column_number + 18] &= column

                    sudoku_check *= OPTION_COUNT_CACHE[only_column] <= 3
            sudoku_check &= temp_total

        self.options = sudoku
        return sudoku_check == SUDOKU_MAX

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
            if not self.scan():
                return False
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
