import React, { useState, useEffect } from 'react';
import axios from 'axios';

const API_BASE_URL = '/api';

const AgentManager = () => {
  const [agents, setAgents] = useState([]);
  const [newAgentName, setNewAgentName] = useState('');
  const [newAgentDescription, setNewAgentDescription] = useState('');
  const [newAgentModel, setNewAgentModel] = useState('');
  const [editingAgent, setEditingAgent] = useState(null);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [aiModels, setAiModels] = useState([]);

  useEffect(() => {
    fetchAgents();
    fetchAiModels();
  }, []);

  useEffect(() => {
    if (error || success) {
      const timer = setTimeout(() => {
        setError(null);
        setSuccess(null);
      }, 5000);
      return () => clearTimeout(timer);
    }
  }, [error, success]);

  const fetchAgents = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await axios.get(`${API_BASE_URL}/agents`);
      setAgents(response.data.agents);
    } catch (err) {
      console.error('Error fetching agents:', err);
      setError('Failed to fetch agents. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const fetchAiModels = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/ai_models`);
      setAiModels(response.data.models);
    } catch (err) {
      console.error('Error fetching AI models:', err);
      setError('Failed to fetch AI models. Please try again.');
    }
  };

  const createAgent = async (e) => {
    e.preventDefault();
    setError(null);
    setSuccess(null);
    try {
      const response = await axios.post(`${API_BASE_URL}/agents`, {
        name: newAgentName,
        description: newAgentDescription,
        assigned_model: newAgentModel,
      });
      setAgents([...agents, response.data.agent]);
      setNewAgentName('');
      setNewAgentDescription('');
      setNewAgentModel('');
      setSuccess('Agent created successfully.');
    } catch (err) {
      console.error('Error creating agent:', err);
      setError('Failed to create agent. Please try again.');
    }
  };

  const updateAgent = async (e) => {
    e.preventDefault();
    setError(null);
    setSuccess(null);
    try {
      const response = await axios.put(`${API_BASE_URL}/agents/${editingAgent.id}`, {
        name: editingAgent.name,
        description: editingAgent.description,
        assigned_model: editingAgent.assigned_model,
      });
      setAgents(agents.map(agent => agent.id === editingAgent.id ? response.data.agent : agent));
      setEditingAgent(null);
      setSuccess('Agent updated successfully.');
    } catch (err) {
      console.error('Error updating agent:', err);
      setError('Failed to update agent. Please try again.');
    }
  };

  const deleteAgent = async (agentId) => {
    if (window.confirm('Are you sure you want to delete this agent?')) {
      setError(null);
      setSuccess(null);
      try {
        await axios.delete(`${API_BASE_URL}/agents/${agentId}`);
        setAgents(agents.filter(agent => agent.id !== agentId));
        setSuccess('Agent deleted successfully.');
      } catch (err) {
        console.error('Error deleting agent:', err);
        setError('Failed to delete agent. Please try again.');
      }
    }
  };

  if (isLoading) {
    return <div className="loading">Loading agents...</div>;
  }

  return (
    <div className="agent-manager">
      <h2>Agent Manager</h2>
      {error && <p className="message error">{error}</p>}
      {success && <p className="message success">{success}</p>}
      <button onClick={fetchAgents} className="refresh-button">Refresh Agents</button>
      <div className="agent-list">
        <h3>Existing Agents</h3>
        {agents.length === 0 ? (
          <p>No agents found.</p>
        ) : (
          <ul>
            {agents.map((agent) => (
              <li key={agent.id} className="agent-item">
                {editingAgent && editingAgent.id === agent.id ? (
                  <form onSubmit={updateAgent} className="agent-form">
                    <input
                      type="text"
                      value={editingAgent.name}
                      onChange={(e) => setEditingAgent({ ...editingAgent, name: e.target.value })}
                      className="agent-input"
                      required
                    />
                    <input
                      type="text"
                      value={editingAgent.description}
                      onChange={(e) => setEditingAgent({ ...editingAgent, description: e.target.value })}
                      className="agent-input"
                      required
                    />
                    <select
                      value={editingAgent.assigned_model}
                      onChange={(e) => setEditingAgent({ ...editingAgent, assigned_model: e.target.value })}
                      className="agent-input"
                      required
                    >
                      <option value="">Select AI Model</option>
                      {aiModels.map((model) => (
                        <option key={model} value={model}>{model}</option>
                      ))}
                    </select>
                    <button type="submit">Save</button>
                    <button onClick={() => setEditingAgent(null)}>Cancel</button>
                  </form>
                ) : (
                  <>
                    <strong>{agent.name}</strong>: {agent.description}
                    <br />
                    <strong>Model:</strong> {agent.assigned_model || 'Not assigned'}
                    <button onClick={() => setEditingAgent(agent)} className="edit-button">Edit</button>
                    <button onClick={() => deleteAgent(agent.id)} className="delete-button">Delete</button>
                  </>
                )}
              </li>
            ))}
          </ul>
        )}
      </div>
      <div className="create-agent">
        <h3>Create New Agent</h3>
        <form onSubmit={createAgent} className="agent-form">
          <input
            type="text"
            placeholder="Agent Name"
            value={newAgentName}
            onChange={(e) => setNewAgentName(e.target.value)}
            required
            className="agent-input"
          />
          <input
            type="text"
            placeholder="Agent Description"
            value={newAgentDescription}
            onChange={(e) => setNewAgentDescription(e.target.value)}
            required
            className="agent-input"
          />
          <select
            value={newAgentModel}
            onChange={(e) => setNewAgentModel(e.target.value)}
            required
            className="agent-input"
          >
            <option value="">Select AI Model</option>
            {aiModels.map((model) => (
              <option key={model} value={model}>{model}</option>
            ))}
          </select>
          <button type="submit" className="create-button">Create Agent</button>
        </form>
      </div>
    </div>
  );
};

export default AgentManager;