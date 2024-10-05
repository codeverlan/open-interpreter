import requests
import json

BASE_URL = "http://localhost:5159/api"

def test_create_agent():
    new_agent = {
        "name": "Test Agent",
        "description": "A test agent for API verification",
        "prompt": "You are a test agent.",
        "ai_model": "gpt-3.5-turbo"
    }
    response = requests.post(f"{BASE_URL}/agents", json=new_agent)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] == True
    assert "agent_id" in data
    return data["agent_id"]

def test_get_agents():
    response = requests.get(f"{BASE_URL}/agents")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] == True
    assert "agents" in data
    return data["agents"]

def test_get_agent(agent_id):
    response = requests.get(f"{BASE_URL}/agents/{agent_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] == True
    assert "agent" in data
    return data["agent"]

def test_update_agent(agent_id):
    updated_agent = {
        "name": "Updated Test Agent",
        "description": "An updated test agent",
        "prompt": "You are an updated test agent.",
        "ai_model": "gpt-4"
    }
    response = requests.put(f"{BASE_URL}/agents/{agent_id}", json=updated_agent)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] == True
    assert "agent" in data
    return data["agent"]

def test_delete_agent(agent_id):
    response = requests.delete(f"{BASE_URL}/agents/{agent_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] == True

def test_submit_feedback(agent_id):
    feedback = {
        "content": "This is a test feedback for the agent."
    }
    response = requests.post(f"{BASE_URL}/agents/{agent_id}/feedback", json=feedback)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] == True

def run_tests():
    print("Starting Agent Management API tests...")

    # Create an agent
    agent_id = test_create_agent()
    print(f"Created agent with ID: {agent_id}")

    # Get all agents
    agents = test_get_agents()
    print(f"Retrieved {len(agents)} agents")

    # Get the created agent
    agent = test_get_agent(agent_id)
    print(f"Retrieved agent: {agent['name']}")

    # Update the agent
    updated_agent = test_update_agent(agent_id)
    print(f"Updated agent: {updated_agent['name']}")

    # Submit feedback
    test_submit_feedback(agent_id)
    print("Submitted feedback for the agent")

    # Delete the agent
    test_delete_agent(agent_id)
    print(f"Deleted agent with ID: {agent_id}")

    print("All tests completed successfully!")

if __name__ == "__main__":
    run_tests()