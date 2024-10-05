import React, { useState, useEffect, useCallback } from 'react';
import ChatInterface from './ChatInterface';
import CodeEditor from './CodeEditor';
import FileBrowser from './FileBrowser';
import SettingsPanel from './SettingsPanel';
import DocumentationViewer from './DocumentationViewer';
import ProjectAnalyzer from './ProjectAnalyzer';
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
  const [config, setConfig] = useState(null);
  const [isLoading, setIsLoading] = useState({
    settings: true,
    projects: true,
    files: false
  });
  const [error, setError] = useState(null);
  const [currentProject, setCurrentProject] = useState(null);
  const [projects, setProjects] = useState([]);
  const [files, setFiles] = useState([]);
  const [currentPath, setCurrentPath] = useState('/');

  const handleApiError = (err, context) => {
    const errorMessage = `App: Error in ${context}: ${err.message}`;
    sendLog(errorMessage, 'error');
    setError(errorMessage);
    setIsLoading(prevState => ({...prevState, [context.toLowerCase()]: false}));
  };

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
  }, []);

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
          setCurrentProject(data.projects[0]);
          sendLog(`App: Current project set to: ${data.projects[0]}`);
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
  }, [currentProject]);

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
        const validFiles = data.files.filter(file => typeof file.name === 'string');
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
  }, []);

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

  const handleProjectChange = (projectName) => {
    sendLog(`App: handleProjectChange called with: ${projectName}`);
    setCurrentProject(projectName);
    setCurrentPath('/');
    fetchFiles('/');
  };

  const handleFileSelect = (path) => {
    sendLog(`App: handleFileSelect called with: ${path}`);
    fetchFiles(path);
  };

  sendLog('App: Rendering component');
  sendLog(`App: Current state - isLoading: ${JSON.stringify(isLoading)}, error: ${error}, config: ${JSON.stringify(config)}`);

  if (isLoading.settings || isLoading.projects) {
    sendLog('App: Rendering loading state');
    return <div className="loading">Loading application data...</div>;
  }

  if (error) {
    sendLog('App: Rendering error state');
    return <div className="error">{error}</div>;
  }

  if (!config) {
    sendLog('App: Rendering no config state');
    return <div className="error">Failed to load configuration. Please refresh the page and try again.</div>;
  }

  sendLog('App: Rendering main content');
  return (
    <ErrorBoundary>
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
          {isLoading.files ? (
            <div className="loading">Loading files...</div>
          ) : (
            <ErrorBoundary>
              <FileBrowser files={files} onFileSelect={handleFileSelect} currentPath={currentPath} />
            </ErrorBoundary>
          )}
          <SettingsPanel apiEndpoint={`${API_BASE_URL}/get_settings`} currentProject={currentProject} />
          <DocumentationViewer apiEndpoint={API_BASE_URL} currentProject={currentProject} />
          <ProjectAnalyzer apiEndpoint={API_BASE_URL} currentProject={currentProject} />
        </div>
      </div>
    </ErrorBoundary>
  );
}

export default App;
