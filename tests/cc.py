def add(x, y):
    """Returns the sum of x and y."""
    return x + y


# write a function to divide two numbers
def divide(x, y):
    """Returns the result of dividing x by y."""
    if y == 0:
        raise ValueError("Cannot divide by zero.")
    return x / y
