# /root/open/interpreter/core/task_assignment.py

from typing import List, Dict
from interpreter.core.agent import Agent
from interpreter.core.openrouter_client import OpenRouterClient
from flask_sqlalchemy import SQLAlchemy
import json
import time

db = SQLAlchemy()

class TaskAssignmentSystem:
    def __init__(self, lead_agent: Agent, openrouter_client: OpenRouterClient):
        self.lead_agent = lead_agent
        if self.lead_agent.role != 'lead':
            raise ValueError("The provided agent must be a Lead Agent.")
        self.openrouter_client = openrouter_client
        self.task_progress = {}

    def analyze_task(self, task: Dict) -> Dict:
        """
        Analyze the task using AI to determine required capabilities, complexity, and subtasks.
        """
        prompt = f"""
        Analyze the following task and provide:
        1. A list of required capabilities
        2. The complexity level (simple, moderate, complex)
        3. Whether it needs to be broken down into subtasks
        4. If subtasks are needed, provide a list of subtasks

        Task: {task['description']}
        """
        
        response = self.openrouter_client.chat_completion([
            {"role": "system", "content": "You are a task analysis AI."},
            {"role": "user", "content": prompt}
        ])

        # Parse the AI response to extract the required information
        analysis = response['choices'][0]['message']['content']
        lines = analysis.split('\n')
        capabilities = lines[0].split(':')[1].strip().split(', ')
        complexity = lines[1].split(':')[1].strip()
        needs_breakdown = 'yes' in lines[2].lower()
        subtasks = []
        if needs_breakdown:
            subtasks = [line.strip() for line in lines[4:] if line.strip()]

        return {
            'required_capabilities': capabilities,
            'complexity': complexity,
            'needs_breakdown': needs_breakdown,
            'subtasks': subtasks
        }

    def select_agents(self, task: Dict) -> List[Agent]:
        """
        Select the most appropriate agent(s) for the given task based on capabilities, roles, and task complexity.
        """
        analysis = self.analyze_task(task)
        required_capabilities = analysis['required_capabilities']
        complexity = analysis['complexity']
        
        suitable_agents = []

        for agent in [self.lead_agent] + self.lead_agent.managed_agents:
            capability_match = all(cap in agent.capabilities for cap in required_capabilities)
            complexity_match = (complexity == 'complex' and agent.role == 'specialized') or \
                               (complexity == 'moderate' and agent.role in ['specialized', 'general']) or \
                               (complexity == 'simple')
            
            if capability_match and complexity_match and agent.status == 'idle':
                suitable_agents.append(agent)

        # Sort suitable agents by role, number of matching capabilities, and user feedback
        suitable_agents.sort(key=lambda a: (
            a.role == 'specialized',  # Specialized agents first
            a.role == 'general',      # Then general agents
            a.role == 'lead',         # Lead agent last
            len(set(a.capabilities) & set(required_capabilities)),  # Then by number of matching capabilities
            self.calculate_agent_score(a)  # Then by agent score based on user feedback
        ), reverse=True)

        return suitable_agents

    def calculate_agent_score(self, agent: Agent) -> float:
        """
        Calculate a score for the agent based on user feedback and task history.
        """
        score = 0
        for feedback in agent.user_feedback:
            # Implement a scoring system based on feedback
            # This is a simple example, you may want to implement a more sophisticated system
            if 'positive' in feedback['feedback'].lower():
                score += 1
            elif 'negative' in feedback['feedback'].lower():
                score -= 1
        
        # Consider task history
        successful_tasks = sum(1 for task in agent.task_history if task['status'] == 'completed')
        score += successful_tasks * 0.5  # Add 0.5 points for each successful task

        return score

    def assign_task(self, task: Dict) -> Agent:
        """
        Assign the task to the most suitable agent or break it down if necessary.
        """
        analysis = self.analyze_task(task)
        
        if analysis['needs_breakdown']:
            subtasks = analysis['subtasks']
            results = []
            for subtask in subtasks:
                subtask_result = self.execute_task({'description': subtask})
                results.append(subtask_result)
            return self.lead_agent.summarize_results(results)

        selected_agents = self.select_agents(task)
        
        if not selected_agents:
            return None

        # Assign to the most suitable agent
        assigned_agent = selected_agents[0]
        assigned_agent.assign_task(task)
        
        # Update agent status in the database
        with db.session.begin():
            agent_model = db.session.query(AgentModel).get(assigned_agent.id)
            agent_model.status = 'working'
            agent_model.current_task = json.dumps(task)
            db.session.commit()

        return assigned_agent

    def execute_task(self, task: Dict, iterations: int = 1) -> str:
        """
        Execute the task using the assigned agent(s) and facilitate inter-agent communication.
        Supports multiple iterations as defined by the user.
        """
        task_id = str(time.time())  # Use timestamp as a simple task ID
        self.task_progress[task_id] = {
            'total_iterations': iterations,
            'current_iteration': 0,
            'status': 'in_progress',
            'results': []
        }

        for i in range(iterations):
            self.task_progress[task_id]['current_iteration'] = i + 1
            
            assigned_agent = self.assign_task(task)
            if not assigned_agent:
                self.task_progress[task_id]['status'] = 'failed'
                return "No suitable agent found for the task."

            result = assigned_agent.complete_task()
            
            # If the assigned agent is not the lead agent, have the lead agent review and possibly enhance the result
            if assigned_agent != self.lead_agent:
                review_prompt = f"""
                Review and enhance the following task result if necessary:

                Task: {task['description']}
                Result: {result}

                Provide an enhanced result or confirm the original result is sufficient.
                """
                
                review_response = self.openrouter_client.chat_completion([
                    {"role": "system", "content": "You are a task review AI."},
                    {"role": "user", "content": review_prompt}
                ])

                enhanced_result = review_response['choices'][0]['message']['content']
                result = self.lead_agent.summarize_results([result, enhanced_result])

            self.task_progress[task_id]['results'].append(result)

            # Perform self-critique for the lead agent
            critique = self.lead_agent.self_critique(result, self.openrouter_client)
            self.task_progress[task_id]['critique'] = critique

            # Evaluate and optimize the assigned agent
            if assigned_agent != self.lead_agent:
                evaluation = self.lead_agent.evaluate_agent(assigned_agent, self.openrouter_client)
                optimization = self.lead_agent.optimize_agent(assigned_agent, evaluation, self.openrouter_client)
                self.task_progress[task_id]['agent_evaluation'] = evaluation
                self.task_progress[task_id]['agent_optimization'] = optimization

            # Update the knowledge base and persistent knowledge base of all agents with the task result
            for agent in [self.lead_agent] + self.lead_agent.managed_agents:
                agent.update_knowledge_base(f"task_{task['description'][:50]}", result)

            # Update agent status, task history, and persistent knowledge base in the database
            with db.session.begin():
                agent_model = db.session.query(AgentModel).get(assigned_agent.id)
                agent_model.status = 'idle'
                agent_model.current_task = None
                task_history = json.loads(agent_model.task_history)
                task_history.append({
                    'task': task,
                    'result': result,
                    'timestamp': time.time()
                })
                agent_model.task_history = json.dumps(task_history)
                agent_model.persistent_knowledge_base = json.dumps(assigned_agent.persistent_knowledge_base)
                if assigned_agent.role == 'lead':
                    self_critiques = json.loads(agent_model.self_critiques)
                    self_critiques.append({
                        'task_result': result,
                        'critique': critique,
                        'timestamp': time.time()
                    })
                    agent_model.self_critiques = json.dumps(self_critiques)
                db.session.commit()

            # If this is not the last iteration, wait for a short time before the next iteration
            if i < iterations - 1:
                time.sleep(5)  # Wait for 5 seconds between iterations

        self.task_progress[task_id]['status'] = 'completed'
        return self.task_progress[task_id]['results'][-1]  # Return the last result

    def get_task_progress(self, task_id: str) -> Dict:
        """
        Get the progress of a specific task.
        """
        return self.task_progress.get(task_id, {'status': 'not_found'})

    def suggest_next_steps(self, task_id: str) -> str:
        """
        Suggest next steps based on the task results and current progress.
        """
        task_info = self.task_progress.get(task_id)
        if not task_info:
            return "Task not found."

        if task_info['status'] != 'completed':
            return "Task is still in progress. Please wait for it to complete."

        results = task_info['results']
        critique = task_info.get('critique', '')
        agent_evaluation = task_info.get('agent_evaluation', '')
        agent_optimization = task_info.get('agent_optimization', '')
        
        suggestion_prompt = f"""
        Based on the following task results, self-critique, agent evaluation, and optimization suggestions, suggest the next steps to take:

        Task Results:
        {' '.join(f'Iteration {i+1}: {result}' for i, result in enumerate(results))}

        Self-Critique:
        {critique}

        Agent Evaluation:
        {agent_evaluation}

        Agent Optimization Suggestions:
        {agent_optimization}

        Please provide 3-5 concrete suggestions for next steps, considering any improvements or new directions that could be explored based on these results, self-critique, and agent evaluation/optimization.
        """

        suggestion_response = self.openrouter_client.chat_completion([
            {"role": "system", "content": "You are an AI assistant specialized in project planning and task management."},
            {"role": "user", "content": suggestion_prompt}
        ])

        return suggestion_response['choices'][0]['message']['content']

    def coordinate_multi_agent_task(self, task: Dict, iterations: int = 1) -> str:
        """
        Coordinate a task that requires multiple agents to complete.
        Supports multiple iterations as defined by the user.
        """
        task_id = str(time.time())  # Use timestamp as a simple task ID
        self.task_progress[task_id] = {
            'total_iterations': iterations,
            'current_iteration': 0,
            'status': 'in_progress',
            'results': []
        }

        for i in range(iterations):
            self.task_progress[task_id]['current_iteration'] = i + 1
            
            analysis = self.analyze_task(task)
            if not analysis['needs_breakdown']:
                return self.execute_task(task)

            subtasks = analysis['subtasks']
            results = []
            for subtask in subtasks:
                subtask_result = self.execute_task({'description': subtask})
                results.append(subtask_result)

            # Have the lead agent coordinate and synthesize the results
            coordination_prompt = f"""
            Coordinate and synthesize the results of the following subtasks into a cohesive solution:

            Main Task: {task['description']}

            Subtask Results:
            {' '.join(f'Subtask {i+1}: {result}' for i, result in enumerate(results))}

            Provide a final, coordinated solution that addresses the main task.
            """

            coordination_response = self.openrouter_client.chat_completion([
                {"role": "system", "content": "You are a task coordination AI."},
                {"role": "user", "content": coordination_prompt}
            ])

            final_result = coordination_response['choices'][0]['message']['content']
            self.task_progress[task_id]['results'].append(final_result)

            # Perform self-critique for the lead agent
            critique = self.lead_agent.self_critique(final_result, self.openrouter_client)
            self.task_progress[task_id]['critique'] = critique

            # Evaluate and optimize all involved agents
            for agent in self.lead_agent.managed_agents:
                evaluation = self.lead_agent.evaluate_agent(agent, self.openrouter_client)
                optimization = self.lead_agent.optimize_agent(agent, evaluation, self.openrouter_client)
                if 'agent_evaluations' not in self.task_progress[task_id]:
                    self.task_progress[task_id]['agent_evaluations'] = {}
                if 'agent_optimizations' not in self.task_progress[task_id]:
                    self.task_progress[task_id]['agent_optimizations'] = {}
                self.task_progress[task_id]['agent_evaluations'][agent.id] = evaluation
                self.task_progress[task_id]['agent_optimizations'][agent.id] = optimization

            # Update the lead agent's task history and persistent knowledge base
            self.lead_agent.task_history.append({
                'task': task,
                'result': final_result,
                'timestamp': time.time()
            })
            self.lead_agent.update_knowledge_base(f"multi_agent_task_{task['description'][:50]}", final_result)

            # Update lead agent's task history, persistent knowledge base, and self-critiques in the database
            with db.session.begin():
                lead_agent_model = db.session.query(AgentModel).get(self.lead_agent.id)
                task_history = json.loads(lead_agent_model.task_history)
                task_history.append({
                    'task': task,
                    'result': final_result,
                    'timestamp': time.time()
                })
                lead_agent_model.task_history = json.dumps(task_history)
                lead_agent_model.persistent_knowledge_base = json.dumps(self.lead_agent.persistent_knowledge_base)
                self_critiques = json.loads(lead_agent_model.self_critiques)
                self_critiques.append({
                    'task_result': final_result,
                    'critique': critique,
                    'timestamp': time.time()
                })
                lead_agent_model.self_critiques = json.dumps(self_critiques)
                db.session.commit()

            # If this is not the last iteration, wait for a short time before the next iteration
            if i < iterations - 1:
                time.sleep(5)  # Wait for 5 seconds between iterations

        self.task_progress[task_id]['status'] = 'completed'
        return self.task_progress[task_id]['results'][-1]  # Return the last result

    def request_human_intervention(self, task: Dict, reason: str) -> str:
        """
        Request human intervention when the agents cannot complete a task.
        """
        intervention_prompt = f"""
        Human intervention is required for the following task:

        Task: {task['description']}
        Reason for intervention: {reason}

        Please provide guidance or additional information to help complete this task.
        """

        # In a real implementation, this would involve notifying the user and waiting for their input
        # For now, we'll simulate it with an AI response
        intervention_response = self.openrouter_client.chat_completion([
            {"role": "system", "content": "You are simulating a human user providing intervention."},
            {"role": "user", "content": intervention_prompt}
        ])

        human_guidance = intervention_response['choices'][0]['message']['content']
        return f"Human intervention received: {human_guidance}"

    def resume_incomplete_tasks(self):
        """
        Resume any incomplete tasks for agents with 'working' status.
        """
        with db.session.begin():
            working_agents = db.session.query(AgentModel).filter_by(status='working').all()
            for agent_model in working_agents:
                agent = Agent.from_dict(agent_model.to_dict())
                task = json.loads(agent_model.current_task)
                self.execute_task(task)

    def submit_user_feedback(self, task_id: str, feedback: str) -> bool:
        """
        Submit user feedback for a completed task.
        """
        if task_id not in self.task_progress or self.task_progress[task_id]['status'] != 'completed':
            return False

        if 'user_feedback' not in self.task_progress[task_id]:
            self.task_progress[task_id]['user_feedback'] = []
        
        self.task_progress[task_id]['user_feedback'].append({
            'feedback': feedback,
            'timestamp': time.time()
        })

        # Update the lead agent's knowledge base with the feedback
        self.lead_agent.update_knowledge_base(f"feedback_task_{task_id}", feedback)

        # Store the feedback in the database
        with db.session.begin():
            lead_agent_model = db.session.query(AgentModel).get(self.lead_agent.id)
            user_feedback = json.loads(lead_agent_model.user_feedback)
            user_feedback.append({
                'task_id': task_id,
                'feedback': feedback,
                'timestamp': time.time()
            })
            lead_agent_model.user_feedback = json.dumps(user_feedback)
            db.session.commit()

        return True

# Example usage:
# lead_agent = Agent("Lead Agent", description="Lead agent for task assignment")
# lead_agent.set_role('lead')
# lead_agent.add_capability("task_delegation")
# 
# specialized_agent = Agent("Specialized Agent", description="Specialized agent for Python tasks")
# specialized_agent.set_role('specialized')
# specialized_agent.add_capability("python")
# specialized_agent.add_capability("code_review")
# 
# general_agent = Agent("General Agent", description="General-purpose agent")
# general_agent.set_role('general')
# general_agent.add_capability("research")
# general_agent.add_capability("writing")
# 
# lead_agent.add_managed_agent(specialized_agent)
# lead_agent.add_managed_agent(general_agent)
# 
# openrouter_client = OpenRouterClient()  # Assume this is properly initialized
# task_system = TaskAssignmentSystem(lead_agent, openrouter_client)
# 
# task = {
#     "name": "Optimize Python Code",
#     "description": "Review and optimize the Python code for our web application, focusing on performance improvements."
# }
# 
# result = task_system.execute_task(task, iterations=3)
# print(result)