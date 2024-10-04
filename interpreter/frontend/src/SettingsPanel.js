import React, { useState, useEffect, useCallback } from 'react';
import { FaSearch, FaDownload, FaUpload, FaPlus, FaTrash } from 'react-icons/fa';

const settingsCategories = {
  general: ['project_name', 'language'],
  interpreter: ['max_tokens'],
  ui: ['theme', 'font_size'],
};

const settingsDescriptions = {
  project_name: 'Name of the current project',
  language: 'Default programming language',
  max_tokens: 'Maximum number of tokens to generate',
  theme: 'UI theme (light or dark)',
  font_size: 'Font size for the editor',
};

const MAX_RETRIES = 3;
const RETRY_DELAY = 1000;

function SettingsPanel({ apiEndpoint }) {
  const [localSettings, setLocalSettings] = useState({});
  const [projectSettings, setProjectSettings] = useState({});
  const [currentProject, setCurrentProject] = useState(null);
  const [projects, setProjects] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [prompts, setPrompts] = useState({});

  const fetchSettings = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await fetch(`${apiEndpoint}/get_settings`);
      if (!response.ok) {
        throw new Error('Failed to fetch settings');
      }
      const data = await response.json();
      setLocalSettings(data.interpreter_settings);
    } catch (error) {
      console.error('Error fetching settings:', error);
      setError('Failed to fetch settings. Please try again.');
    } finally {
      setIsLoading(false);
    }
  }, [apiEndpoint]);

  const fetchProjects = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await fetch(`${apiEndpoint}/get_projects`);
      if (!response.ok) {
        throw new Error('Failed to fetch projects');
      }
      const data = await response.json();
      setProjects(data.projects);
    } catch (error) {
      console.error('Error fetching projects:', error);
      setError('Failed to fetch projects. Please try again.');
    } finally {
      setIsLoading(false);
    }
  }, [apiEndpoint]);

  const fetchProjectSettings = useCallback(async (projectName) => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await fetch(`${apiEndpoint}/get_project_settings?project=${projectName}`);
      if (!response.ok) {
        throw new Error('Failed to fetch project settings');
      }
      const data = await response.json();
      setProjectSettings(data.settings);
    } catch (error) {
      console.error('Error fetching project settings:', error);
      setError('Failed to fetch project settings. Please try again.');
    } finally {
      setIsLoading(false);
    }
  }, [apiEndpoint]);

  const fetchProjectPrompts = useCallback(async (projectName) => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await fetch(`${apiEndpoint}/get_project_prompts?project=${projectName}`);
      if (!response.ok) {
        throw new Error('Failed to fetch project prompts');
      }
      const data = await response.json();
      setPrompts(data.prompts);
    } catch (error) {
      console.error('Error fetching project prompts:', error);
      setError('Failed to fetch project prompts. Please try again.');
    } finally {
      setIsLoading(false);
    }
  }, [apiEndpoint]);

  useEffect(() => {
    fetchSettings();
    fetchProjects();
  }, [fetchSettings, fetchProjects]);

  useEffect(() => {
    if (currentProject) {
      fetchProjectSettings(currentProject);
      fetchProjectPrompts(currentProject);
    }
  }, [currentProject, fetchProjectSettings, fetchProjectPrompts]);

  const updateSettingsWithRetry = useCallback(async (updatedSettings, retryCount = 0) => {
    try {
      const response = await fetch(`${apiEndpoint}/update_settings`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(updatedSettings),
      });
      if (!response.ok) {
        throw new Error('Failed to update settings');
      }
      const result = await response.json();
      if (!result.success) {
        throw new Error('Failed to update settings');
      }
    } catch (error) {
      if (retryCount < MAX_RETRIES) {
        await new Promise(resolve => setTimeout(resolve, RETRY_DELAY));
        return updateSettingsWithRetry(updatedSettings, retryCount + 1);
      }
      throw error;
    }
  }, [apiEndpoint]);

  const debouncedUpdateSettings = useCallback(
    debounce((updatedSettings) => {
      setIsLoading(true);
      setError(null);
      updateSettingsWithRetry(updatedSettings)
        .then(() => {
          setIsLoading(false);
        })
        .catch((err) => {
          setError('Failed to update settings. Please try again.');
          setIsLoading(false);
          console.error('Error updating settings:', err);
        });
    }, 500),
    [updateSettingsWithRetry]
  );

  const handleSettingChange = (key, value) => {
    const updatedSettings = { ...localSettings, [key]: value };
    setLocalSettings(updatedSettings);
    debouncedUpdateSettings(updatedSettings);
  };

  const handleProjectSettingChange = (key, value) => {
    const updatedSettings = { ...projectSettings, [key]: value };
    setProjectSettings(updatedSettings);
    debouncedUpdateProjectSettings(updatedSettings);
  };

  const handlePromptChange = (key, value) => {
    const updatedPrompts = { ...prompts, [key]: value };
    setPrompts(updatedPrompts);
    debouncedUpdateProjectPrompts(updatedPrompts);
  };

  const debouncedUpdateProjectSettings = useCallback(
    debounce((updatedSettings) => {
      setIsLoading(true);
      setError(null);
      fetch(`${apiEndpoint}/update_project_settings`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ project: currentProject, settings: updatedSettings }),
      })
        .then((response) => {
          if (!response.ok) {
            throw new Error('Failed to update project settings');
          }
          return response.json();
        })
        .then(() => {
          setIsLoading(false);
        })
        .catch((err) => {
          setError('Failed to update project settings. Please try again.');
          setIsLoading(false);
          console.error('Error updating project settings:', err);
        });
    }, 500),
    [apiEndpoint, currentProject]
  );

  const debouncedUpdateProjectPrompts = useCallback(
    debounce((updatedPrompts) => {
      setIsLoading(true);
      setError(null);
      fetch(`${apiEndpoint}/update_project_prompts`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ project: currentProject, prompts: updatedPrompts }),
      })
        .then((response) => {
          if (!response.ok) {
            throw new Error('Failed to update project prompts');
          }
          return response.json();
        })
        .then(() => {
          setIsLoading(false);
        })
        .catch((err) => {
          setError('Failed to update project prompts. Please try again.');
          setIsLoading(false);
          console.error('Error updating project prompts:', err);
        });
    }, 500),
    [apiEndpoint, currentProject]
  );

  const resetToDefaults = () => {
    if (window.confirm('Are you sure you want to reset all settings to their default values?')) {
      setIsLoading(true);
      setError(null);
      updateSettingsWithRetry('default')
        .then(() => {
          fetchSettings();
        })
        .catch((err) => {
          setError('Failed to reset settings. Please try again.');
          setIsLoading(false);
          console.error('Error resetting settings:', err);
        });
    }
  };

  const validateInput = (key, value) => {
    switch (key) {
      case 'max_tokens':
        return value > 0 && value <= 4096;
      case 'font_size':
        return value >= 8 && value <= 24;
      default:
        return true;
    }
  };

  const renderSetting = (key, value, isProjectSetting = false) => {
    const isValid = validateInput(key, value);
    const handleChange = isProjectSetting ? handleProjectSettingChange : handleSettingChange;
    return (
      <div key={key} className={`setting-item ${!isValid ? 'invalid' : ''}`}>
        <label>
          {key}:
          {typeof value === 'boolean' ? (
            <input
              type="checkbox"
              checked={value}
              onChange={(e) => handleChange(key, e.target.checked)}
            />
          ) : typeof value === 'number' ? (
            <input
              type="number"
              value={value}
              onChange={(e) => handleChange(key, Number(e.target.value))}
              step={1}
            />
          ) : (
            <input
              type="text"
              value={value}
              onChange={(e) => handleChange(key, e.target.value)}
            />
          )}
        </label>
        <p className="setting-description">{settingsDescriptions[key]}</p>
        {!isValid && <p className="error-message">Invalid value</p>}
      </div>
    );
  };

  const renderPrompt = (key, value) => {
    return (
      <div key={key} className="setting-item">
        <label>
          {key}:
          <textarea
            value={value}
            onChange={(e) => handlePromptChange(key, e.target.value)}
            rows={4}
            cols={50}
          />
        </label>
      </div>
    );
  };

  const filteredSettings = Object.entries(settingsCategories).reduce((acc, [category, keys]) => {
    const filteredKeys = keys.filter(key => 
      key.toLowerCase().includes(searchTerm.toLowerCase()) || 
      settingsDescriptions[key].toLowerCase().includes(searchTerm.toLowerCase())
    );
    if (filteredKeys.length > 0) {
      acc[category] = filteredKeys;
    }
    return acc;
  }, {});

  const handleExportSettings = () => {
    const settingsJson = JSON.stringify(currentProject ? projectSettings : localSettings, null, 2);
    const blob = new Blob([settingsJson], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = currentProject ? `${currentProject}_settings.json` : 'global_settings.json';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const handleImportSettings = (event) => {
    const file = event.target.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (e) => {
        try {
          const importedSettings = JSON.parse(e.target.result);
          if (currentProject) {
            setProjectSettings(importedSettings);
            debouncedUpdateProjectSettings(importedSettings);
          } else {
            setLocalSettings(importedSettings);
            debouncedUpdateSettings(importedSettings);
          }
        } catch (error) {
          setError('Failed to import settings. Invalid file format.');
          console.error('Error importing settings:', error);
        }
      };
      reader.readAsText(file);
    }
  };

  const handleCreateProject = async () => {
    const projectName = prompt('Enter the name for the new project:');
    if (projectName) {
      setIsLoading(true);
      setError(null);
      try {
        const response = await fetch(`${apiEndpoint}/create_project`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ project_name: projectName }),
        });
        if (!response.ok) {
          throw new Error('Failed to create project');
        }
        await fetchProjects();
        setCurrentProject(projectName);
        fetchProjectSettings(projectName);
        fetchProjectPrompts(projectName);
      } catch (error) {
        console.error('Error creating project:', error);
        setError('Failed to create project. Please try again.');
      } finally {
        setIsLoading(false);
      }
    }
  };

  const handleDeleteProject = async () => {
    if (currentProject && window.confirm(`Are you sure you want to delete the project "${currentProject}"?`)) {
      setIsLoading(true);
      setError(null);
      try {
        const response = await fetch(`${apiEndpoint}/delete_project`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ project_name: currentProject }),
        });
        if (!response.ok) {
          throw new Error('Failed to delete project');
        }
        await fetchProjects();
        setCurrentProject(null);
        setProjectSettings({});
        setPrompts({});
      } catch (error) {
        console.error('Error deleting project:', error);
        setError('Failed to delete project. Please try again.');
      } finally {
        setIsLoading(false);
      }
    }
  };

  return (
    <div className="settings-panel">
      <h3>Settings</h3>
      <div className="project-selector">
        <select
          value={currentProject || ''}
          onChange={(e) => {
            const selectedProject = e.target.value;
            setCurrentProject(selectedProject);
            if (selectedProject) {
              fetchProjectSettings(selectedProject);
              fetchProjectPrompts(selectedProject);
            }
          }}
        >
          <option value="">Global Settings</option>
          {projects.map((project) => (
            <option key={project} value={project}>
              {project}
            </option>
          ))}
        </select>
        <button onClick={handleCreateProject} title="Create New Project">
          <FaPlus /> New Project
        </button>
        {currentProject && (
          <button onClick={handleDeleteProject} title="Delete Current Project">
            <FaTrash /> Delete Project
          </button>
        )}
      </div>
      <div className="settings-actions">
        <div className="search-bar">
          <FaSearch />
          <input
            type="text"
            placeholder="Search settings..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>
        <button onClick={handleExportSettings} title="Export Settings">
          <FaDownload /> Export
        </button>
        <label htmlFor="import-settings" className="button" title="Import Settings">
          <FaUpload /> Import
          <input
            id="import-settings"
            type="file"
            accept=".json"
            style={{ display: 'none' }}
            onChange={handleImportSettings}
          />
        </label>
        <button onClick={resetToDefaults} disabled={isLoading}>
          Reset to Defaults
        </button>
      </div>
      {isLoading && <p>Updating settings...</p>}
      {error && <p className="error-message">{error}</p>}
      {Object.entries(filteredSettings).map(([category, keys]) => (
        <div key={category} className="settings-category">
          <h4>{category.charAt(0).toUpperCase() + category.slice(1)}</h4>
          {keys.map((key) => 
            renderSetting(key, currentProject ? projectSettings[key] : localSettings[key], !!currentProject)
          )}
        </div>
      ))}
      {currentProject && (
        <div className="settings-category">
          <h4>Custom Prompts</h4>
          {Object.entries(prompts).map(([key, value]) => renderPrompt(key, value))}
        </div>
      )}
    </div>
  );
}

function debounce(func, delay) {
  let timeoutId;
  return (...args) => {
    clearTimeout(timeoutId);
    timeoutId = setTimeout(() => func(...args), delay);
  };
}

export default SettingsPanel;