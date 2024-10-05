import React, { useState, useEffect } from 'react';
import axios from 'axios';

const AgentManager = () => {
  const [agents, setAgents] = useState([]);
  const [newAgent, setNewAgent] = useState({ name: '', description: '', prompt: '', ai_model: '' });
  const [feedback, setFeedback] = useState({ agentId: '', content: '' });
  const [selectedAgent, setSelectedAgent] = useState(null);

  useEffect(() => {
    fetchAgents();
  }, []);

  const fetchAgents = async () => {
    try {
      const response = await axios.get('/api/agents');
      setAgents(response.data.agents);
    } catch (error) {
      console.error('Error fetching agents:', error);
    }
  };

  const handleInputChange = (e) => {
    setNewAgent({ ...newAgent, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await axios.post('/api/agents', newAgent);
      setNewAgent({ name: '', description: '', prompt: '', ai_model: '' });
      fetchAgents();
    } catch (error) {
      console.error('Error creating agent:', error);
    }
  };

  const handleDelete = async (agentId) => {
    try {
      await axios.delete(`/api/agents/${agentId}`);
      fetchAgents();
    } catch (error) {
      console.error('Error deleting agent:', error);
    }
  };

  const handleFeedbackChange = (e) => {
    setFeedback({ ...feedback, [e.target.name]: e.target.value });
  };

  const handleFeedbackSubmit = async (e) => {
    e.preventDefault();
    try {
      await axios.post(`/api/agents/${feedback.agentId}/feedback`, { content: feedback.content });
      setFeedback({ agentId: '', content: '' });
      alert('Feedback submitted successfully');
    } catch (error) {
      console.error('Error submitting feedback:', error);
    }
  };

  const handleAgentSelect = (agent) => {
    setSelectedAgent(agent);
    setFeedback({ agentId: agent.id, content: '' });
  };

  return (
    <div>
      <h2>Agent Manager</h2>
      <form onSubmit={handleSubmit}>
        <input
          type="text"
          name="name"
          value={newAgent.name}
          onChange={handleInputChange}
          placeholder="Agent Name"
          required
        />
        <input
          type="text"
          name="description"
          value={newAgent.description}
          onChange={handleInputChange}
          placeholder="Description"
        />
        <textarea
          name="prompt"
          value={newAgent.prompt}
          onChange={handleInputChange}
          placeholder="Prompt"
          required
        />
        <input
          type="text"
          name="ai_model"
          value={newAgent.ai_model}
          onChange={handleInputChange}
          placeholder="AI Model"
          required
        />
        <button type="submit">Create Agent</button>
      </form>
      <h3>Agents</h3>
      <ul>
        {agents.map((agent) => (
          <li key={agent.id}>
            {agent.name} - {agent.description}
            <button onClick={() => handleAgentSelect(agent)}>Select</button>
            <button onClick={() => handleDelete(agent.id)}>Delete</button>
          </li>
        ))}
      </ul>
      {selectedAgent && (
        <div>
          <h3>Selected Agent: {selectedAgent.name}</h3>
          <h4>Submit Feedback</h4>
          <form onSubmit={handleFeedbackSubmit}>
            <textarea
              name="content"
              value={feedback.content}
              onChange={handleFeedbackChange}
              placeholder="Enter your feedback"
              required
            />
            <button type="submit">Submit Feedback</button>
          </form>
        </div>
      )}
    </div>
  );
};

export default AgentManager;