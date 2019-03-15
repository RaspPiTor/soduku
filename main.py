import itertools
import tkinter.ttk as ttk
import tkinter

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
        options = [[x] for x in self.square_options(0)]
        for i in range(1, 81):
            new = []
            for option in options:
                self.data[:len(option)] = option
                square_options = self.square_options(i)
                if square_options:
                    for x in square_options:
                        new.append(option + [x])
            print(i, len(new))
            options = new
        if len(options) == 1:
            self.data = options[0]
        return len(options)

class GUI(ttk.Frame):
    def __init__(self, master=None):
        ttk.Frame.__init__(self, master)
        self.soduku = Soduku()
        self.squares = []
        for i in [3,7]:
            ttk.Label(self, text=' ').grid(row=i)
            ttk.Label(self, text=' ').grid(column=i)
        for x in [0,1,2,4,5,6,8,9,10]:
            for y in [0,1,2,4,5,6,8,9,10]:
                square = ttk.Entry(self, width=2)
                square.grid(row=x, column=y)
                self.squares.append(square)
        verify = ttk.Button(self, text='Verify', command=self.verify)
        verify.grid(row=11, columnspan=10)
        solve = ttk.Button(self, text='Solve', command=self.solve)
        solve.grid(row=12, columnspan=10)
        self.refresh()
    def refresh(self):
        for square in self.squares:
            n = square.get()
            if n:
                if not n.isnumeric():
                    square.delete(0, 'end')
                elif int(n) not in [0,1,2,3,4,5,6,7,8,9]:
                    square.delete(0, 'end')
        self.after(10, self.refresh)
    def verify(self):
        self.refresh()
        for i, square in enumerate(self.squares):
            n = square.get()
            if n:
                self.soduku.data[i] = int(n)
            else:
                self.soduku.data[i]= None
        valid = self.soduku.is_valid()
        print(valid)
    def solve(self):
        self.verify()
        result = self.soduku.solve()
        for i, square in enumerate(self.squares):
            square.delete(0, 'end')
            square.insert(0, str(self.soduku.data[i]))
        print(result)
            
        



if __name__ == '__main__':
    gui = GUI()
    gui.grid()
    gui.mainloop()
