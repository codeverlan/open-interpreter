import React, { useState, useEffect, useCallback } from 'react';
import ChatInterface from './ChatInterface';
import CodeEditor from './CodeEditor';
import FileBrowser from './FileBrowser';
import SettingsPanel from './SettingsPanel';
import DocumentationViewer from './DocumentationViewer';
import ProjectAnalyzer from './ProjectAnalyzer';
import './styles.css';

const API_BASE_URL = '/api';

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null, errorInfo: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true };
  }

  componentDidCatch(error, errorInfo) {
    this.setState({
      error: error,
      errorInfo: errorInfo
    });
    console.error("Uncaught error:", error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div>
          <h1>Something went wrong.</h1>
          <details style={{ whiteSpace: 'pre-wrap' }}>
            {this.state.error && this.state.error.toString()}
            <br />
            {this.state.errorInfo.componentStack}
          </details>
        </div>
      );
    }

    return this.props.children;
  }
}

function App() {
  const [config, setConfig] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [currentProject, setCurrentProject] = useState(null);
  const [projects, setProjects] = useState([]);
  const [files, setFiles] = useState([]);
  const [currentPath, setCurrentPath] = useState('/');

  const fetchSettings = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await fetch(`${API_BASE_URL}/get_settings`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      console.log('Received settings data:', data);
      if (data.success) {
        setConfig(data.settings);
      } else {
        throw new Error('Settings data is not in the expected format');
      }
    } catch (err) {
      console.error('Error fetching settings:', err);
      setError(`Failed to load settings: ${err.message}`);
    } finally {
      setIsLoading(false);
    }
  }, []);

  const fetchProjects = useCallback(async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/get_projects`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      console.log('Received projects data:', data);
      if (data.success) {
        setProjects(data.projects);
        if (data.projects.length > 0 && !currentProject) {
          setCurrentProject(data.projects[0]);
        }
      } else {
        throw new Error('Projects data is not in the expected format');
      }
    } catch (err) {
      console.error('Error fetching projects:', err);
      setError(`Failed to load projects: ${err.message}`);
    }
  }, [currentProject]);

  const fetchFiles = useCallback(async (path = '/') => {
    try {
      const response = await fetch(`${API_BASE_URL}/list_files?path=${encodeURIComponent(path)}`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      console.log('Received files data:', data);
      if (data.success) {
        setFiles(data.files);
        setCurrentPath(path);
      } else {
        throw new Error('Files data is not in the expected format');
      }
    } catch (err) {
      console.error('Error fetching files:', err);
      setError(`Failed to load files: ${err.message}`);
    }
  }, []);

  useEffect(() => {
    fetchSettings();
    fetchProjects();
    fetchFiles(currentPath);
  }, [fetchSettings, fetchProjects, fetchFiles, currentPath]);

  const handleProjectChange = (projectName) => {
    setCurrentProject(projectName);
    setCurrentPath('/');
    fetchFiles('/');
  };

  const handleFileSelect = (path) => {
    fetchFiles(path);
  };

  if (isLoading) {
    return <div className="loading">Loading...</div>;
  }

  if (error) {
    return <div className="error">{error}</div>;
  }

  if (!config) {
    return <div className="error">Failed to load configuration. Please refresh the page and try again.</div>;
  }

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
          <FileBrowser files={files} onFileSelect={handleFileSelect} currentPath={currentPath} />
          <SettingsPanel apiEndpoint={API_BASE_URL} currentProject={currentProject} />
          <DocumentationViewer apiEndpoint={API_BASE_URL} currentProject={currentProject} />
          <ProjectAnalyzer apiEndpoint={API_BASE_URL} currentProject={currentProject} />
        </div>
      </div>
    </ErrorBoundary>
  );
}

export default App;