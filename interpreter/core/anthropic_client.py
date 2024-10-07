import os
import anthropic
from functools import lru_cache
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class AnthropicClient:
    def __init__(self):
        self.client = anthropic.Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))

    @lru_cache(maxsize=100)
    def chat_completion(self, messages):
        try:
            response = self.client.messages.create(
                model="claude-2",
                messages=messages,
                max_tokens=1000
            )
            return response.content
        except Exception as e:
            print(f"Error in chat completion: {str(e)}")
            return None

anthropic_client = AnthropicClient()

# Example usage:
# response = anthropic_client.chat_completion([
#     {"role": "user", "content": "Hello, how are you?"}
# ])
# print(response)