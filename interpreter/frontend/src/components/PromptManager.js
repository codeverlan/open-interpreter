import React, { useState, useEffect, useCallback, useMemo } from 'react';
import axios from 'axios';
import debounce from 'lodash/debounce';

const PromptManager = ({ projectId }) => {
  const [prompts, setPrompts] = useState([]);
  const [newPrompt, setNewPrompt] = useState({ name: '', content: '' });
  const [editingPrompt, setEditingPrompt] = useState(null);
  const [defaultSystemMessage, setDefaultSystemMessage] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [selectedPrompt, setSelectedPrompt] = useState(null);
  const [promptVersions, setPromptVersions] = useState([]);

  const fetchPrompts = useCallback(async () => {
    if (!projectId) return;
    setIsLoading(true);
    setError(null);
    try {
      const response = await axios.get(`/api/projects/${projectId}/prompts`);
      setPrompts(response.data.prompts.filter(p => !p.is_default_system_message));
    } catch (error) {
      setError('Error fetching prompts. Please try again.');
      console.error('Error fetching prompts:', error);
    } finally {
      setIsLoading(false);
    }
  }, [projectId]);

  const fetchDefaultSystemMessage = useCallback(async () => {
    if (!projectId) return;
    setIsLoading(true);
    setError(null);
    try {
      const response = await axios.get(`/api/projects/${projectId}/prompts/default_system_message`);
      setDefaultSystemMessage(response.data.prompt);
    } catch (error) {
      setError('Error fetching default system message. Please try again.');
      console.error('Error fetching default system message:', error);
    } finally {
      setIsLoading(false);
    }
  }, [projectId]);

  const fetchPromptVersions = useCallback(async (promptId) => {
    if (!projectId || !promptId) return;
    setIsLoading(true);
    setError(null);
    try {
      const response = await axios.get(`/api/projects/${projectId}/prompts/${promptId}/versions`);
      setPromptVersions(response.data.versions);
    } catch (error) {
      setError('Error fetching prompt versions. Please try again.');
      console.error('Error fetching prompt versions:', error);
    } finally {
      setIsLoading(false);
    }
  }, [projectId]);

  useEffect(() => {
    fetchPrompts();
    fetchDefaultSystemMessage();
  }, [fetchPrompts, fetchDefaultSystemMessage]);

  const handleCreatePrompt = useCallback(async () => {
    if (!newPrompt.name || !newPrompt.content) {
      setError('Please provide both name and content for the new prompt.');
      return;
    }
    setIsLoading(true);
    setError(null);
    try {
      const response = await axios.post(`/api/projects/${projectId}/prompts`, newPrompt);
      setPrompts(prevPrompts => [...prevPrompts, response.data.prompt]);
      setNewPrompt({ name: '', content: '' });
    } catch (error) {
      setError('Error creating prompt. Please try again.');
      console.error('Error creating prompt:', error);
    } finally {
      setIsLoading(false);
    }
  }, [projectId, newPrompt]);

  const handleUpdatePrompt = useCallback(async () => {
    if (!editingPrompt || !editingPrompt.name || !editingPrompt.content) {
      setError('Please provide both name and content for the prompt.');
      return;
    }
    setIsLoading(true);
    setError(null);
    try {
      const response = await axios.put(`/api/projects/${projectId}/prompts/${editingPrompt.id}`, editingPrompt);
      setPrompts(prevPrompts =>
        prevPrompts.map(p => (p.id === editingPrompt.id ? response.data.prompt : p))
      );
      setEditingPrompt(null);
      fetchPromptVersions(editingPrompt.id);
    } catch (error) {
      setError('Error updating prompt. Please try again.');
      console.error('Error updating prompt:', error);
    } finally {
      setIsLoading(false);
    }
  }, [projectId, editingPrompt, fetchPromptVersions]);

  const handleDeletePrompt = useCallback(async (promptId) => {
    setIsLoading(true);
    setError(null);
    try {
      await axios.delete(`/api/projects/${projectId}/prompts/${promptId}`);
      setPrompts(prevPrompts => prevPrompts.filter(p => p.id !== promptId));
      setSelectedPrompt(null);
      setPromptVersions([]);
    } catch (error) {
      setError('Error deleting prompt. Please try again.');
      console.error('Error deleting prompt:', error);
    } finally {
      setIsLoading(false);
    }
  }, [projectId]);

  const handleUpdateDefaultSystemMessage = useCallback(async () => {
    if (!defaultSystemMessage || !defaultSystemMessage.content) {
      setError('Please provide content for the default system message.');
      return;
    }
    setIsLoading(true);
    setError(null);
    try {
      await axios.put(`/api/projects/${projectId}/prompts/default_system_message`, {
        content: defaultSystemMessage.content
      });
      setError('Default system message updated successfully.');
    } catch (error) {
      setError('Error updating default system message. Please try again.');
      console.error('Error updating default system message:', error);
    } finally {
      setIsLoading(false);
    }
  }, [projectId, defaultSystemMessage]);

  const handleSelectPrompt = useCallback((prompt) => {
    setSelectedPrompt(prompt);
    fetchPromptVersions(prompt.id);
  }, [fetchPromptVersions]);

  const handleActivateVersion = useCallback(async (versionId) => {
    setIsLoading(true);
    setError(null);
    try {
      await axios.post(`/api/projects/${projectId}/prompts/${selectedPrompt.id}/versions/${versionId}/activate`);
      fetchPromptVersions(selectedPrompt.id);
      fetchPrompts();
    } catch (error) {
      setError('Error activating prompt version. Please try again.');
      console.error('Error activating prompt version:', error);
    } finally {
      setIsLoading(false);
    }
  }, [projectId, selectedPrompt, fetchPromptVersions, fetchPrompts]);

  const debouncedSetNewPrompt = useMemo(
    () => debounce((field, value) => setNewPrompt(prev => ({ ...prev, [field]: value })), 300),
    []
  );

  const debouncedSetEditingPrompt = useMemo(
    () => debounce((field, value) => setEditingPrompt(prev => ({ ...prev, [field]: value })), 300),
    []
  );

  const debouncedSetDefaultSystemMessage = useMemo(
    () => debounce((value) => setDefaultSystemMessage(prev => ({ ...prev, content: value })), 300),
    []
  );

  if (!projectId) {
    return <div className="prompt-manager">Please select a project to manage prompts.</div>;
  }

  return (
    <div className="prompt-manager">
      <h2>Prompt Manager</h2>
      {error && <div className="error">{error}</div>}
      {isLoading && <div className="loading">Loading...</div>}
      
      <div className="default-system-message">
        <h3>Default System Message</h3>
        <textarea
          value={defaultSystemMessage?.content || ''}
          onChange={(e) => debouncedSetDefaultSystemMessage(e.target.value)}
          disabled={isLoading}
        />
        <button onClick={handleUpdateDefaultSystemMessage} disabled={isLoading}>
          Update Default System Message
        </button>
      </div>

      <div className="prompt-form">
        <h3>Create New Prompt</h3>
        <input
          type="text"
          placeholder="Prompt Name"
          value={newPrompt.name}
          onChange={(e) => debouncedSetNewPrompt('name', e.target.value)}
          disabled={isLoading}
        />
        <textarea
          placeholder="Prompt Content"
          value={newPrompt.content}
          onChange={(e) => debouncedSetNewPrompt('content', e.target.value)}
          disabled={isLoading}
        />
        <button onClick={handleCreatePrompt} disabled={isLoading || !newPrompt.name || !newPrompt.content}>
          Create Prompt
        </button>
      </div>

      <div className="prompt-list">
        <h3>Existing Prompts</h3>
        {prompts.map((prompt) => (
          <div key={prompt.id} className="prompt-item">
            {editingPrompt && editingPrompt.id === prompt.id ? (
              <>
                <input
                  type="text"
                  value={editingPrompt.name}
                  onChange={(e) => debouncedSetEditingPrompt('name', e.target.value)}
                  disabled={isLoading}
                />
                <textarea
                  value={editingPrompt.content}
                  onChange={(e) => debouncedSetEditingPrompt('content', e.target.value)}
                  disabled={isLoading}
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
                <button onClick={() => handleSelectPrompt(prompt)} disabled={isLoading}>View Versions</button>
              </>
            )}
          </div>
        ))}
      </div>

      {selectedPrompt && (
        <div className="prompt-versions">
          <h3>Versions for {selectedPrompt.name}</h3>
          {promptVersions.map((version) => (
            <div key={version.id} className="version-item">
              <p>Version {version.version} {version.is_active ? '(Active)' : ''}</p>
              <p>{version.content}</p>
              {!version.is_active && (
                <button onClick={() => handleActivateVersion(version.id)} disabled={isLoading}>
                  Activate
                </button>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default PromptManager;