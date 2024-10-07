from typing import List, Dict
import json
import time
from .anthropic_client import anthropic_client
from .openrouter_client import openrouter_client

class Agent:
    def __init__(self, name: str, description: str = '', prompt: str = '', ai_model: str = 'claude-2', skills: List = None, parent=None):
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
        self.real_time_feedback = []

    # ... (previous methods remain unchanged)

    def add_real_time_feedback(self, feedback: str, task_id: str = None):
        self.real_time_feedback.append({
            'feedback': feedback,
            'task_id': task_id,
            'timestamp': time.time()
        })
        self._process_real_time_feedback(feedback)

    def _process_real_time_feedback(self, feedback: str):
        prompt = f"""
        Based on the following real-time feedback, suggest how I should adjust my behavior:
        
        Feedback: {feedback}
        
        Current task: {self.current_task}
        Recent performance: {json.dumps(self.performance_history[-3:], indent=2)}
        
        Provide specific, actionable suggestions for adjusting my behavior.
        """
        
        response = anthropic_client.chat_completion([
            {"role": "user", "content": prompt}
        ])
        
        print(f"Behavior adjustment suggestions based on feedback: {response}")

    def get_latest_feedback(self, count: int = 5) -> List[Dict]:
        return sorted(self.real_time_feedback, key=lambda x: x['timestamp'], reverse=True)[:count]

    def internet_access(self, query: str) -> str:
        prompt = f"""
        I need to find information about the following query:
        
        {query}
        
        Please provide a summary of the most relevant information you can find. 
        If you can't find exact information, provide the most relevant related information.
        """
        
        response = anthropic_client.chat_completion([
            {"role": "user", "content": prompt}
        ])
        
        return response

    def recommend_behavior_update(self) -> str:
        recent_tasks = self.task_history[-5:]
        recent_feedback = self.get_latest_feedback()
        recent_performance = self.performance_history[-5:]

        prompt = f"""
        Based on my recent performance, feedback, and task history, recommend updates to my behavior:

        Recent tasks: {json.dumps(recent_tasks, indent=2)}
        Recent feedback: {json.dumps(recent_feedback, indent=2)}
        Recent performance: {json.dumps(recent_performance, indent=2)}

        Provide specific, actionable recommendations for improving my performance and capabilities.
        """

        response = openrouter_client.chat_completion([
            {"role": "user", "content": prompt}
        ])

        return response['choices'][0]['message']['content']

    def self_critique(self, task_result: str) -> str:
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

    def evaluate_agent(self, agent) -> str:
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

    def optimize_agent(self, agent, evaluation: str) -> str:
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
            'agent_evaluations': self.agent_evaluations,
            'real_time_feedback': self.real_time_feedback
        }

    @classmethod
    def from_dict(cls, data):
        agent = cls(
            name=data.get('name'),
            description=data.get('description', ''),
            prompt=data.get('prompt', ''),
            ai_model=data.get('ai_model', 'claude-2'),
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
        agent.real_time_feedback = data.get('real_time_feedback', [])
        return agent

    def __repr__(self):
        return f"Agent(id={self.id}, name={self.name}, role={self.role})"