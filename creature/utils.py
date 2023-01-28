import greenlet


def print_stack():
    # DEBUG: Print the stacktrace of the sync greenlet.
    frame = greenlet.getcurrent().sync_greenlet.gr_frame
    while frame:
        print(frame)
        frame = frame.f_back
