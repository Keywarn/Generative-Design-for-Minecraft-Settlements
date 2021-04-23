from collections import namedtuple

Info = namedtuple('Info', 'start height')

# returns height, width, and position of the top left corner of the largest
#  rectangle with the given value in mat
def max_size(mat, value=0):
    it = iter(mat)
    hist = [(el==value) for el in next(it, [])]
    max_size_start, start_row = max_rectangle_size(hist), 0
    for i, row in enumerate(it):
        hist = [(1+h) if el == value else 0 for h, el in zip(hist, row)]
        mss = max_rectangle_size(hist)
        if area(mss) > area(max_size_start):
            max_size_start, start_row = mss, i+2-mss[0]
    return max_size_start[:2], [max_size_start[2],start_row]

# returns height, width, and start column of the largest rectangle that
#  fits entirely under the histogram
def max_rectangle_size(histogram):
    stack = []
    top = lambda: stack[-1]
    max_size_start = (0, 0, 0) # height, width, start of the largest rectangle
    pos = 0 # current position in the histogram
    for pos, height in enumerate(histogram):
        start = pos # position where rectangle starts
        while True:
            if not stack or height > top().height:
                stack.append(Info(start, height)) # push
            elif stack and height < top().height:
                max_size_start = max(
                    max_size_start,
                    (top().height, pos - top().start, top().start),
                    key=area)
                start, _ = stack.pop()
                continue
            break # height == top().height goes here

    pos += 1
    for start, height in stack:
        max_size_start = max(max_size_start, (height, pos - start, start),
            key=area)

    return max_size_start

def area(size): return size[0]*size[1]