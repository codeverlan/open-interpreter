# /root/open/interpreter/core/test_environment.py

import sys
import os

# Add the project root directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from interpreter.core.agent import Agent
from interpreter.core.environment import Environment
from interpreter.core.skill import TEMPERATURE_CONTROL, HUMIDITY_CONTROL

def test_agent_environment_interaction():
    # Create an environment
    env = Environment()
    env.set_state({"temperature": 25, "humidity": 70})  # Start with suboptimal conditions

    # Create an agent with skills
    agent = Agent(name="ClimateController", description="Controls room climate")
    agent.add_skill(TEMPERATURE_CONTROL)
    agent.add_skill(HUMIDITY_CONTROL)

    # Set the environment for the agent
    agent.set_environment(env)

    print("Initial setup:")
    print(f"Environment state: {env.get_state()}")
    print(f"Agent skills: {agent.get_skills()}")

    # Simulate multiple cycles of perception, action, and evaluation
    for cycle in range(3):
        print(f"\nCycle {cycle + 1}:")
        
        # Agent perceives the environment
        agent.perceive()
        print(f"Agent state after perception: {agent.state}")

        # Agent acts on the environment
        actions = agent.act()
        print("Actions taken:")
        for action in actions:
            print(f"- {action}")

        # Environment updates
        env.update()
        print(f"Environment state after update: {env.get_state()}")

        # Agent evaluates its performance
        evaluation = agent.evaluate()
        print(f"Performance evaluation:\n{evaluation}")

    # Demonstrate accessing agent abilities
    print("\nAgent Abilities:")
    for skill in agent.get_skills():
        print(f"- {skill['name']}: {skill['description']}")

if __name__ == "__main__":
    test_agent_environment_interaction()