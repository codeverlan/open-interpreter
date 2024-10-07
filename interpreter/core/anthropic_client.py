import os
import anthropic
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class AnthropicClient:
    def __init__(self):
        self.client = anthropic.Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY'))

    def chat_completion(self, messages):
        try:
            response = self.client.completions.create(
                model="claude-2",
                prompt=self._convert_messages_to_prompt(messages),
                max_tokens_to_sample=1000
            )
            return response.completion
        except Exception as e:
            print(f"Error in chat completion: {str(e)}")
            return None

    def _convert_messages_to_prompt(self, messages):
        prompt = ""
        for message in messages:
            if message["role"] == "user":
                prompt += f"\n\nHuman: {message['content']}"
            elif message["role"] == "assistant":
                prompt += f"\n\nAssistant: {message['content']}"
        prompt += "\n\nAssistant:"
        return prompt

    def test_api(self):
        try:
            test_message = [{"role": "user", "content": "Hello, Claude. Please respond with 'API test successful' if you receive this message."}]
            response = self.chat_completion(test_message)
            if response and "API test successful" in response:
                return True, "Anthropic API test successful"
            else:
                return False, f"Unexpected response: {response}"
        except Exception as e:
            return False, f"Error testing Anthropic API: {str(e)}"

anthropic_client = AnthropicClient()

# Example usage:
# response = anthropic_client.chat_completion([
#     {"role": "user", "content": "Hello, how are you?"}
# ])
# print(response)

# Test the API
# success, message = anthropic_client.test_api()
# print(message)