import React, { useState, useEffect } from 'react';
import Sidebar from './components/Sidebar';
import Header from './components/Header';
import ProjectList from './components/ProjectList';
import AgentsView from './components/AgentsView';
import SettingsView from './components/SettingsView';

function App() {
  const [darkMode, setDarkMode] = useState(false);
  const [currentView, setCurrentView] = useState('projects');
  const [projects, setProjects] = useState([
    { id: 1, name: 'Project 1', lastOpened: '2 days ago' },
    { id: 2, name: 'Project 2', lastOpened: '1 week ago' },
    { id: 3, name: 'Project 3', lastOpened: '3 weeks ago' },
  ]);

  useEffect(() => {
    if (darkMode) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, [darkMode]);

  const handleCreateProject = () => {
    const newProject = {
      id: projects.length + 1,
      name: `Project ${projects.length + 1}`,
      lastOpened: 'Just now'
    };
    setProjects([...projects, newProject]);
  };

  const handleOpenProject = (id) => {
    console.log('Open project', id);
  };

  const handleProjectSettings = (id) => {
    console.log('Project settings', id);
  };

  const handleDeleteProject = (id) => {
    setProjects(projects.filter(project => project.id !== id));
  };

  const renderView = () => {
    switch (currentView) {
      case 'projects':
        return (
          <ProjectList
            projects={projects}
            onOpenProject={handleOpenProject}
            onProjectSettings={handleProjectSettings}
            onDeleteProject={handleDeleteProject}
          />
        );
      case 'agents':
        return <AgentsView />;
      case 'settings':
        return <SettingsView />;
      default:
        return <div>404 Not Found</div>;
    }
  };

  return (
    <div className="min-h-screen bg-gray-100 dark:bg-gray-900 dark:text-white">
      <div className="flex">
        <Sidebar setCurrentView={setCurrentView} />
        <main className="flex-1 p-8">
          <Header
            darkMode={darkMode}
            setDarkMode={setDarkMode}
            onCreateProject={handleCreateProject}
          />
          {renderView()}
        </main>
      </div>
    </div>
  );
}

export default App;
