# Dynamic Programming for 0-1 Knapsack with dominance
# By James Lao.
#!/usr/bin/env python3

from collections import deque
import sys
import time
INF = float("inf")


def knapsack(vw, limit, n):
    vw = sorted(vw, key=lambda x: x[1], reverse=True)  # Accelerate
    A = deque([(0, 0)])

    for i in range(0, n):
        B = deque()  # find all possiblities after adding one new item
        for item in A:
            if item[1] + vw[i][1] > limit:  # A is sorted
                break
            B.append((item[0] + vw[i][0], item[1] + vw[i][1]))

        level, merge = -1, deque()  # the bar keeps going up
        while A or B:    # merging the two queues
            ia, ib = A[0][1] if A else INF, B[0][1] if B else INF
            x = A.popleft() if (ia < ib) else B.popleft()
            if x[0] > level:
                merge.append(x)
                level = x[0]
        A = merge
    return A[-1]

if __name__ == "__main__":
    with open(sys.argv[1] if len(sys.argv) > 1 else sys.exit(1)) as f:
        limit, n = map(int, f.readline().split())
        vw = [tuple(map(int, ln.split())) for ln in f.readlines()]

    start = time.time()
    A = knapsack(vw, limit, n)
    end = time.time()

    print("Max value:", A[0])
    print("Total weight:", A[1])
    print(end - start)
