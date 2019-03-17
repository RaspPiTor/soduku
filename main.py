import itertools
from tkinter import filedialog
from tkinter import messagebox
import tkinter.ttk as ttk
import tkinter
import time
import json

class Sudoku():
    def __init__(self):
        self.data = [None for _ in range(81)]

    def square_options(self, square, options=set(range(1,10))):
        data = self.data
        if data[square] is not None:
            return [data[square]]
        start = square // 27 * 27 + square // 3 % 3 * 3
        exclude = set(data[start: start + 3] # Box 1st layer
                      + data[start + 9: start + 12] # Box 2nd layer
                      + data[start + 18: start + 21] # Box 3rd layer
                      + data[square % 9: 81: 9] # Columns
                      + data[square // 9 * 9: square // 9 * 9 + 9] # Rows
                      )
        return options.difference(exclude)

    def solve(self):
        import cProfile
        run = cProfile.Profile()
        run.enable()
        old = self.data.copy()
        options = [[None] * len(self.data)]
        start = time.time()
        for round_number in range(81):
            new = []
            for option in options:
                to_explore = []
                for i, value in enumerate(option):
                    if value is not None:
                        self.data[i] = value
                    else:
                        self.data[i] = old[i]
                        to_explore.append(i)
                ops = tuple(zip(to_explore, map(self.square_options, to_explore)))
                pos, values = min(ops, key=lambda x: len(x[1]))
                if len(values) == 0:
                    continue
                for value in values:
                    next_option = option.copy()
                    next_option[pos] = value
                    new.append(next_option)
                if time.time() - start > 0.1:
                    yield False, 0, round_number, 81
                    start = time.time()
            print('Number:%s Options:%s' % (round_number, len(new)))
            options = new
        if len(options) == 1:
            self.data = options[0]
        yield True, len(options), 81, 81

class GUI(ttk.Frame):
    def __init__(self, master=None):
        ttk.Frame.__init__(self, master)
        self.sudoku  = Sudoku()
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

        self.progress = ttk.Progressbar(self)
        self.progress.grid(column=12, row=4, rowspan=2)

        solve = ttk.Button(self, text='Open', command=self.open)
        solve.grid(column=12, row=6, rowspan=2, columnspan=10, sticky='nesw')
        stop = ttk.Button(self, text='Save', command=self.save)
        stop.grid(column=12, row=8, rowspan=2, columnspan=10, sticky='nesw')
        self.solver = iter(())
        self.refresh()
    def clean(self):
        for square in self.squares:
            n = square.get()
            if n:
                if not n.isnumeric():
                    square.delete(0, 'end')
                elif int(n) not in [0,1,2,3,4,5,6,7,8,9]:
                    square.delete(0, 'end')
    def load(self):
        self.clean()
        for i, square in enumerate(self.squares):
            n = square.get()
            if n:
                self.sudoku.data[i] = int(n)
            else:
                self.sudoku.data[i]= None
    def display(self):
         for i, square in enumerate(self.squares):
            square.delete(0, 'end')
            if self.sudoku.data[i] is not None:
                square.insert(0, str(self.sudoku.data[i]))
    def refresh(self):
        for square in self.squares:
            n = square.get()
            if n:
                if not n.isnumeric():
                    square.delete(0, 'end')
                elif int(n) not in [0,1,2,3,4,5,6,7,8,9]:
                    square.delete(0, 'end')
        try:
            done, length, value, maximum = next(self.solver)
            self.progress['value'] = value
            self.progress['maximum'] = maximum
            if done:
                if length == 1:
                    self.display()
                else:
                    if length == 0:
                        messagebox.showerror(message='No Solutions')
                    else:
                        messagebox.showerror(message='%s Solutions' % length)
                    self.load()
        except StopIteration:
            pass
        self.after(10, self.refresh)
    def solve(self):
        self.load()
        self.solver = self.sudoku.solve()
    def stop(self):
        self.solver = iter(())
        self.progress['value'] = 0
        self.progress['maximum'] = 1
    def clear(self):
        self.sudoku.data = [None] * len(self.sudoku.data)
        self.display()
    def open(self):
        path = filedialog.askopenfilename(filetypes=[("JSON", "*.json")])
        if path:
            try:
                with open(path) as file:
                    data = json.load(file)
                    if len(data) is 81 and isinstance(data, (list, tuple)):
                        if all(i in [1,2,3,4,5,6,7,8,9,None] for i in data):
                            self.sudoku .data = data
                            self.display()
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
        self.load()
        try:
            with filedialog.asksaveasfile(filetypes=[("JSON", "*.json")]) as file:
                json.dump(self.sudoku.data, file)
        except AttributeError:
            pass


if __name__ == '__main__':
    gui = GUI()
    gui.grid()
    gui.mainloop()
