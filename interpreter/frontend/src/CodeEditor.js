import React, { useState } from 'react';

function CodeEditor({ apiEndpoint }) {
  const [code, setCode] = useState('');
  const [output, setOutput] = useState('');
  const [language, setLanguage] = useState('python');

  const handleCodeChange = (e) => {
    setCode(e.target.value);
  };

  const handleLanguageChange = (e) => {
    setLanguage(e.target.value);
  };

  const handleRunCode = () => {
    setOutput('Running code...');
    fetch(apiEndpoint, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ code, language }),
    })
      .then(response => response.json())
      .then(data => {
        setOutput(data.map(item => item.content).join('\n'));
      })
      .catch(error => {
        console.error('Error:', error);
        setOutput('An error occurred while running the code.');
      });
  };

  return (
    <div className="code-editor">
      <select value={language} onChange={handleLanguageChange}>
        <option value="python">Python</option>
        <option value="javascript">JavaScript</option>
        <option value="shell">Shell</option>
      </select>
      <textarea
        value={code}
        onChange={handleCodeChange}
        placeholder="Enter your code here..."
        rows={10}
        cols={50}
      />
      <button onClick={handleRunCode}>Run Code</button>
      <div className="output">
        <h4>Output:</h4>
        <pre>{output}</pre>
      </div>
    </div>
  );
}

export default CodeEditor;