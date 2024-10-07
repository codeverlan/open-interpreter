import React, { useState, useEffect } from 'react';
import axios from 'axios';

const API_BASE_URL = '/api';

const AgentManager = () => {
  const [agents, setAgents] = useState([]);
  const [projects, setProjects] = useState([]);
  const [selectedProject, setSelectedProject] = useState(null);
  const [newAgentName, setNewAgentName] = useState('');
  const [newAgentDescription, setNewAgentDescription] = useState('');
  const [newAgentModel, setNewAgentModel] = useState('');
  const [newAgentRole, setNewAgentRole] = useState('general');
  const [editingAgent, setEditingAgent] = useState(null);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [aiModels, setAiModels] = useState([]);
  const [taskDescription, setTaskDescription] = useState('');
  const [taskIterations, setTaskIterations] = useState(1);
  const [taskResult, setTaskResult] = useState('');
  const [taskProgress, setTaskProgress] = useState(null);
  const [nextSteps, setNextSteps] = useState('');
  const [currentTaskId, setCurrentTaskId] = useState(null);
  const [feedback, setFeedback] = useState('');
  const [preferenceKey, setPreferenceKey] = useState('');
  const [preferenceValue, setPreferenceValue] = useState('');
  const [projectInfo, setProjectInfo] = useState({});
  const [editingProjectInfo, setEditingProjectInfo] = useState(false);
  const [editingKnowledgeBase, setEditingKnowledgeBase] = useState(null);
  const [selfCritiques, setSelfCritiques] = useState({});
  const [agentEvaluations, setAgentEvaluations] = useState({});

  useEffect(() => {
    fetchProjects();
    fetchAiModels();
  }, []);

  useEffect(() => {
    if (selectedProject) {
      fetchAgents();
      fetchProjectInfo();
    }
  }, [selectedProject]);

  useEffect(() => {
    if (error || success) {
      const timer = setTimeout(() => {
        setError(null);
        setSuccess(null);
      }, 5000);
      return () => clearTimeout(timer);
    }
  }, [error, success]);

  useEffect(() => {
    let intervalId;
    if (currentTaskId) {
      intervalId = setInterval(() => {
        fetchTaskProgress(currentTaskId);
      }, 5000); // Check progress every 5 seconds
    }
    return () => {
      if (intervalId) {
        clearInterval(intervalId);
      }
    };
  }, [currentTaskId]);

  const fetchProjects = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await axios.get(`${API_BASE_URL}/projects`);
      setProjects(response.data.projects);
      if (response.data.projects.length > 0) {
        setSelectedProject(response.data.projects[0].id);
      }
    } catch (err) {
      console.error('Error fetching projects:', err);
      setError('Failed to fetch projects. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const fetchProjectInfo = async () => {
    if (!selectedProject) return;
    try {
      const response = await axios.get(`${API_BASE_URL}/projects/${selectedProject}/info`);
      setProjectInfo(response.data.project_info);
    } catch (err) {
      console.error('Error fetching project info:', err);
      setError('Failed to fetch project info. Please try again.');
    }
  };

  const updateProjectInfo = async () => {
    if (!selectedProject) return;
    try {
      await axios.put(`${API_BASE_URL}/projects/${selectedProject}/info`, projectInfo);
      setSuccess('Project information updated successfully.');
      setEditingProjectInfo(false);
    } catch (err) {
      console.error('Error updating project info:', err);
      setError('Failed to update project info. Please try again.');
    }
  };

  const fetchAgents = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await axios.get(`${API_BASE_URL}/agents?project_id=${selectedProject}`);
      setAgents(response.data.agents);
      response.data.agents.forEach(agent => {
        if (agent.role === 'lead') {
          fetchSelfCritiques(agent.id);
        }
        fetchAgentEvaluations(agent.id);
      });
    } catch (err) {
      console.error('Error fetching agents:', err);
      setError('Failed to fetch agents. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const fetchSelfCritiques = async (agentId) => {
    try {
      const response = await axios.get(`${API_BASE_URL}/agents/${agentId}/self_critiques`);
      setSelfCritiques(prevState => ({...prevState, [agentId]: response.data.self_critiques}));
    } catch (err) {
      console.error('Error fetching self-critiques:', err);
      setError('Failed to fetch self-critiques. Please try again.');
    }
  };

  const fetchAgentEvaluations = async (agentId) => {
    try {
      const response = await axios.get(`${API_BASE_URL}/agents/${agentId}/evaluations`);
      setAgentEvaluations(prevState => ({...prevState, [agentId]: response.data.agent_evaluations}));
    } catch (err) {
      console.error('Error fetching agent evaluations:', err);
      setError('Failed to fetch agent evaluations. Please try again.');
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
        role: newAgentRole,
        project_id: selectedProject,
      });
      setAgents([...agents, response.data.agent]);
      setNewAgentName('');
      setNewAgentDescription('');
      setNewAgentModel('');
      setNewAgentRole('general');
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
        role: editingAgent.role,
        status: editingAgent.status,
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

  const handleProjectChange = (e) => {
    setSelectedProject(e.target.value);
  };

  const executeTask = async (e) => {
    e.preventDefault();
    setError(null);
    setSuccess(null);
    setTaskResult('');
    setTaskProgress(null);
    setNextSteps('');
    try {
      const response = await axios.post(`${API_BASE_URL}/tasks`, {
        description: taskDescription,
        iterations: taskIterations,
      });
      setCurrentTaskId(response.data.task_id);
      setSuccess('Task started successfully.');
    } catch (err) {
      console.error('Error executing task:', err);
      setError('Failed to execute task. Please try again.');
    }
  };

  const fetchTaskProgress = async (taskId) => {
    try {
      const response = await axios.get(`${API_BASE_URL}/tasks/${taskId}/progress`);
      setTaskProgress(response.data.progress);
      if (response.data.progress.status === 'completed') {
        setTaskResult(response.data.progress.results[response.data.progress.results.length - 1]);
        fetchNextSteps(taskId);
        setCurrentTaskId(null);
        fetchAgents(); // Refresh agents to get updated self-critiques and evaluations
      }
    } catch (err) {
      console.error('Error fetching task progress:', err);
    }
  };

  const fetchNextSteps = async (taskId) => {
    try {
      const response = await axios.get(`${API_BASE_URL}/tasks/${taskId}/next_steps`);
      setNextSteps(response.data.next_steps);
    } catch (err) {
      console.error('Error fetching next steps:', err);
    }
  };

  const submitFeedback = async (agentId) => {
    try {
      await axios.post(`${API_BASE_URL}/agents/${agentId}/feedback`, { feedback });
      setSuccess('Feedback submitted successfully.');
      setFeedback('');
    } catch (err) {
      console.error('Error submitting feedback:', err);
      setError('Failed to submit feedback. Please try again.');
    }
  };

  const setPreference = async (agentId) => {
    try {
      await axios.post(`${API_BASE_URL}/agents/${agentId}/preferences`, { key: preferenceKey, value: preferenceValue });
      setSuccess('Preference set successfully.');
      setPreferenceKey('');
      setPreferenceValue('');
    } catch (err) {
      console.error('Error setting preference:', err);
      setError('Failed to set preference. Please try again.');
    }
  };

  const updateKnowledgeBase = async (agentId) => {
    try {
      await axios.put(`${API_BASE_URL}/agents/${agentId}/knowledge`, editingKnowledgeBase);
      setSuccess('Knowledge base updated successfully.');
      setEditingKnowledgeBase(null);
      fetchAgents(); // Refresh the agents to get the updated knowledge base
    } catch (err) {
      console.error('Error updating knowledge base:', err);
      setError('Failed to update knowledge base. Please try again.');
    }
  };

  if (isLoading) {
    return <div className="loading">Loading...</div>;
  }

  return (
    <div className="agent-manager">
      <h2>Agent Manager</h2>
      {error && <p className="message error">{error}</p>}
      {success && <p className="message success">{success}</p>}
      <div className="project-selector">
        <label htmlFor="project-select">Select Project: </label>
        <select id="project-select" value={selectedProject} onChange={handleProjectChange}>
          {projects.map((project) => (
            <option key={project.id} value={project.id}>{project.name}</option>
          ))}
        </select>
      </div>
      <div className="project-info">
        <h3>Project Information</h3>
        {editingProjectInfo ? (
          <div>
            <textarea
              value={JSON.stringify(projectInfo, null, 2)}
              onChange={(e) => setProjectInfo(JSON.parse(e.target.value))}
              rows={10}
              cols={50}
            />
            <button onClick={updateProjectInfo}>Save Project Info</button>
            <button onClick={() => setEditingProjectInfo(false)}>Cancel</button>
          </div>
        ) : (
          <div>
            <pre>{JSON.stringify(projectInfo, null, 2)}</pre>
            <button onClick={() => setEditingProjectInfo(true)}>Edit Project Info</button>
          </div>
        )}
      </div>
      <button onClick={fetchAgents} className="refresh-button">Refresh Agents</button>
      <div className="agent-list">
        <h3>Existing Agents</h3>
        {agents.length === 0 ? (
          <p>No agents found for this project.</p>
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
                    <select
                      value={editingAgent.role}
                      onChange={(e) => setEditingAgent({ ...editingAgent, role: e.target.value })}
                      className="agent-input"
                      required
                    >
                      <option value="lead">Lead</option>
                      <option value="general">General</option>
                      <option value="specialized">Specialized</option>
                    </select>
                    <select
                      value={editingAgent.status}
                      onChange={(e) => setEditingAgent({ ...editingAgent, status: e.target.value })}
                      className="agent-input"
                      required
                    >
                      <option value="idle">Idle</option>
                      <option value="working">Working</option>
                      <option value="completed">Completed</option>
                    </select>
                    <button type="submit">Save</button>
                    <button onClick={() => setEditingAgent(null)}>Cancel</button>
                  </form>
                ) : (
                  <>
                    <strong>{agent.name}</strong>: {agent.description}
                    <br />
                    <strong>Model:</strong> {agent.assigned_model || 'Not assigned'}
                    <br />
                    <strong>Role:</strong> {agent.role}
                    <br />
                    <strong>Status:</strong> {agent.status}
                    <br />
                    <strong>Current Task:</strong> {agent.current_task ? JSON.stringify(agent.current_task) : 'None'}
                    <br />
                    <strong>Knowledge Base:</strong>
                    <pre>{JSON.stringify(agent.knowledge_base, null, 2)}</pre>
                    <strong>Persistent Knowledge Base:</strong>
                    {editingKnowledgeBase && editingKnowledgeBase.id === agent.id ? (
                      <div>
                        <textarea
                          value={JSON.stringify(editingKnowledgeBase.persistent_knowledge_base, null, 2)}
                          onChange={(e) => setEditingKnowledgeBase({
                            ...editingKnowledgeBase,
                            persistent_knowledge_base: JSON.parse(e.target.value)
                          })}
                          rows={10}
                          cols={50}
                        />
                        <button onClick={() => updateKnowledgeBase(agent.id)}>Save Knowledge Base</button>
                        <button onClick={() => setEditingKnowledgeBase(null)}>Cancel</button>
                      </div>
                    ) : (
                      <div>
                        <pre>{JSON.stringify(agent.persistent_knowledge_base, null, 2)}</pre>
                        <button onClick={() => setEditingKnowledgeBase({
                          id: agent.id,
                          persistent_knowledge_base: agent.persistent_knowledge_base
                        })}>Edit Knowledge Base</button>
                      </div>
                    )}
                    <strong>Task History:</strong>
                    <ul>
                      {agent.task_history.map((task, index) => (
                        <li key={index}>
                          <strong>Task:</strong> {task.task.description}
                          <br />
                          <strong>Result:</strong> {task.result}
                          <br />
                          <strong>Timestamp:</strong> {new Date(task.timestamp * 1000).toLocaleString()}
                        </li>
                      ))}
                    </ul>
                    <strong>User Feedback:</strong>
                    <ul>
                      {agent.user_feedback.map((feedback, index) => (
                        <li key={index}>
                          <strong>Feedback:</strong> {feedback.feedback}
                          <br />
                          <strong>Timestamp:</strong> {new Date(feedback.timestamp * 1000).toLocaleString()}
                        </li>
                      ))}
                    </ul>
                    <strong>Preferences:</strong>
                    <pre>{JSON.stringify(agent.preferences, null, 2)}</pre>
                    {agent.role === 'lead' && (
                      <>
                        <strong>Self-Critiques:</strong>
                        <ul>
                          {selfCritiques[agent.id] && selfCritiques[agent.id].map((critique, index) => (
                            <li key={index}>
                              <strong>Task Result:</strong> {critique.task_result}
                              <br />
                              <strong>Critique:</strong> {critique.critique}
                              <br />
                              <strong>Timestamp:</strong> {new Date(critique.timestamp * 1000).toLocaleString()}
                            </li>
                          ))}
                        </ul>
                      </>
                    )}
                    <strong>Agent Evaluations:</strong>
                    <ul>
                      {agentEvaluations[agent.id] && Object.entries(agentEvaluations[agent.id]).map(([evaluatedAgentId, evaluation]) => (
                        <li key={evaluatedAgentId}>
                          <strong>Evaluated Agent:</strong> {evaluation.agent_name}
                          <br />
                          <strong>Evaluation:</strong> {evaluation.evaluation}
                          <br />
                          <strong>Timestamp:</strong> {new Date(evaluation.timestamp * 1000).toLocaleString()}
                        </li>
                      ))}
                    </ul>
                    <button onClick={() => setEditingAgent(agent)} className="edit-button">Edit</button>
                    <button onClick={() => deleteAgent(agent.id)} className="delete-button">Delete</button>
                    <div className="feedback-form">
                      <input
                        type="text"
                        value={feedback}
                        onChange={(e) => setFeedback(e.target.value)}
                        placeholder="Enter feedback"
                      />
                      <button onClick={() => submitFeedback(agent.id)}>Submit Feedback</button>
                    </div>
                    <div className="preference-form">
                      <input
                        type="text"
                        value={preferenceKey}
                        onChange={(e) => setPreferenceKey(e.target.value)}
                        placeholder="Preference Key"
                      />
                      <input
                        type="text"
                        value={preferenceValue}
                        onChange={(e) => setPreferenceValue(e.target.value)}
                        placeholder="Preference Value"
                      />
                      <button onClick={() => setPreference(agent.id)}>Set Preference</button>
                    </div>
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
          <select
            value={newAgentRole}
            onChange={(e) => setNewAgentRole(e.target.value)}
            required
            className="agent-input"
          >
            <option value="lead">Lead</option>
            <option value="general">General</option>
            <option value="specialized">Specialized</option>
          </select>
          <button type="submit" className="create-button">Create Agent</button>
        </form>
      </div>
      <div className="execute-task">
        <h3>Execute Task</h3>
        <form onSubmit={executeTask} className="task-form">
          <textarea
            placeholder="Task Description"
            value={taskDescription}
            onChange={(e) => setTaskDescription(e.target.value)}
            required
            className="task-input"
          />
          <input
            type="number"
            placeholder="Number of Iterations"
            value={taskIterations}
            onChange={(e) => setTaskIterations(parseInt(e.target.value))}
            required
            min="1"
            className="task-input"
          />
          <button type="submit" className="execute-button">Execute Task</button>
        </form>
        {taskProgress && (
          <div className="task-progress">
            <h4>Task Progress:</h4>
            <p>Status: {taskProgress.status}</p>
            <p>Iteration: {taskProgress.current_iteration} / {taskProgress.total_iterations}</p>
          </div>
        )}
        {taskResult && (
          <div className="task-result">
            <h4>Task Result:</h4>
            <pre>{taskResult}</pre>
          </div>
        )}
        {nextSteps && (
          <div className="next-steps">
            <h4>Suggested Next Steps:</h4>
            <pre>{nextSteps}</pre>
          </div>
        )}
      </div>
    </div>
  );
};

export default AgentManager;