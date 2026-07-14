import os

def run(args):
    try:
        # If args is passed as a string, use it as the path.
        path = str(args)
        return str(os.listdir(path))
    except Exception as e:
        return str(e)