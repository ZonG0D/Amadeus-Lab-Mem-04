import requests
import json
import re
import time # Added for sleep/retries

class LLMBrain:
    def __init__(self, config):
        self.config = config
        # We define how many times we retry on connection errors before giving up
        self.max_retries = 2
        # Timeout in seconds (Connect timeout, Read timeout)
        self.timeout_settings = (5, 60) # Wait 5s to connect, 60s for the model to think

    def ask(self, model_type, messages, force_json=False):
        target = self.config['models'][model_type]
        payload = {
            "model": target['name'],
            "messages": messages,
            "stream": False
        }

        attempt = 0
        while attempt <= self.max_retries:
            try:
                response = requests.post(target['url'], json=payload, timeout=self.timeout_settings)
                
                # If it's a client error (4xx), don't retry; the request itself is wrong.
                if 400 <= response.status_code < 500:
                    return {"error": f"Ollama Client Error ({response.status_code}): {response.text}"}
                
                # If it's a server error (5xx), retry! It might be the GPU/Service restarting.
                if response.status_code >= 500:
                    raise requests.exceptions.ConnectionError("Ollama Server Error")

                data = response.json()

                if not data or 'message' not in data:
                    return {"error": "Empty response from Ollama."}

                content = data['message'].get('content', "").strip()
                thought = data['message'].get('thinking', "")

                # If content is empty, check if it put everything into a thinking block
                if not content and thought:
                    content = thought

                return self._parse_robustly(content, thought)

            except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
                attempt += 1
                print(f"[Brain] Connection attempt {attempt} failed... retrying in 2s...")
                if attempt > self.max_retries:
                    return {"error": f"Failed after {self.max_retries} attempts: {str(e)}"}
                time.sleep(2) # Wait before trying again

            except Exception as e:
                return {"error": str(e)}

    def _parse_robustly(self, content, thought):
        """Extracts JSON using non-greedy regex and handles messy text/thinking blocks."""
        if isinstance(content, dict): return content
        
        # If the model is empty but provided a thinking block (common in reasoning models)
        if not content.strip() and thought:
            return {"thought": thought}

        try:
            parsed = json.loads(content)
            if isinstance(parsed, dict): return parsed
            else: return {"thought": str(parsed), "action": "final_answer", "response": str(parsed)}
        except json.JSONDecodeError:
            pass

        # Regex for finding the JSON block in a messy response (handles thinking blocks)
        match = re.search(r'(\{.*\})', content, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(1))
            except Exception:
                pass

        # Fallback for raw text responses (no JSON found at all)
        if content.strip():
            return {"thought": thought if thought else "No reasoning provided.", "response": content}
        else:
            return {"error": "Model returned no usable response."}