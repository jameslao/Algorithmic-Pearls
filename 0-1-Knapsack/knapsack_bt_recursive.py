# 0-1 Knapsack backtracking, recursive
# By James Lao

import time
import sys
import threading


def knapsack(vw, limit):

    def bound(v, w, j):
        if j >= len(vw) or w > limit:
            return -1
        else:
            while j < len(vw) and w + vw[j][1] <= limit:
                v, w, j = v + vw[j][0], w + vw[j][1], j + 1
            if j < len(vw):
                v += (limit - w) * vw[j][0] / (vw[j][1] * 1.0)
            return v

    def traverse(v, w, j):
        nonlocal maxValue
        # print(v,w,j, bound(v,w,j))
        if bound(v, w, j) >= maxValue:  # promising w/ j
            if w + vw[j][1] <= limit:
                maxValue = max(maxValue, v + vw[j][0])
                traverse(v + vw[j][0], w + vw[j][1], j + 1)
            if j < len(vw) - 1:  # promising w/o j
                traverse(v, w, j + 1)
        return

    maxValue = 0
    traverse(0, 0, 0)
    return maxValue


def main():
    with open(sys.argv[1] if len(sys.argv) > 1 else sys.exit(1)) as f:
        limit, n = map(int, f.readline().split())
        vw = []                   # value, weight, value density
        for ln in f.readlines():
            vl, wl = tuple(map(int, ln.split()))
            vw.append([vl, wl, vl / (wl * 1.0)])

    start = time.time()
    A = knapsack(sorted(vw, key=lambda x: x[2], reverse=True), limit)
    end = time.time()
    print(A)
    print(end - start)


if __name__ == "__main__":
    threading.stack_size(67108864)  # 64MB stack
    sys.setrecursionlimit(20000)
    thread = threading.Thread(target=main)
    thread.start()
