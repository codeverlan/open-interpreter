import React, { useState, useEffect } from 'react';
import ChatInterface from './ChatInterface';
import CodeEditor from './CodeEditor';
import FileBrowser from './FileBrowser';
import SettingsPanel from './SettingsPanel';

function App() {
  const [config, setConfig] = useState(null);
  const [frontendConfig, setFrontendConfig] = useState(null);

  useEffect(() => {
    fetch('/api/get_settings')
      .then(response => response.json())
      .then(data => {
        setConfig(data.interpreter_config);
        setFrontendConfig(data.frontend_config);
      });
  }, []);

  const handleSettingsUpdate = (newSettings) => {
    fetch('/api/update_settings', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ interpreter_config: newSettings }),
    })
      .then(response => response.json())
      .then(data => {
        if (data.status === 'success') {
          setConfig(newSettings);
        }
      });
  };

  if (!config || !frontendConfig) {
    return <div>Loading...</div>;
  }

  return (
    <div className="App" style={{ color: frontendConfig.theme.primary_color }}>
      <h1>{config.project?.name || "Open Interpreter"}</h1>
      <div className="main-content">
        {frontendConfig.components.includes('chat_interface') && <ChatInterface apiEndpoint={frontendConfig.api.chat_endpoint} />}
        {frontendConfig.components.includes('code_editor') && <CodeEditor apiEndpoint={frontendConfig.api.run_code_endpoint} />}
        {frontendConfig.components.includes('file_browser') && <FileBrowser apiEndpoint={frontendConfig.api.get_files_endpoint} />}
        {frontendConfig.components.includes('settings_panel') && <SettingsPanel settings={config} onSettingsUpdate={handleSettingsUpdate} />}
      </div>
    </div>
  );
}

export default App;