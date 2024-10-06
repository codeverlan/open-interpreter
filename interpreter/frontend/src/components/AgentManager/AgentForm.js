```javascript
import React, { useState, useEffect } from 'react';
import { createAgent, getAgent, updateAgent } from '../../api/agentApi';
import { useHistory, useParams } from 'react-router-dom';

const AgentForm = () => {
  const { id } = useParams();
  const history = useHistory();
  const isEditing = Boolean(id);

  const [agentData, setAgentData] = useState({
    name: '',
    description: '',
    prompt: '',
    ai_model: '',
    skills: []
  });

  useEffect(() => {
    if (isEditing) {
      fetchAgent();
    }
  }, []);

  const fetchAgent = async () => {
    try {
      const response = await getAgent(id);
      if (response.success) {
        setAgentData(response.agent);
      } else {
        console.error('Failed to fetch agent:', response.error);
      }
    } catch (error) {
      console.error('Error fetching agent:', error);
    }
  };

  const handleChange = (e) => {
    setAgentData({
      ...agentData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      let response;
      if (isEditing) {
        response = await updateAgent(id, agentData);
      } else {
        response = await createAgent(agentData);
      }

      if (response.success) {
        history.push('/agents');
      } else {
        console.error('Failed to save agent:', response.error);
      }
    } catch (error) {
      console.error('Error saving agent:', error);
    }
  };

  return (
    <div>
      <h2>{isEditing ? 'Edit Agent' : 'Create Agent'}</h2>
      <form onSubmit={handleSubmit}>
        <div>
          <label>Agent Name:</label>
          <input
            type="text"
            name="name"
            value={agentData.name}
            onChange={handleChange}
            required
          />
        </div>
        <div>
          <label>Description:</label>
          <textarea
            name="description"
            value={agentData.description}
            onChange={handleChange}
          />
        </div>
        <div>
          <label>Prompt:</label>
          <textarea
            name="prompt"
            value={agentData.prompt}
            onChange={handleChange}
          />
        </div>
        <div>
          <label>AI Model:</label>
          <input
            type="text"
            name="ai_model"
            value={agentData.ai_model}
            onChange={handleChange}
          />
        </div>
        {/* Add fields for skills and other parameters as needed */}
        <button type="submit">{isEditing ? 'Update Agent' : 'Create Agent'}</button>
      </form>
    </div>
  );
};

export default AgentForm;
```