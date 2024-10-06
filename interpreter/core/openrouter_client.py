import requests
import os
from typing import List, Dict, Any

class OpenRouterClient:
    BASE_URL = "https://openrouter.ai/api/v1"

    def __init__(self):
        self.api_key = os.environ.get("OPENROUTER_API_KEY")

    def set_api_key(self, api_key: str):
        self.api_key = api_key

    def _make_request(self, endpoint: str, method: str = "GET", data: Dict[str, Any] = None) -> Dict[str, Any]:
        if not self.api_key:
            raise ValueError("API key is not set. Use set_api_key() method to set it.")

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        url = f"{self.BASE_URL}{endpoint}"
        
        if method == "GET":
            response = requests.get(url, headers=headers)
        elif method == "POST":
            response = requests.post(url, json=data, headers=headers)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")
        
        response.raise_for_status()
        return response.json()

    def get_available_models(self) -> List[str]:
        if not self.api_key:
            return ["API key not set. Available models cannot be retrieved."]
        try:
            response = self._make_request("/models")
            return [model['id'] for model in response['data']]
        except Exception as e:
            print(f"Error fetching available models: {str(e)}")
            return []

    def chat_completion(self, messages: List[Dict[str, str]], model: str) -> Dict[str, Any]:
        data = {
            "model": model,
            "messages": messages
        }
        return self._make_request("/chat/completions", method="POST", data=data)

    def text_completion(self, prompt: str, model: str) -> Dict[str, Any]:
        data = {
            "model": model,
            "prompt": prompt
        }
        return self._make_request("/completions", method="POST", data=data)

# Example usage:
# client = OpenRouterClient()
# client.set_api_key("your-api-key-here")
# available_models = client.get_available_models()
# chat_response = client.chat_completion([{"role": "user", "content": "Hello, how are you?"}], "openai/gpt-3.5-turbo")
# text_response = client.text_completion("Once upon a time", "openai/gpt-3.5-turbo")