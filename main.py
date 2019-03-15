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
        print(self.boxes)
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
        valid = []
        for i in range(10):
            self.data[square] = i
            if self.is_valid():
                valid.append(i)
        self.data[square] = None
        return valid
    def solve(self):
        options = []
        for i in range(81):
            options.append(self.square_options(i))
        total = 1
        for i in options:
            total *= len(i)
        current = []
        print(total, options)

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
        self.soduku.solve()
            
        



if __name__ == '__main__':
    gui = GUI()
    gui.grid()
    gui.mainloop()
