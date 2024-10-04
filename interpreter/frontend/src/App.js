import React, { useState, useEffect, useCallback } from 'react';
import ChatInterface from './ChatInterface';
import CodeEditor from './CodeEditor';
import FileBrowser from './FileBrowser';
import SettingsPanel from './SettingsPanel';
import DocumentationViewer from './DocumentationViewer';
import ProjectAnalyzer from './ProjectAnalyzer';
import './styles.css';

const API_BASE_URL = '/api';

function App() {
  const [config, setConfig] = useState(null);
  const [frontendConfig, setFrontendConfig] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [currentProject, setCurrentProject] = useState(null);
  const [projects, setProjects] = useState([]);

  const fetchSettings = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await fetch(`${API_BASE_URL}/get_settings`);
      if (!response.ok) {
        throw new Error('Failed to fetch settings');
      }
      const data = await response.json();
      setConfig(data.interpreter_settings);
      setFrontendConfig(data.frontend_config);
    } catch (err) {
      console.error('Error fetching settings:', err);
      setError('Failed to load settings. Please refresh the page and try again.');
    } finally {
      setIsLoading(false);
    }
  }, []);

  const fetchProjects = useCallback(async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/get_projects`);
      if (!response.ok) {
        throw new Error('Failed to fetch projects');
      }
      const data = await response.json();
      setProjects(data.projects);
      if (data.projects.length > 0 && !currentProject) {
        setCurrentProject(data.projects[0]);
      }
    } catch (err) {
      console.error('Error fetching projects:', err);
      setError('Failed to load projects. Please try again.');
    }
  }, [currentProject]);

  useEffect(() => {
    fetchSettings();
    fetchProjects();
  }, [fetchSettings, fetchProjects]);

  const handleProjectChange = (projectName) => {
    setCurrentProject(projectName);
  };

  if (isLoading) {
    return <div className="loading">Loading...</div>;
  }

  if (error) {
    return <div className="error">{error}</div>;
  }

  if (!config || !frontendConfig) {
    return <div className="error">Failed to load configuration. Please refresh the page and try again.</div>;
  }

  return (
    <div className="App container">
      <h1>{config.project_name || "Open Interpreter"}</h1>
      <div className="project-selector">
        <select value={currentProject || ''} onChange={(e) => handleProjectChange(e.target.value)}>
          <option value="">Select a project</option>
          {projects.map((project) => (
            <option key={project} value={project}>
              {project}
            </option>
          ))}
        </select>
      </div>
      <div className="main-content">
        <ChatInterface apiEndpoint={`${API_BASE_URL}/chat`} currentProject={currentProject} />
        <CodeEditor apiEndpoint={`${API_BASE_URL}/run_code`} currentProject={currentProject} />
        <FileBrowser apiEndpoint={API_BASE_URL} currentProject={currentProject} />
        <SettingsPanel apiEndpoint={API_BASE_URL} currentProject={currentProject} />
        <DocumentationViewer apiEndpoint={API_BASE_URL} currentProject={currentProject} />
        <ProjectAnalyzer apiEndpoint={API_BASE_URL} currentProject={currentProject} />
      </div>
    </div>
  );
}

export default App;