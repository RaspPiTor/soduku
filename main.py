from tkinter import filedialog
from tkinter import messagebox
import tkinter.ttk as ttk
import tkinter

import json

import lib


class GUI(ttk.Frame):
    def __init__(self, master=None):
        ttk.Frame.__init__(self, master)
        self.squares = []
        for row, column in ((3, 3), (7, 8)):
            ttk.Label(self, text=' ').grid(row=row)
            ttk.Label(self, text=' ').grid(column=column)
        for x in [0, 1, 2, 4, 5, 6, 8, 9, 10]:
            for y in [0, 1, 2, 5, 6, 7, 9, 10, 11]:
                square = ttk.Entry(self, width=2)
                square.grid(row=x, column=y)
                self.squares.append(square)
        clear = ttk.Button(self, text='Clear', command=self.clear)
        clear.grid(row=12, column=0, columnspan=6, sticky='nesw')

        solve = ttk.Button(self, text='Solve', command=self.solve)
        solve.grid(column=12, row=0, rowspan=2, columnspan=10, sticky='nesw')

        solve = ttk.Button(self, text='Open', command=self.open)
        solve.grid(column=12, row=6, rowspan=2, columnspan=10, sticky='nesw')
        save = ttk.Button(self, text='Save', command=self.save)
        save.grid(column=12, row=8, rowspan=2, columnspan=10, sticky='nesw')

    def clean(self):
        for square in self.squares:
            n = square.get()
            if n:
                if not n.isnumeric():
                    square.delete(0, 'end')
                elif int(n) not in [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]:
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
        self.display(lib.solve(self.load()))

    def display(self, sudoku):
        for i, square in enumerate(self.squares):
            square.delete(0, 'end')
            if sudoku[i]:
                square.insert(0, str(sudoku[i]))

    def clear(self):
        self.display([0 for _ in range(81)])

    def open(self):
        path = filedialog.askopenfilename(filetypes=[("JSON", "*.json")])
        if path:
            try:
                with open(path) as file:
                    data = json.load(file)
                    if len(data) == 81 and isinstance(data, (list, tuple)):
                        if all(i in range(10) for i in data):
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
        filetypes = [("JSON", "*.json")]
        try:
            with filedialog.asksaveasfile(filetypes=filetypes) as file:
                json.dump(self.load(), file)
        except AttributeError:
            pass


if __name__ == '__main__':
    gui = GUI()
    gui.grid()
    gui.mainloop()
