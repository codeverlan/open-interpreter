import React, { useState, useEffect, useCallback } from 'react';
import './ProjectStatus.css';

const ProjectStatus = ({ apiEndpoint }) => {
  const [status, setStatus] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [isSaving, setIsSaving] = useState(false);

  const fetchProjectStatus = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await fetch(`${apiEndpoint}/project_status`);
      if (!response.ok) {
        throw new Error('Failed to fetch project status');
      }
      const data = await response.json();
      setStatus(data.status || 'No project status available. Click to edit.');
    } catch (error) {
      console.error('Error fetching project status:', error);
      setError('Failed to fetch project status. Please try again.');
    } finally {
      setIsLoading(false);
    }
  }, [apiEndpoint]);

  useEffect(() => {
    fetchProjectStatus();
  }, [fetchProjectStatus]);

  const updateProjectStatus = useCallback(async () => {
    setIsSaving(true);
    setError(null);
    try {
      const response = await fetch(`${apiEndpoint}/project_status`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ status }),
      });
      if (!response.ok) {
        throw new Error('Failed to update project status');
      }
    } catch (error) {
      console.error('Error updating project status:', error);
      setError('Failed to update project status. Please try again.');
    } finally {
      setIsSaving(false);
    }
  }, [apiEndpoint, status]);

  const handleChange = (e) => {
    setStatus(e.target.value);
  };

  const handleSave = () => {
    updateProjectStatus();
  };

  const handleCancel = () => {
    fetchProjectStatus();
  };

  if (isLoading) {
    return <div className="loading">Loading...</div>;
  }

  if (error) {
    return <div className="error">{error}</div>;
  }

  return (
    <div className="project-status">
      <h2>Project Status</h2>
      <textarea
        className="markdown-editor"
        value={status}
        onChange={handleChange}
        placeholder="Enter project status here..."
      />
      <div className="button-group">
        <button onClick={handleSave} disabled={isSaving}>
          {isSaving ? 'Saving...' : 'Save'}
        </button>
        <button onClick={handleCancel}>Cancel</button>
      </div>
      {isSaving && <div className="save-indicator">Saving...</div>}
    </div>
  );
};

export default ProjectStatus;