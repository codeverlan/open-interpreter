# /root/open/interpreter/core/skill.py

class Skill:
    def __init__(self, name, description, action):
        self.name = name
        self.description = description
        self.action = action

    def execute(self, agent, environment):
        """
        Execute the skill's action.

        :param agent: The agent executing the skill
        :param environment: The environment the skill is being executed in
        :return: The result of the action
        """
        return self.action(agent, environment)

    def __repr__(self):
        return f"Skill(name='{self.name}', description='{self.description}')"

# Example skills
def adjust_temperature(agent, environment):
    current_temp = environment.get_state().get('temperature', 20)
    if current_temp > 22:
        environment.set_state({'temperature': current_temp - 1})
        return f"{agent.name} lowered the temperature to {current_temp - 1}"
    elif current_temp < 20:
        environment.set_state({'temperature': current_temp + 1})
        return f"{agent.name} raised the temperature to {current_temp + 1}"
    return f"{agent.name} maintained the temperature at {current_temp}"

def adjust_humidity(agent, environment):
    current_humidity = environment.get_state().get('humidity', 50)
    if current_humidity > 60:
        environment.set_state({'humidity': current_humidity - 5})
        return f"{agent.name} lowered the humidity to {current_humidity - 5}"
    elif current_humidity < 40:
        environment.set_state({'humidity': current_humidity + 5})
        return f"{agent.name} raised the humidity to {current_humidity + 5}"
    return f"{agent.name} maintained the humidity at {current_humidity}"

TEMPERATURE_CONTROL = Skill("Temperature Control", "Adjust room temperature", adjust_temperature)
HUMIDITY_CONTROL = Skill("Humidity Control", "Adjust room humidity", adjust_humidity)