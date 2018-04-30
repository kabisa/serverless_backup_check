
def within_tolerance(current, previous):
    return current <= previous * 1.1 and current >= previous * 0.9
