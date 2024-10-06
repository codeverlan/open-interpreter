```javascript
import React, { useEffect, useState } from 'react';
import { getAgent, deleteAgent } from '../../api/agentApi';
import { useParams, useHistory, Link } from 'react-router-dom';

const AgentDetail = () => {
  const { id } = useParams();
  const history = useHistory();
  const [agent, setAgent] = useState(null);

  useEffect(() => {
    fetchAgent();
  }, []);

  const fetchAgent = async () => {
    try {
      const response = await getAgent(id);
      if (response.success) {
        setAgent(response.agent);
      } else {
        console.error('Failed to fetch agent:', response.error);
      }
    } catch (error) {
      console.error('Error fetching agent:', error);
    }
  };

  const handleDelete = async () => {
    try {
      const response = await deleteAgent(id);
      if (response.success) {
        history.push('/agents');
      } else {
        console.error('Failed to delete agent:', response.error);
      }
    } catch (error) {
      console.error('Error deleting agent:', error);
    }
  };

  if (!agent) {
    return <div>Loading agent...</div>;
  }

  return (
    <div>
      <h2>{agent.name}</h2>
      <p>{agent.description}</p>
      <Link to={`/agents/edit/${agent.id}`}>Edit Agent</Link>
      <button onClick={handleDelete}>Delete Agent</button>
    </div>
  );
};

export default AgentDetail;
```