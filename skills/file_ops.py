import os

def run(path):
    """Reads a file from /home/kurisu/research_inbox/."""
    try:
        # Clean the path (remove quotes if model sends them)
        clean_path = path.strip().strip('"')
        if not os.path.exists(clean_path):
            return {"error": f"Path {clean_path} does not exist."}
        with open(clean_path, 'r') as f:
            content = f.read()
        return {"result": content[:2000]} 
    except Exception as e:
        return {"error": str(e)}

def list_dir(directory="/home/kurisu/research_inbox"):
    """Lists the files in a directory."""
    try:
        files = os.listdir(directory)
        return {"files": files}
    except Exception as e:
        return {"error": str(e)}

def get_name(): return "file_reader" # We'll use this for both reading and listing in the orchestrator logic below