# /root/open/interpreter/core/task_assignment.py

from typing import List, Dict
from interpreter.core.agent import Agent

class TaskAssignmentSystem:
    def __init__(self, agents: List[Agent]):
        self.agents = agents

    def analyze_task(self, task: Dict) -> List[str]:
        """
        Analyze the task and return a list of required capabilities.
        """
        # This is a simple implementation. In a real-world scenario,
        # this method would use NLP or other AI techniques to analyze the task.
        return task.get('required_capabilities', [])

    def select_agents(self, task: Dict) -> List[Agent]:
        """
        Select the most appropriate agent(s) for the given task.
        """
        required_capabilities = self.analyze_task(task)
        suitable_agents = []

        for agent in self.agents:
            if all(cap in agent.capabilities for cap in required_capabilities):
                suitable_agents.append(agent)

        # Sort suitable agents by the number of matching capabilities (most to least)
        suitable_agents.sort(key=lambda a: len(set(a.capabilities) & set(required_capabilities)), reverse=True)

        return suitable_agents

    def assign_task(self, task: Dict) -> List[Agent]:
        """
        Assign the task to the most suitable agent(s).
        """
        selected_agents = self.select_agents(task)
        assigned_agents = []

        for agent in selected_agents:
            if agent.assign_task(task):
                assigned_agents.append(agent)
                break  # For now, we're assigning the task to only one agent

        return assigned_agents

    def execute_task(self, task: Dict) -> str:
        """
        Execute the task using the assigned agent(s).
        """
        assigned_agents = self.assign_task(task)
        if not assigned_agents:
            return "No suitable agent found for the task."

        results = []
        for agent in assigned_agents:
            result = agent.complete_task()
            results.append(result)

        return "\n".join(results)

# Example usage:
# task = {
#     "name": "Analyze code",
#     "description": "Review and optimize Python code",
#     "required_capabilities": ["python", "code_review"]
# }
# task_system = TaskAssignmentSystem(agents)
# result = task_system.execute_task(task)
# print(result)