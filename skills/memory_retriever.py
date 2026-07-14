
def run(args):
    import json
    import os

    log_file = evolutionary_logs.json
    if not os.path.exists(log_file):
        return []
    \n    with open(log_file, r) as f:
        try:
            data = json.load(f)
            return data
        except json.JSONDecodeError:
            return []