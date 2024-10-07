from typing import List, Dict
import json
import time

class Agent:
    def __init__(self, name: str, description: str = '', prompt: str = '', ai_model: str = 'openai/gpt-3.5-turbo', skills: List = None, parent=None):
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
        self.capabilities = []
        self.current_task = None
        self.role = 'general'
        self.managed_agents = []
        self.knowledge_base = {}
        self.persistent_knowledge_base = {}
        self.task_history = []
        self.user_feedback = []
        self.preferences = {}
        self.self_critiques = []
        self.agent_evaluations = {}

    def set_role(self, role: str):
        if role in ['lead', 'general', 'specialized']:
            self.role = role
        else:
            raise ValueError("Invalid role. Must be 'lead', 'general', or 'specialized'.")

    def add_managed_agent(self, agent):
        if self.role == 'lead':
            self.managed_agents.append(agent)
        else:
            raise ValueError("Only lead agents can manage other agents.")

    def remove_managed_agent(self, agent):
        if self.role == 'lead':
            self.managed_agents = [a for a in self.managed_agents if a.id != agent.id]
        else:
            raise ValueError("Only lead agents can manage other agents.")

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

    def add_capability(self, capability):
        if capability not in self.capabilities:
            self.capabilities.append(capability)

    def remove_capability(self, capability):
        if capability in self.capabilities:
            self.capabilities.remove(capability)

    def can_handle_task(self, task):
        required_capabilities = task.get('required_capabilities', [])
        return all(cap in self.capabilities for cap in required_capabilities)

    def assign_task(self, task):
        if self.can_handle_task(task):
            self.current_task = task
            return True
        return False

    def complete_task(self):
        if self.current_task:
            result = f"Task '{self.current_task.get('name', 'Unknown')}' completed by {self.name}"
            self.task_history.append({
                'task': self.current_task,
                'result': result,
                'status': 'completed'
            })
            self.current_task = None
            return result
        return "No task assigned"

    def update_knowledge_base(self, key: str, value: any):
        self.knowledge_base[key] = value
        self.persistent_knowledge_base[key] = value

    def get_knowledge(self, key: str) -> any:
        return self.persistent_knowledge_base.get(key) or self.knowledge_base.get(key)

    def add_user_feedback(self, feedback: str, task_id: str = None):
        self.user_feedback.append({
            'feedback': feedback,
            'task_id': task_id,
            'timestamp': time.time()
        })

    def set_preference(self, key: str, value: any):
        self.preferences[key] = value

    def get_preference(self, key: str) -> any:
        return self.preferences.get(key)

    def self_critique(self, task_result: str, openrouter_client) -> str:
        if self.role != 'lead':
            return "Only lead agents can perform self-critique."

        critique_prompt = f"""
        As a lead agent, critically evaluate your performance on the following task:

        Task Result: {task_result}

        Consider the following aspects in your critique:
        1. Task completion: Was the task fully completed? If not, what was missing?
        2. Efficiency: Could the task have been completed more efficiently?
        3. Quality: How would you rate the quality of the result?
        4. Resource utilization: Were the right agents assigned to the task?
        5. Areas for improvement: What could be done better next time?

        Provide a detailed self-critique based on these aspects.
        """

        critique_response = openrouter_client.chat_completion([
            {"role": "system", "content": "You are a highly capable AI assistant performing a self-critique."},
            {"role": "user", "content": critique_prompt}
        ])

        critique = critique_response['choices'][0]['message']['content']
        self.self_critiques.append({
            'task_result': task_result,
            'critique': critique,
            'timestamp': time.time()
        })

        return critique

    def evaluate_agent(self, agent, openrouter_client) -> str:
        if self.role != 'lead':
            return "Only lead agents can evaluate other agents."

        evaluation_prompt = f"""
        As a lead agent, evaluate the performance of the following agent:

        Agent Name: {agent.name}
        Agent Role: {agent.role}
        Agent Capabilities: {', '.join(agent.capabilities)}
        Recent Task History: {json.dumps(agent.task_history[-5:], indent=2)}

        Consider the following aspects in your evaluation:
        1. Task completion rate: How often does the agent successfully complete assigned tasks?
        2. Quality of work: How well does the agent perform its assigned tasks?
        3. Efficiency: Does the agent complete tasks in a timely manner?
        4. Versatility: How well does the agent adapt to different types of tasks?
        5. Collaboration: How well does the agent work with other agents?
        6. Areas for improvement: What skills or capabilities could the agent develop to perform better?

        Provide a detailed evaluation based on these aspects.
        """

        evaluation_response = openrouter_client.chat_completion([
            {"role": "system", "content": "You are a highly capable AI assistant evaluating another agent's performance."},
            {"role": "user", "content": evaluation_prompt}
        ])

        evaluation = evaluation_response['choices'][0]['message']['content']
        self.agent_evaluations[agent.id] = {
            'agent_name': agent.name,
            'evaluation': evaluation,
            'timestamp': time.time()
        }

        return evaluation

    def optimize_agent(self, agent, evaluation: str, openrouter_client) -> str:
        if self.role != 'lead':
            return "Only lead agents can optimize other agents."

        optimization_prompt = f"""
        Based on the following evaluation of an agent, suggest specific ways to optimize its performance:

        Agent Name: {agent.name}
        Agent Role: {agent.role}
        Agent Capabilities: {', '.join(agent.capabilities)}
        Evaluation: {evaluation}

        Provide specific recommendations for:
        1. Skill development: What new skills should the agent learn?
        2. Knowledge expansion: What areas of knowledge should the agent focus on expanding?
        3. Task allocation: What types of tasks should be assigned or avoided for this agent?
        4. Collaboration improvements: How can the agent better work with other agents?
        5. Performance metrics: What metrics should be tracked to monitor the agent's improvement?

        Offer concrete, actionable suggestions for each area.
        """

        optimization_response = openrouter_client.chat_completion([
            {"role": "system", "content": "You are a highly capable AI assistant providing optimization suggestions for another agent."},
            {"role": "user", "content": optimization_prompt}
        ])

        optimization = optimization_response['choices'][0]['message']['content']
        return optimization

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
            'role': self.role,
            'managed_agents': [agent.id for agent in self.managed_agents] if self.role == 'lead' else [],
            'knowledge_base': self.knowledge_base,
            'persistent_knowledge_base': self.persistent_knowledge_base,
            'task_history': self.task_history,
            'user_feedback': self.user_feedback,
            'preferences': self.preferences,
            'self_critiques': self.self_critiques,
            'agent_evaluations': self.agent_evaluations
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
        agent.role = data.get('role', 'general')
        agent.knowledge_base = data.get('knowledge_base', {})
        agent.persistent_knowledge_base = data.get('persistent_knowledge_base', {})
        agent.task_history = data.get('task_history', [])
        agent.user_feedback = data.get('user_feedback', [])
        agent.preferences = data.get('preferences', {})
        agent.self_critiques = data.get('self_critiques', [])
        agent.agent_evaluations = data.get('agent_evaluations', {})
        return agent

    def __repr__(self):
        return f"Agent(id={self.id}, name={self.name}, role={self.role})"