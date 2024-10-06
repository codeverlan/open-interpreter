# /root/open/interpreter/core/task_assignment.py

from typing import List, Dict
from interpreter.core.agent import Agent

class TaskAssignmentSystem:
    def __init__(self, lead_agent: Agent):
        self.lead_agent = lead_agent
        if not self.lead_agent.is_lead_agent:
            raise ValueError("The provided agent must be a Lead Agent.")

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

        for agent in [self.lead_agent] + self.lead_agent.managed_agents:
            if all(cap in agent.capabilities for cap in required_capabilities):
                suitable_agents.append(agent)

        # Sort suitable agents by the number of matching capabilities (most to least)
        suitable_agents.sort(key=lambda a: len(set(a.capabilities) & set(required_capabilities)), reverse=True)

        return suitable_agents

    def assign_task(self, task: Dict) -> Agent:
        """
        Assign the task to the most suitable agent.
        """
        selected_agents = self.select_agents(task)
        
        if not selected_agents:
            return None

        # If the lead agent can handle the task, assign it to the lead agent
        if selected_agents[0] == self.lead_agent:
            self.lead_agent.assign_task(task)
            return self.lead_agent

        # Otherwise, let the lead agent delegate the task
        return self.lead_agent.delegate_task(task)

    def execute_task(self, task: Dict) -> str:
        """
        Execute the task using the assigned agent(s).
        """
        assigned_agent = self.assign_task(task)
        if not assigned_agent:
            return "No suitable agent found for the task."

        result = assigned_agent.process_task(task)
        
        # If the assigned agent is not the lead agent, have the lead agent summarize the result
        if assigned_agent != self.lead_agent:
            result = self.lead_agent.summarize_results([result])

        return result

# Example usage:
# lead_agent = Agent("Lead Agent", description="Lead agent for task assignment")
# lead_agent.set_as_lead_agent()
# lead_agent.add_capability("task_delegation")
# 
# specialized_agent = Agent("Specialized Agent", description="Specialized agent for Python tasks")
# specialized_agent.add_capability("python")
# specialized_agent.add_capability("code_review")
# 
# lead_agent.add_managed_agent(specialized_agent)
# 
# task_system = TaskAssignmentSystem(lead_agent)
# 
# task = {
#     "name": "Analyze code",
#     "description": "Review and optimize Python code",
#     "required_capabilities": ["python", "code_review"]
# }
# 
# result = task_system.execute_task(task)
# print(result)