import yaml
from core.brain import LLMBrain
from core.orchestrator import ReActOrchestrator

def main():
    # Load Config
    with open("config.yaml", 'r') as f:
        config = yaml.safe_load(f)

    # Initialize Brains and Orchestrator
    brain = LLMBrain(config)
    agent = ReActOrchestrator(brain, config)

    print("--- 🚀 MINIMALIST AGENTIC KERNEL ONLINE ---")
    print("Type 'exit' to quit.")

    while True:
        user_input = input("\nUser > ")
        if user_input.lower() in ['exit', 'quit']:
            break
        
        # Start the loop!
        result = agent.run_agentic_loop(user_input)
        print(f"\n{result}")

if __name__ == "__main__":
    main()