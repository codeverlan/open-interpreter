```javascript
// /root/open/interpreter/frontend/src/api/agentApi.js

import axios from 'axios';

const API_BASE_URL = '/api';

// Existing functions (if any) are retained here

/**
 * Fetch all agents from the backend API.
 * @returns {Promise<Object>} Response data containing the list of agents.
 */
export async function getAgents() {
  try {
    const response = await axios.get(`${API_BASE_URL}/agents`);
    return response.data;
  } catch (error) {
    console.error('Error fetching agents:', error);
    throw error;
  }
}

/**
 * Fetch a specific agent by ID from the backend API.
 * @param {number} agentId - The ID of the agent to retrieve.
 * @returns {Promise<Object>} Response data containing the agent details.
 */
export async function getAgent(agentId) {
  try {
    const response = await axios.get(`${API_BASE_URL}/agents/${agentId}`);
    return response.data;
  } catch (error) {
    console.error(`Error fetching agent with ID ${agentId}:`, error);
    throw error;
  }
}

/**
 * Create a new agent using the backend API.
 * @param {Object} agentData - The data of the agent to create.
 * @returns {Promise<Object>} Response data after creating the agent.
 */
export async function createAgent(agentData) {
  try {
    const response = await axios.post(`${API_BASE_URL}/agents`, agentData);
    return response.data;
  } catch (error) {
    console.error('Error creating agent:', error);
    throw error;
  }
}

/**
 * Update an existing agent using the backend API.
 * @param {number} agentId - The ID of the agent to update.
 * @param {Object} agentData - The updated data of the agent.
 * @returns {Promise<Object>} Response data after updating the agent.
 */
export async function updateAgent(agentId, agentData) {
  try {
    const response = await axios.put(`${API_BASE_URL}/agents/${agentId}`, agentData);
    return response.data;
  } catch (error) {
    console.error(`Error updating agent with ID ${agentId}:`, error);
    throw error;
  }
}

/**
 * Delete an agent using the backend API.
 * @param {number} agentId - The ID of the agent to delete.
 * @returns {Promise<Object>} Response data after deleting the agent.
 */
export async function deleteAgent(agentId) {
  try {
    const response = await axios.delete(`${API_BASE_URL}/agents/${agentId}`);
    return response.data;
  } catch (error) {
    console.error(`Error deleting agent with ID ${agentId}:`, error);
    throw error;
  }
}

// Export other existing functions (if any)
```