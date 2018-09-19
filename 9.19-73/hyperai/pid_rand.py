import os
import random
import argparse
from multiprocessing import pool, Process


def exec_sh(temp):
    os.system(temp)


def li(temp):
    if temp < 10:
        temp = 10
    for i in range(temp):
        exec_sh("sleep 1")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="")
    parser.add_argument("-a", "--args", help='')

    args = vars(parser.parse_args())

    rand_num = random.randint(1, 20)

    p = Process(target=li, args=(30,))
    p.start()
    # p.join()

    for i in range(rand_num):
        exec_sh('sleep 0.02')

    exec_sh(args['args'])

