
def run(args):
    import json
    import os
    from datetime import datetime

    log_file = evolutionary_logs.json
    entry = args['entry'] # Expected: {'type': 'success'
'avoid'
'error', 'content': str}
    if 'timestamp' not in entry:
        entry['timestamp'] = datetime.now().isoformat()

    logs = []
    if os.path.exists(log_file):
        with open(log_file, r) as f:
            try:
                logs = json.load(f)
            except json.JSONDecodeError:
                logs = []

    logs.append(entry)
    with open(log_file, w) as f:
        json.dump(logs, f, indent=4)

    return fLogged {entry['type']}.