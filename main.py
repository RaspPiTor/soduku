import itertools
import tkinter.ttk as ttk
import tkinter
import time

class Soduku():
    def __init__(self):
        self.data = [None for _ in range(81)]
        self.rows = [[x + i for i in range(9)] for x in range(0, 81, 9)]
        self.columns = [[x + i for i in range(0, 81, 9)] for x in range(9)]
        self.boxes = []
        for x_offset in range(0, 9, 3):
            for y_offset in range(0, 9, 3):
                box = []
                for row in range(x_offset, x_offset+3):
                    box.extend(self.rows[row][y_offset:y_offset+3])
                self.boxes.append(box)
    def is_valid(self):
        for box in self.boxes:
            for i in set(box):
                n = self.data[i]
                if n is not None:
                    if [self.data[x] for x in box].count(n) > 1:
                        return False
        for row in self.rows:
            for i in set(row):
                n = self.data[i]
                if n is not None:
                    if [self.data[x] for x in row].count(n) > 1:
                        return False
        for columns in self.columns:
            for i in set(columns):
                n = self.data[i]
                if n is not None:
                    if [self.data[x] for x in columns].count(n) > 1:
                        return False
        return True
    def square_options(self, square):
        if self.data[square] is not None:
            return [self.data[square]]
        row = [self.data[x] for x in self.rows[square // 9]]
        column = [self.data[x] for x in self.columns[square % 9]]
        for i in range(9):
            if square in self.boxes[i]:
                box = [self.data[x] for x in self.boxes[i]]
        options = [i for i in range(1, 10) if i not in row and i not in column and i not in box]
        return options
    def solve(self):
        old = self.data.copy()
        for i in range(1, 81):
            now = self.square_options(i)
            if len(now) == 1:
                self.data[i] = now[0]
        options = [[x] for x in self.square_options(0)]
        start = time.time()
        for i in range(1, 81):
            new = []
            for option in options:
                self.data[:len(option)] = option
                square_options = self.square_options(i)
                if square_options:
                    for x in square_options:
                        new.append(option + [x])
                if time.time() - start > 0.1:
                    yield False, 0, i, 81
                    start = time.time()
            print('Number:%s Options:%s' % (i, len(new)))
            options = new
        if len(options) == 1:
            self.data = options[0]
        yield True, len(options), 81, 81

class GUI(ttk.Frame):
    def __init__(self, master=None):
        ttk.Frame.__init__(self, master)
        self.soduku = Soduku()
        self.squares = []
        for row, column in ((3, 3), (7, 8)):
            ttk.Label(self, text=' ').grid(row=row)
            ttk.Label(self, text=' ').grid(column=column)
        for x in [0,1,2,4,5,6,8,9,10]:
            for y in [0,1,2,5,6,7,9,10,11]:
                square = ttk.Entry(self, width=2)
                square.grid(row=x, column=y)
                self.squares.append(square)
        verify = ttk.Button(self, text='Verify', command=self.verify)
        verify.grid(row=12, column=0, columnspan=6, sticky='nesw')
        clear = ttk.Button(self, text='Clear', command=self.clear)
        clear.grid(row=12, column=7, columnspan=5, sticky='nesw')

        solve = ttk.Button(self, text='Solve', command=self.solve)
        solve.grid(column=12, row=0, rowspan=2, columnspan=10, sticky='nesw')
        stop = ttk.Button(self, text='Stop', command=self.stop)
        stop.grid(column=12, row=2, rowspan=2, columnspan=10, sticky='nesw')

        self.progress = ttk.Progressbar(self)
        self.progress.grid(column=12, row=4, rowspan=2)
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
                self.soduku.data[i] = int(n)
            else:
                self.soduku.data[i]= None
    def display(self):
         for i, square in enumerate(self.squares):
            square.delete(0, 'end')
            if self.soduku.data[i] is not None:
                square.insert(0, str(self.soduku.data[i]))
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
                    self.load()
        except StopIteration:
            pass
        self.after(10, self.refresh)
    def verify(self):
        self.load()
        valid = self.soduku.is_valid()
        print(valid)
    def solve(self):
        self.verify()
        self.solver = self.soduku.solve()
    def stop(self):
        self.solver = iter(())
        self.progress['value'] = 0
        self.progress['maximum'] = 1
    def clear(self):
        self.soduku.data = [None] * len(self.soduku.data)
        self.display()





if __name__ == '__main__':
    gui = GUI()
    gui.grid()
    gui.mainloop()
