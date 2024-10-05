import uuid

class Agent:
    def __init__(self, name, description, prompt, ai_model, id=None, feedback=None):
        self.id = id or str(uuid.uuid4())
        self.name = name
        self.description = description
        self.prompt = prompt
        self.ai_model = ai_model
        self.feedback = feedback or []

    def add_feedback(self, feedback_content):
        self.feedback.append({
            'content': feedback_content,
            'timestamp': datetime.now().isoformat()
        })

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'prompt': self.prompt,
            'ai_model': self.ai_model,
            'feedback': self.feedback
        }