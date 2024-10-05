import React, { useState, useEffect } from 'react';
import axios from 'axios';

const PromptManager = ({ projectId }) => {
  const [prompts, setPrompts] = useState([]);
  const [newPrompt, setNewPrompt] = useState({ name: '', content: '' });
  const [editingPrompt, setEditingPrompt] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (projectId) {
      fetchPrompts();
    }
  }, [projectId]);

  const fetchPrompts = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await axios.get(`/api/projects/${projectId}/prompts`);
      setPrompts(response.data.prompts);
    } catch (error) {
      setError('Error fetching prompts. Please try again.');
      console.error('Error fetching prompts:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleCreatePrompt = async () => {
    setIsLoading(true);
    setError(null);
    try {
      await axios.post(`/api/projects/${projectId}/prompts`, newPrompt);
      setNewPrompt({ name: '', content: '' });
      await fetchPrompts();
    } catch (error) {
      setError('Error creating prompt. Please try again.');
      console.error('Error creating prompt:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleUpdatePrompt = async () => {
    setIsLoading(true);
    setError(null);
    try {
      await axios.put(`/api/projects/${projectId}/prompts/${editingPrompt.id}`, editingPrompt);
      setEditingPrompt(null);
      await fetchPrompts();
    } catch (error) {
      setError('Error updating prompt. Please try again.');
      console.error('Error updating prompt:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleDeletePrompt = async (promptId) => {
    setIsLoading(true);
    setError(null);
    try {
      await axios.delete(`/api/projects/${projectId}/prompts/${promptId}`);
      await fetchPrompts();
    } catch (error) {
      setError('Error deleting prompt. Please try again.');
      console.error('Error deleting prompt:', error);
    } finally {
      setIsLoading(false);
    }
  };

  if (!projectId) {
    return <div>Please select a project to manage prompts.</div>;
  }

  return (
    <div>
      <h2>Prompt Manager</h2>
      {error && <div className="error">{error}</div>}
      {isLoading && <div className="loading">Loading...</div>}
      <div>
        <h3>Create New Prompt</h3>
        <input
          type="text"
          placeholder="Prompt Name"
          value={newPrompt.name}
          onChange={(e) => setNewPrompt({ ...newPrompt, name: e.target.value })}
        />
        <textarea
          placeholder="Prompt Content"
          value={newPrompt.content}
          onChange={(e) => setNewPrompt({ ...newPrompt, content: e.target.value })}
        />
        <button onClick={handleCreatePrompt} disabled={isLoading}>Create Prompt</button>
      </div>
      <div>
        <h3>Existing Prompts</h3>
        {prompts.map((prompt) => (
          <div key={prompt.id}>
            {editingPrompt && editingPrompt.id === prompt.id ? (
              <>
                <input
                  type="text"
                  value={editingPrompt.name}
                  onChange={(e) => setEditingPrompt({ ...editingPrompt, name: e.target.value })}
                />
                <textarea
                  value={editingPrompt.content}
                  onChange={(e) => setEditingPrompt({ ...editingPrompt, content: e.target.value })}
                />
                <button onClick={handleUpdatePrompt} disabled={isLoading}>Save</button>
                <button onClick={() => setEditingPrompt(null)} disabled={isLoading}>Cancel</button>
              </>
            ) : (
              <>
                <h4>{prompt.name}</h4>
                <p>{prompt.content}</p>
                <button onClick={() => setEditingPrompt(prompt)} disabled={isLoading}>Edit</button>
                <button onClick={() => handleDeletePrompt(prompt.id)} disabled={isLoading}>Delete</button>
              </>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

export default PromptManager;