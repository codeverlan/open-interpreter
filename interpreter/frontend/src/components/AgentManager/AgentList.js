```javascript
import React, { useEffect, useState } from 'react';
import { getAgents } from '../../api/agentApi';
import { Link } from 'react-router-dom';

const AgentList = () => {
  const [agents, setAgents] = useState([]);

  useEffect(() => {
    fetchAgents();
  }, []);

  const fetchAgents = async () => {
    try {
      const response = await getAgents();
      if (response.success) {
        setAgents(response.agents);
      } else {
        console.error('Failed to fetch agents:', response.error);
      }
    } catch (error) {
      console.error('Error fetching agents:', error);
    }
  };

  return (
    <div>
      <h2>Agents</h2>
      <Link to="/agents/new">Create New Agent</Link>
      <ul>
        {agents.map((agent) => (
          <li key={agent.id}>
            <Link to={`/agents/${agent.id}`}>{agent.name}</Link>
          </li>
        ))}
      </ul>
    </div>
  );
};

export default AgentList;
```