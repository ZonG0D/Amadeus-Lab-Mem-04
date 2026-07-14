import os
from pathlib import Path

SKILLS_DIR = Path(__file__).parent

def run(args):
    """ 
    Args can be:
      - 'list' (for meta_manager|list)
      - 'create|name|code' (for meta_manager|create|...)
      - 'remove|name' (for meta_manager|remove|...)
    """
    # Split the arguments by pipe. 
    parts = args.split("|")

    if not parts or parts[0].strip() == "":
        return {"error": "No command provided to meta_manager."}

    command = parts[0].strip().lower()

    if command == "list":
        available = []
        for file in SKILLS_DIR.glob("*.py"):
            module_name = file.stem
            # We exclude __init__ and the manager itself from being 'skills' to list
            if module_name not in ["meta_manager", "__init__"]:
                available.append(f"{module_name}")
        return {"skills": available}

    elif command == "create" and len(parts) >= 3:
        try:
            skill_name = parts[1].strip()
            # Re-join everything after the name as code, in case there are more pipes!
            code_content = "|".join(parts[2:]).replace('|', '\n')

            target_path = SKILLS_DIR / f"{skill_name}.py"
            with open(target_path, "w") as f:
                f.write(code_content)
            return {"status": "success", "message": f"Skill '{skill_name}' created."}
        except Exception as e:
            return {"error": str(e)}

    elif command == "remove" and len(parts) >= 2:
        try:
            target = parts[1].strip()
            if target in ['meta_manager', 'orchestrator']:
                return {"error": f"Permission Denied: '{target}' is a core skill."}

            file_to_delete = SKILLS_DIR / f"{target}.py"
            if file_to_delete.exists():
                os.remove(file_to_delete)
                return {"status": "success", "message": f"Skill '{target}' removed."}
            else:
                return {"error": f"File {target}.py not found."}
        except Exception as e:
            return {"error": str(e)}

    else:
        # If the command is unrecognized, return a helpful error to help the agent learn!
        return {"error": f"Unknown meta_manager command '{command}'. Valid: list, create|name|code, remove|name"}

def get_name(): return "meta_manager"