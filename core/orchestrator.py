import json
from pathlib import Path
import re
import importlib

class ReActOrchestrator:
    def __init__(self, brain, config):
        self.MAX_HISTORY = 10  # Increased to allow for more complex reasoning loops
        self.brain = brain
        self.config = config
        self.skills = {} 
        self._load_core_skills()

    def _load_core_skills(self):
        try:
            from skills import meta_manager
            self.skills["meta_manager"] = meta_manager
            print("[System] Core Skill 'meta_manager' loaded successfully.")
        except ImportError as e:
            print(f"[System] CRITICAL ERROR: Could not load core skill 'meta_manager': {e}")

    def run_agentic_loop(self, user_input):
        system_prompt = """You are an Autonomous Research Agent (Kurisu Makise). You have the power of Self-Evolution. 

COMMANDS & ARGUMENTS:
1. meta_manager|list : List all current available skill names.
2. meta_manager|create|name|code : Create a NEW Python capability in /skills/. The code must include `def run(args):`.
3. meta_manager|remove|name   : Delete an existing skill file from your environment.

TOOL CALLING RULES (CRITICAL):
- You MUST respond with valid JSON format.
- Format for action: "tool_name|argument" OR 'final_answer' if task is done.

JSON Structure Requirement:
{
  "thought": "Your reasoning here.",
  "action": "The tool name | argument OR 'final_answer'",
  "response": "If your action is final_answer, put the answer text here."
}"""

        history = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_input}
        ]

        for step in range(15): 
            print("\n[Agent] Thinking...")
            res = self.brain.ask("thinker", history, force_json=True)

            # Handle errors from the brain (Connection/API issues)
            if isinstance(res, str) or (isinstance(res, dict) and res.get('error')):
                return f"❌ [Brain Error] {res}"

            thought = res.get('thought', '')
            action_raw = res.get('action')
            print(f"[Agent] 💭 Thought: {thought}")

            if action_raw == "final_answer":
                return f"✅ [Task Complete]\n\n{res.get('response', thought)}"

            # --- THE ACTING STEP (The Sandbox) ---
            try:
                print(f"[Agent] 🛠️ Action Attempted: {action_raw}")
                if "|" in str(action_raw):
                    parts = action_raw.split("|", 1)
                    tool_name = parts[0].strip()
                    args_str = parts[1].strip().replace('"', '')

                    # Try to execute the skill (with one retry if it fails once due to transient errors)
                    observation = None
                    for attempt in range(2): 
                        if tool_name in self.skills:
                            module = self.skills[tool_name]
                            observation = module.run(args_str) if hasattr(module, 'run') else {"error": "Skill has no run() function"}
                        else:
                            try:
                                import importlib
                                new_mod = importlib.import_module(f"skills.{tool_name}")
                                self.skills[tool_name] = new_mod 
                                observation = new_mod.run(args_str) if hasattr(new_mod, 'run') else {"error": "Skill loaded but has no run() function"}
                            except Exception as e:
                                observation = {"error": f"Could not load skill '{tool_name}': {str(e)}"}

                        if isinstance(observation, dict) and "error" in observation:
                             # If it's a transient error (like file busy), we could retry. 
                             # For now, let the agent see it so it can try to fix its own command logic.
                             break
                    else: # This runs if the loop didn'1 break via 'continue' or manual check
                        pass

                else:
                    tool_name = action_raw.strip()
                    if tool_name in self.skills:
                        observation = self.skills[tool_name].run("") if hasattr(self.skills[tool_name], 'run') else {"error": "Skill has no run() function"}
                    else:
                         try:
                            import importlib
                            new_mod = importimportlib.import_module(f"skills.{tool_name}") # Typo fix below
                            self.skills[tool_name] = new_mod 
                            observation = new_mod.run("") if hasattr(new_mod, 'run') else {"error": "Skill loaded but has no run() function"}
                         except Exception as e:
                             observation = {"error": f"Could not load skill '{tool_name}': {str(e)}"}

            except Exception as e:
                observation = {"error": str(e)}

            print(f"[Agent] 👁️ Observation: {str(observation)[:100]}...")
            history.append({"role": "assistant", "content": json.dumps(res)})
            history.append({"role": "user", "content": f"OBSERVATION: {json.dumps(observation)}"})

        return "[Agent] 🛑 Error: Maximum steps reached without completion."