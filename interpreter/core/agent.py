```python
# /root/open/interpreter/core/agent.py

class Agent:
    def __init__(self, name, description='', prompt='', ai_model='', skills=None, parent=None):
        """
        Initialize a new Agent instance.

        :param name: Unique identifier for the agent.
        :param description: Brief description of the agent.
        :param prompt: Default prompt or instructions for the agent.
        :param ai_model: AI model assigned to the agent.
        :param skills: List of skills the agent possesses.
        :param parent: Reference to the parent agent, if any.
        """
        self.id = None  # Will be set when saved to the database
        self.name = name
        self.description = description
        self.prompt = prompt
        self.ai_model = ai_model
        self.skills = skills if skills else []
        self.parent = parent
        self.sub_agents = []
        self.state = {}
        self.parameters = {}

    def add_skill(self, skill):
        """
        Add a skill to the agent.

        :param skill: The skill to be added.
        """
        self.skills.append(skill)

    def remove_skill(self, skill):
        """
        Remove a skill from the agent.

        :param skill: The skill to be removed.
        """
        if skill in self.skills:
            self.skills.remove(skill)

    def add_sub_agent(self, agent):
        """
        Add a sub-agent under this agent.

        :param agent: The agent to be added as a sub-agent.
        """
        agent.parent = self
        self.sub_agents.append(agent)

    def perceive(self, environment):
        """
        Perceive the environment and update internal state.

        :param environment: The environment to perceive.
        """
        # Implement perception logic here
        pass

    def act(self):
        """
        Perform actions based on current state and skills.
        """
        # Implement action logic here
        pass

    def evaluate(self):
        """
        Evaluate performance and adjust strategies.
        """
        # Implement self-evaluation logic here
        pass

    def to_dict(self):
        """
        Serialize the agent to a dictionary for JSON responses or database storage.

        :return: A dictionary representation of the agent.
        """
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'prompt': self.prompt,
            'ai_model': self.ai_model,
            'skills': self.skills,
            'parent': self.parent.id if self.parent else None,
            'sub_agents': [agent.id for agent in self.sub_agents],
            'state': self.state,
            'parameters': self.parameters
        }

    @classmethod
    def from_dict(cls, data):
        """
        Create an Agent instance from a dictionary.

        :param data: A dictionary containing agent data.
        :return: An Agent instance.
        """
        agent = cls(
            name=data.get('name'),
            description=data.get('description', ''),
            prompt=data.get('prompt', ''),
            ai_model=data.get('ai_model', ''),
            skills=data.get('skills', []),
            parent=None  # Parent assignment can be handled separately if needed
        )
        agent.id = data.get('id')
        agent.state = data.get('state', {})
        agent.parameters = data.get('parameters', {})
        return agent

    def __repr__(self):
        return f"Agent(id={self.id}, name={self.name})"
```