import React, { useState, useEffect, useCallback } from 'react';
import ChatInterface from './ChatInterface';
import FileBrowser from './FileBrowser';
import SettingsPanel from './SettingsPanel';
import DocumentationViewer from './DocumentationViewer';
import ProjectOutline from './components/ProjectOutline';
import PromptManager from './components/PromptManager';
import Terminal from './components/Terminal';
import AgentManager from './components/AgentManager';
import ProjectCreator from './components/ProjectCreator';
import './styles.css';

const API_BASE_URL = '/api';

// Function to send logs to the server
const sendLog = async (message, level = 'info') => {
  try {
    await fetch(`${API_BASE_URL}/log`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ message, level, timestamp: new Date().toISOString() }),
    });
  } catch (error) {
    console.error('Failed to send log to server:', error);
  }
};

// Override console methods to send logs to the server
const originalConsole = { ...console };
console.log = (...args) => {
  sendLog(args.join(' '), 'info');
  originalConsole.log(...args);
};
console.error = (...args) => {
  sendLog(args.join(' '), 'error');
  originalConsole.error(...args);
};
console.warn = (...args) => {
  sendLog(args.join(' '), 'warn');
  originalConsole.warn(...args);
};

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null, errorInfo: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    this.setState({
      error: error,
      errorInfo: errorInfo
    });
    sendLog(`Uncaught error: ${error}\n${errorInfo?.componentStack || 'No component stack available'}`, 'error');
  }

  render() {
    if (this.state.hasError) {
      return (
        <div>
          <h1>Something went wrong.</h1>
          <details style={{ whiteSpace: 'pre-wrap' }}>
            {this.state.error && this.state.error.toString()}
            <br />
            {this.state.errorInfo && this.state.errorInfo.componentStack}
          </details>
        </div>
      );
    }

    return this.props.children;
  }
}

function App() {
  sendLog('App: Component function started');
  const [config, setConfig] = useState({ project_name: "Open Interpreter" });
  const [isLoading, setIsLoading] = useState({
    settings: true,
    projects: true,
    files: false
  });
  const [error, setError] = useState(null);
  const [currentProject, setCurrentProject] = useState(null);
  const [projects, setProjects] = useState([]);
  const [files, setFiles] = useState([]);
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [currentPath, setCurrentPath] = useState('/');
  const [activeTab, setActiveTab] = useState('chat');

  const handleApiError = useCallback((err, context) => {
    const errorMessage = `App: Error in ${context}: ${err.message}`;
    sendLog(errorMessage, 'error');
    setError(errorMessage);
    setIsLoading(prevState => ({...prevState, [context.toLowerCase()]: false}));
  }, []);

  const fetchSettings = useCallback(async () => {
    sendLog('App: fetchSettings started');
    setIsLoading(prevState => ({...prevState, settings: true}));
    setError(null);
    try {
      const response = await fetch(`${API_BASE_URL}/get_settings`);
      sendLog(`App: fetchSettings response status: ${response.status}`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      sendLog(`App: Received settings data: ${JSON.stringify(data)}`);
      if (data.success) {
        setConfig(data.settings);
        sendLog('App: Settings updated successfully');
      } else {
        throw new Error(data.error || 'Failed to fetch settings');
      }
    } catch (err) {
      handleApiError(err, 'Settings');
    } finally {
      setIsLoading(prevState => ({...prevState, settings: false}));
      sendLog('App: fetchSettings completed');
    }
  }, [handleApiError]);

  const fetchProjects = useCallback(async () => {
    sendLog('App: fetchProjects started');
    setIsLoading(prevState => ({...prevState, projects: true}));
    try {
      const response = await fetch(`${API_BASE_URL}/get_projects`);
      sendLog(`App: fetchProjects response status: ${response.status}`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      sendLog(`App: Received projects data: ${JSON.stringify(data)}`);
      if (data.success) {
        setProjects(data.projects);
        if (data.projects.length > 0 && !currentProject) {
          setCurrentProject(data.projects[0].id);
          sendLog(`App: Current project set to: ${data.projects[0].id}`);
        }
      } else {
        throw new Error(data.error || 'Failed to fetch projects');
      }
    } catch (err) {
      handleApiError(err, 'Projects');
    } finally {
      setIsLoading(prevState => ({...prevState, projects: false}));
      sendLog('App: fetchProjects completed');
    }
  }, [currentProject, handleApiError]);

  const fetchFiles = useCallback(async (path = '/') => {
    sendLog(`App: fetchFiles started with path: ${path}`);
    setIsLoading(prevState => ({...prevState, files: true}));
    try {
      const response = await fetch(`${API_BASE_URL}/list_files?path=${encodeURIComponent(path)}`);
      sendLog(`App: fetchFiles response status: ${response.status}`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      sendLog(`App: Received files data: ${JSON.stringify(data)}`);
      if (data.success) {
        // Ensure all file names are strings
        const validFiles = data.files.filter(file => typeof file === 'string');
        setFiles(validFiles);
        setCurrentPath(path);
        sendLog('App: Files and current path updated');
      } else {
        throw new Error(data.error || 'Failed to fetch files');
      }
    } catch (err) {
      handleApiError(err, 'Files');
    } finally {
      setIsLoading(prevState => ({...prevState, files: false}));
      sendLog('App: fetchFiles completed');
    }
  }, [handleApiError]);

  useEffect(() => {
    sendLog('App: useEffect for fetchSettings and fetchProjects started');
    fetchSettings();
    fetchProjects();
    sendLog('App: useEffect for fetchSettings and fetchProjects completed');
  }, [fetchSettings, fetchProjects]);

  useEffect(() => {
    sendLog('App: useEffect for fetchFiles started');
    if (currentProject) {
      fetchFiles(currentPath);
    }
    sendLog('App: useEffect for fetchFiles completed');
  }, [fetchFiles, currentPath, currentProject]);

  const handleProjectChange = (projectId) => {
    sendLog(`App: handleProjectChange called with: ${projectId}`);
    setCurrentProject(projectId);
    setCurrentPath('/');
    fetchFiles('/');
  };

  const handleFileSelect = (path) => {
    sendLog(`App: handleFileSelect called with: ${path}`);
    fetchFiles(path);
  };

  const handleFileCheck = (file, isChecked) => {
    sendLog(`App: handleFileCheck called with: ${file}, ${isChecked}`);
    if (isChecked) {
      setSelectedFiles(prev => [...prev, file]);
    } else {
      setSelectedFiles(prev => prev.filter(f => f !== file));
    }
  };

  const handleProjectCreated = (newProject) => {
    sendLog(`App: handleProjectCreated called with: ${JSON.stringify(newProject)}`);
    setProjects([...projects, newProject]);
    setCurrentProject(newProject.id);
  };

  sendLog('App: Rendering main content');
  sendLog(`App: Current state - isLoading: ${JSON.stringify(isLoading)}, error: ${error}, config: ${JSON.stringify(config)}`);

  if (isLoading.settings || isLoading.projects) {
    sendLog('App: Rendering loading state');
    return <div className="loading">Loading application data...</div>;
  }

  if (error) {
    sendLog('App: Rendering error state');
    return <div className="error">{error}</div>;
  }

  sendLog('App: Rendering main content');
  return (
    <ErrorBoundary>
      <div className="App container" style={{ backgroundColor: '#f0f0f0', color: '#333' }}>
        <h1>{config.project_name || "Open Interpreter"}</h1>
        <div className="project-selector">
          <select value={currentProject || ''} onChange={(e) => handleProjectChange(e.target.value)}>
            <option value="">Select a project</option>
            {projects.map((project) => (
              <option key={project.id} value={project.id}>
                {project.name}
              </option>
            ))}
          </select>
          <ProjectCreator onProjectCreated={handleProjectCreated} />
        </div>
        <nav>
          <button onClick={() => setActiveTab('chat')} style={{ fontSize: '1.2em', padding: '10px 20px' }}>Chat</button>
          <button onClick={() => setActiveTab('files')} style={{ fontSize: '1.2em', padding: '10px 20px' }}>Files</button>
          <button onClick={() => setActiveTab('agents')} style={{ fontSize: '1.2em', padding: '10px 20px' }}>Agents</button>
          <button onClick={() => setActiveTab('docs')} style={{ fontSize: '1.2em', padding: '10px 20px' }}>Docs</button>
          <button onClick={() => setActiveTab('outline')} style={{ fontSize: '1.2em', padding: '10px 20px' }}>Outline</button>
          <button onClick={() => setActiveTab('prompts')} style={{ fontSize: '1.2em', padding: '10px 20px' }}>Prompts</button>
          <button onClick={() => setActiveTab('terminal')} style={{ fontSize: '1.2em', padding: '10px 20px' }}>Terminal</button>
          <button onClick={() => setActiveTab('settings')} style={{ fontSize: '1.2em', padding: '10px 20px' }}>Settings</button>
        </nav>
        <div className="main-content">
          {activeTab === 'chat' && <ChatInterface apiEndpoint={`${API_BASE_URL}/chat`} currentProject={currentProject} selectedFiles={selectedFiles} />}
          {activeTab === 'files' && (
            isLoading.files ? (
              <div className="loading">Loading files...</div>
            ) : (
              <ErrorBoundary>
                <FileBrowser 
                  files={files} 
                  onFileSelect={handleFileSelect} 
                  currentPath={currentPath} 
                  onFileCheck={handleFileCheck}
                  selectedFiles={selectedFiles}
                />
              </ErrorBoundary>
            )
          )}
          {activeTab === 'settings' && <SettingsPanel apiEndpoint={`${API_BASE_URL}/get_settings`} currentProject={currentProject} />}
          {activeTab === 'docs' && <DocumentationViewer apiEndpoint={API_BASE_URL} currentProject={currentProject} />}
          {activeTab === 'outline' && <ProjectOutline apiEndpoint={API_BASE_URL} currentProject={currentProject} />}
          {activeTab === 'prompts' && currentProject && (
            <ErrorBoundary>
              <PromptManager projectId={currentProject} />
            </ErrorBoundary>
          )}
          {activeTab === 'terminal' && <Terminal apiEndpoint={API_BASE_URL} />}
          {activeTab === 'agents' && <AgentManager />}
        </div>
      </div>
    </ErrorBoundary>
  );
}

export default App;
