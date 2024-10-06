import React, { useState } from 'react';
import axios from 'axios';

const API_BASE_URL = '/api';

const ProjectCreator = ({ onProjectCreated }) => {
  const [projectName, setProjectName] = useState('');
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);

    try {
      const response = await axios.post(`${API_BASE_URL}/create_project`, { name: projectName });
      if (response.data.success) {
        setProjectName('');
        onProjectCreated(response.data.project);
      } else {
        setError(response.data.error || 'Failed to create project');
      }
    } catch (err) {
      setError('Error creating project. Please try again.');
      console.error('Error creating project:', err);
    }
  };

  return (
    <div className="project-creator">
      <h3>Create New Project</h3>
      {error && <p className="error">{error}</p>}
      <form onSubmit={handleSubmit}>
        <input
          type="text"
          value={projectName}
          onChange={(e) => setProjectName(e.target.value)}
          placeholder="Enter project name"
          required
        />
        <button type="submit">Create Project</button>
      </form>
    </div>
  );
};

export default ProjectCreator;