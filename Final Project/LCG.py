# from tabulate import tabulate
# import time

# class LCG:
#     def __init__(self, seed, a, c, m):
#         self.seed = seed
#         self.a = a
#         self.c = c
#         self.m = m

#     def randomNumber(self):
#         self.random = self.seed / self.m
#         return self.random

#     def next(self):
#         self.seed = (self.a * self.seed + self.c) % self.m
#         return self.seed

#     def getPriority(self):
#         self.priority = (3 - 1) * self.random + 1
#         return round(self.priority)

# # Prompting user for parameters
# seed = int(input("Enter the seed value: "))
# a = int(input("Enter the 'a' value: "))
# c = int(input("Enter the 'c' value: "))
# m = int(input("Enter the 'm' value: "))
# n = int(input("Enter the Number of iterations needed: "))

# # Creating an LCG instance
# lcg = LCG(seed, a, c, m)

# # Generating data
# table = [["Simulation", "Initial Seed", "LCG(initial Seed)", "Random Number", "Priority"]]
# for i in range(n):
#     temp = []
#     temp.append(i + 1)
#     temp.append(lcg.seed)
#     temp.append(lcg.next())
#     temp.append(lcg.randomNumber())
#     temp.append(lcg.getPriority())
#     table.append(temp)

# # Printing the table
# print(tabulate(table, headers="firstrow", tablefmt="grid"))


# =================================================================================================================================


import tkinter as tk
from tabulate import tabulate


class LCG:
    def __init__(self, seed, a, c, m):
        self.seed = seed
        self.a = a
        self.c = c
        self.m = m

    def randomNumber(self):
        self.random = self.seed / self.m
        return self.random

    def next(self):
        self.seed = (self.a * self.seed + self.c) % self.m
        return self.seed

    def getPriority(self):
        self.priority = (3 - 1) * self.random + 1
        return round(self.priority)


def create_lcg():
    seed = int(seed_entry.get())
    a = int(a_entry.get())
    c = int(c_entry.get())
    m = int(m_entry.get())
    n = int(n_entry.get())

    lcg = LCG(seed, a, c, m)
    table = [["Simulation", "Initial Seed",
              "LCG(initial Seed)", "Random Number", "Priority"]]
    for i in range(n):
        temp = []
        temp.append(i + 1)
        temp.append(lcg.seed)
        temp.append(lcg.next())
        temp.append(lcg.randomNumber())
        temp.append(lcg.getPriority())
        table.append(temp)

    print(tabulate(table, headers="firstrow", tablefmt="grid"))


root = tk.Tk()
root.title("LCG Parameters")
root.geometry("400x300")

tk.Label(root, text="Seed").grid(row=0, padx=20, pady=10)
tk.Label(root, text="a").grid(row=1, padx=20, pady=10)
tk.Label(root, text="c").grid(row=2, padx=20, pady=10)
tk.Label(root, text="m").grid(row=3, padx=20, pady=10)
tk.Label(root, text="n").grid(row=4, padx=20, pady=10)

seed_entry = tk.Entry(root)
a_entry = tk.Entry(root)
c_entry = tk.Entry(root)
m_entry = tk.Entry(root)
n_entry = tk.Entry(root)

seed_entry.grid(row=0, column=1, padx=20, pady=10)
a_entry.grid(row=1, column=1, padx=20, pady=10)
c_entry.grid(row=2, column=1, padx=20, pady=10)
m_entry.grid(row=3, column=1, padx=20, pady=10)
n_entry.grid(row=4, column=1, padx=20, pady=10)


tk.Button(root, text='Submit', command=create_lcg).grid(
    row=5, column=1, sticky=tk.W, pady=20, padx=20)

root.mainloop()
