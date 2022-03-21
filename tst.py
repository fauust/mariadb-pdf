import os
import time
import random


def reprint(lines):
    os.system("cls")
    if type(lines) in [str, int]:
        print(lines)
    else:
        print("\n".join(i for i in lines))
# lines = ["Hi", "Bye", "Cry", "asdasd"]
# print("\n"*20)
# for i in range(20):
#     a = random.randint(0, len(lines)-1)
#     b = random.randint(0, len(lines)-1)
#     lines[a], lines[b] = lines[b], lines[a]
#     reprint(lines)
#     time.sleep(1)


class Informer:
    def __init__(self, arr = None):
        if arr is None: self.arr = []
        else: self.arr = arr

    def print(self):
        os.system("cls")
        print("\n".join(str(i) for i in self.arr), end="")



informer = Informer([1, 2, 3])
informer.print()
