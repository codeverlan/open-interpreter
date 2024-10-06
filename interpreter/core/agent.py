# /root/open/interpreter/core/agent.py

from interpreter.core.environment import Environment
from interpreter.core.skill import Skill
from interpreter.core.openrouter_client import OpenRouterClient

class Agent:
    def __init__(self, name, description='', prompt='', ai_model='openai/gpt-3.5-turbo', skills=None, parent=None):
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
        self.openrouter_client = OpenRouterClient()
        self.capabilities = []  # New attribute for task assignment
        self.current_task = None  # New attribute to track current task
        self.is_lead_agent = False  # New attribute to identify lead agents
        self.managed_agents = []  # New attribute for lead agents to manage other agents

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

    def get_ai_response(self, messages):
        """
        Get an AI-powered response using OpenRouter.
        """
        try:
            response = self.openrouter_client.chat_completion(messages, self.ai_model)
            return response['choices'][0]['message']['content']
        except Exception as e:
            print(f"Error getting AI response: {str(e)}")
            return None

    def process_input(self, user_input):
        """
        Process user input and generate a response using AI.
        """
        messages = [
            {"role": "system", "content": self.prompt},
            {"role": "user", "content": user_input}
        ]
        return self.get_ai_response(messages)

    def add_capability(self, capability):
        """
        Add a new capability to the agent.
        """
        if capability not in self.capabilities:
            self.capabilities.append(capability)

    def remove_capability(self, capability):
        """
        Remove a capability from the agent.
        """
        if capability in self.capabilities:
            self.capabilities.remove(capability)

    def can_handle_task(self, task):
        """
        Check if the agent can handle a given task based on its capabilities.
        """
        required_capabilities = task.get('required_capabilities', [])
        return all(cap in self.capabilities for cap in required_capabilities)

    def assign_task(self, task):
        """
        Assign a task to the agent.
        """
        if self.can_handle_task(task):
            self.current_task = task
            return True
        return False

    def complete_task(self):
        """
        Complete the current task and return the result.
        """
        if self.current_task:
            # Here you would implement the logic to complete the task
            # For now, we'll just return a placeholder result
            result = f"Task '{self.current_task.get('name', 'Unknown')}' completed by {self.name}"
            self.current_task = None
            return result
        return "No task assigned"

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
            'parameters': self.parameters,
            'capabilities': self.capabilities,
            'current_task': self.current_task,
            'is_lead_agent': self.is_lead_agent,
            'managed_agents': [agent.id for agent in self.managed_agents] if self.is_lead_agent else []
        }

    @classmethod
    def from_dict(cls, data):
        agent = cls(
            name=data.get('name'),
            description=data.get('description', ''),
            prompt=data.get('prompt', ''),
            ai_model=data.get('ai_model', 'openai/gpt-3.5-turbo'),
            skills=None,  # Skills will be added separately
            parent=None  # Parent assignment can be handled separately if needed
        )
        agent.id = data.get('id')
        agent.state = data.get('state', {})
        agent.parameters = data.get('parameters', {})
        agent.capabilities = data.get('capabilities', [])
        agent.current_task = data.get('current_task')
        agent.is_lead_agent = data.get('is_lead_agent', False)
        return agent

    def __repr__(self):
        return f"Agent(id={self.id}, name={self.name})"

    # New methods for Lead Agent functionality
    def set_as_lead_agent(self):
        """
        Set this agent as a lead agent.
        """
        self.is_lead_agent = True

    def add_managed_agent(self, agent):
        """
        Add an agent to be managed by the lead agent.
        """
        if self.is_lead_agent:
            self.managed_agents.append(agent)
        else:
            raise ValueError("Only lead agents can manage other agents.")

    def remove_managed_agent(self, agent):
        """
        Remove an agent from being managed by the lead agent.
        """
        if self.is_lead_agent:
            self.managed_agents = [a for a in self.managed_agents if a.id != agent.id]
        else:
            raise ValueError("Only lead agents can manage other agents.")

    def delegate_task(self, task):
        """
        Delegate a task to the most suitable managed agent.
        """
        if not self.is_lead_agent:
            raise ValueError("Only lead agents can delegate tasks.")
        
        for agent in self.managed_agents:
            if agent.can_handle_task(task):
                return agent.assign_task(task)
        return False

    def process_task(self, task):
        """
        Process a task by either handling it directly or delegating to a managed agent.
        """
        if not self.is_lead_agent:
            return self.complete_task() if self.can_handle_task(task) else "Cannot handle this task."
        
        if self.can_handle_task(task):
            return self.complete_task()
        else:
            delegated = self.delegate_task(task)
            if delegated:
                return "Task delegated to a specialized agent."
            else:
                return "No suitable agent found for the task."

    def summarize_results(self, results):
        """
        Summarize the results from multiple agents.
        """
        if not self.is_lead_agent:
            raise ValueError("Only lead agents can summarize results from multiple agents.")
        
        summary = f"Task summary by {self.name}:\n"
        for result in results:
            summary += f"- {result}\n"
        return summary