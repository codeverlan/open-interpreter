# /root/open/interpreter/core/agent.py

from interpreter.core.environment import Environment
from interpreter.core.skill import Skill

class Agent:
    def __init__(self, name, description='', prompt='', ai_model='', skills=None, parent=None):
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
        self.environment = None
        self.performance_history = []

    def add_skill(self, skill):
        if isinstance(skill, Skill):
            self.skills.append(skill)
        else:
            raise ValueError("Skill must be an instance of the Skill class")

    def remove_skill(self, skill_name):
        self.skills = [skill for skill in self.skills if skill.name != skill_name]

    def get_skills(self):
        return [{"name": skill.name, "description": skill.description} for skill in self.skills]

    def add_sub_agent(self, agent):
        agent.parent = self
        self.sub_agents.append(agent)

    def set_environment(self, environment):
        self.environment = environment

    def perceive(self):
        if self.environment:
            env_state = self.environment.get_state()
            self.state.update(env_state)
        else:
            raise ValueError("Environment not set for the agent.")

    def act(self):
        if self.environment:
            print(f"Agent {self.name} is acting based on state: {self.state}")
            
            actions_taken = []
            for skill in self.skills:
                result = skill.execute(self, self.environment)
                actions_taken.append(result)
            
            self.performance_history.append(actions_taken)
            return actions_taken
        else:
            raise ValueError("Environment not set for the agent.")

    def evaluate(self):
        if not self.performance_history:
            return "No actions taken yet to evaluate."

        last_actions = self.performance_history[-1]
        evaluation = f"Last actions taken by {self.name}:\n"
        for action in last_actions:
            evaluation += f"- {action}\n"
        
        # Simple evaluation based on maintaining optimal conditions
        env_state = self.environment.get_state()
        temp = env_state.get('temperature', 20)
        humidity = env_state.get('humidity', 50)
        
        if 19 <= temp <= 23 and 40 <= humidity <= 60:
            evaluation += "Performance: Good. Maintaining optimal conditions."
        else:
            evaluation += "Performance: Needs improvement. Conditions are outside optimal range."
        
        return evaluation

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'prompt': self.prompt,
            'ai_model': self.ai_model,
            'skills': self.get_skills(),
            'parent': self.parent.id if self.parent else None,
            'sub_agents': [agent.id for agent in self.sub_agents],
            'state': self.state,
            'parameters': self.parameters
        }

    @classmethod
    def from_dict(cls, data):
        agent = cls(
            name=data.get('name'),
            description=data.get('description', ''),
            prompt=data.get('prompt', ''),
            ai_model=data.get('ai_model', ''),
            skills=None,  # Skills will be added separately
            parent=None  # Parent assignment can be handled separately if needed
        )
        agent.id = data.get('id')
        agent.state = data.get('state', {})
        agent.parameters = data.get('parameters', {})
        return agent

    def __repr__(self):
        return f"Agent(id={self.id}, name={self.name})"