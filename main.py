from tkinter import filedialog
from tkinter import messagebox
import tkinter.ttk as ttk
import tkinter

import multiprocessing
import threading
import queue

import time
import json

class SudokuSpawn(multiprocessing.Process):
    def __init__(self, in_queue, out_queue):
        multiprocessing.Process.__init__(self)
        self.in_queue = in_queue
        self.out_queue = out_queue
        self.data = [0 for _ in range(81)]

    def square_options(self, to_explore):
        options={1, 2, 3, 4, 5, 6, 7, 8, 9}
        min_length = 11
        min_result = 0, options
        data = self.data
        rows = [set(data[i:i + 9]) for i in (0, 9, 18, 27, 36, 45, 54, 63, 72)]
        columns = [set(data[i:81:9]) for i in (0, 1, 2, 3, 4, 5, 6, 7, 8)]
        boxes = [set(data[i:i + 3]
                     + data[i + 9:i + 12]
                     + data[i + 18:i + 21])
                 for i in (0, 3, 6,
                           27, 30, 33,
                           54, 57, 60)
                 ]
        for square in to_explore:
            result = options.difference(rows[square // 9],
                                        columns[square % 9],
                                        boxes[square // 27 * 3
                                              + square // 3 % 3])
            length = len(result)
            if length < min_length:
                if length == 0:
                    return False, (0, set())
                elif length == 1:
                    return True, (square, result)
                else:
                    min_result = square, result
                    min_lenth = length
        return True, min_result
    def run(self):
        in_queue = self.in_queue
        out_queue = self.out_queue
        self.data = in_queue.get()
        while True:
            to_explore = []
            for i, value in enumerate(self.data):
                if not value:
                    to_explore.append(i)
            if not to_explore:
                out_queue.put(self.data.copy())
                self.data = in_queue.get()
                continue
            done, (pos, values) = self.square_options(to_explore)
            if done:
                values = tuple(values)
                for value in values[:-1]:
                    next_option = self.data.copy()
                    next_option[pos] = value
                    out_queue.put(next_option)
                self.data[pos] = values[-1]
            else:
                self.data = in_queue.get()

class SudokuSolver(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.data = [0 for _ in range(81)]
        self.result = multiprocessing.Queue()
        self.to_process = multiprocessing.Queue()
        for _ in range(multiprocessing.cpu_count()):
            process = SudokuSpawn(self.to_process, self.result)
            process.start()
        self.lock = threading.Lock()
        self.solution_lock = threading.Lock()
        self.solution = ()
        self.start_time = 0
    def new(self, sudoku):
        self.lock.acquire()

        self.data = sudoku
        self.solution = ()
        self.start_time = time.time()
        
        self.lock.release()
        
        self.to_process.put(sudoku)

    def refresh(self):
        with self.solution_lock:
            solution = self.solution
        return solution

    def run(self):
        while True:
            result = self.result.get()
            with self.lock:
                data = self.data
            with self.solution_lock:
                solution = self.solution
            if solution:
                continue
            valid = True
            for i, value in enumerate(result):
                if value == data[i] or data[i] == 0:
                    pass
                else:
                    valid = False
                    break
            if valid:
                if 0 not in result:
                    with self.solution_lock:
                        self.solution = result
                        print('Duration: %s' % (time.time() - self.start_time))
                else:
                    self.to_process.put(result)
    def stop(self):
        with self.lock:
            self.data = [None for _ in range(81)]
        with self.solution_lock:
            self.solution = ()

class GUI(ttk.Frame):
    def __init__(self, master=None):
        ttk.Frame.__init__(self, master)
        self.squares = []
        for row, column in ((3, 3), (7, 8)):
            ttk.Label(self, text=' ').grid(row=row)
            ttk.Label(self, text=' ').grid(column=column)
        for x in [0,1,2,4,5,6,8,9,10]:
            for y in [0,1,2,5,6,7,9,10,11]:
                square = ttk.Entry(self, width=2)
                square.grid(row=x, column=y)
                self.squares.append(square)
        clear = ttk.Button(self, text='Clear', command=self.clear)
        clear.grid(row=12, column=0, columnspan=6, sticky='nesw')

        solve = ttk.Button(self, text='Solve', command=self.solve)
        solve.grid(column=12, row=0, rowspan=2, columnspan=10, sticky='nesw')
        stop = ttk.Button(self, text='Stop', command=self.stop)
        stop.grid(column=12, row=2, rowspan=2, columnspan=10, sticky='nesw')

        solve = ttk.Button(self, text='Open', command=self.open)
        solve.grid(column=12, row=6, rowspan=2, columnspan=10, sticky='nesw')
        stop = ttk.Button(self, text='Save', command=self.save)
        stop.grid(column=12, row=8, rowspan=2, columnspan=10, sticky='nesw')
        self.solver = SudokuSolver()
        self.solver.start()
        self.solved = True
        self.refresh()
    def clean(self):
        for square in self.squares:
            n = square.get()
            if n:
                if not n.isnumeric():
                    square.delete(0, 'end')
                elif int(n) not in [0,1,2,3,4,5,6,7,8,9]:
                    square.delete(0, 'end')
        self.solved = True
    def load(self):
        self.clean()
        sudoku = []
        for i, square in enumerate(self.squares):
            n = square.get()
            if n:
                sudoku.append(int(n))
            else:
                sudoku.append(0)
        return sudoku
    def solve(self):
        self.solver.new(self.load())
        self.solved = False
    def display(self, sudoku):
         for i, square in enumerate(self.squares):
            square.delete(0, 'end')
            if sudoku[i]:
                square.insert(0, str(sudoku[i]))
    def refresh(self):
        for square in self.squares:
            n = square.get()
            if n:
                if not n.isnumeric():
                    square.delete(0, 'end')
                elif int(n) not in [1,2,3,4,5,6,7,8,9]:
                    square.delete(0, 'end')
        try:
            if not self.solved:
                result = self.solver.refresh()
                if result:
                    self.display(result)
                    self.solved = True
        except StopIteration:
            pass
        self.after(10, self.refresh)
    def stop(self):
        self.solver.stop()
        self.solved = True
    def clear(self):
        self.stop()
        self.display([0 for _ in range(81)])
        self.solved = True
    def open(self):
        path = filedialog.askopenfilename(filetypes=[("JSON", "*.json")])
        if path:
            try:
                with open(path) as file:
                    data = json.load(file)
                    if len(data) is 81 and isinstance(data, (list, tuple)):
                        if all(i in [0,1,2,3,4,5,6,7,8,9] for i in data):
                            self.solver.stop()
                            self.display(data)
                        else:
                            messagebox.showerror(message='Invalid contents')
                    else:
                        messagebox.showerror(message='Not 81 item list')
            except json.JSONDecodeError:
                messagebox.showerror(message='JSON decode error')
            except UnicodeDecodeError:
                messagebox.showerror(message='Invalid characters')
            except FileNotFoundError:
                messagebox.showerror(message='No such file')
    def save(self):
        try:
            with filedialog.asksaveasfile(filetypes=[("JSON", "*.json")]) as file:
                json.dump(self.load(), file)
        except AttributeError:
            pass


if __name__ == '__main__':
    gui = GUI()
    gui.grid()
    gui.mainloop()
