import greenlet


def print_stack():
    frame = greenlet.getcurrent()._other_greenlet.gr_frame
    while frame:
        print(frame)
        frame = frame.f_back