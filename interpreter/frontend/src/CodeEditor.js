import React, { useState, useCallback, useRef } from 'react';
import { Light as SyntaxHighlighter } from 'react-syntax-highlighter';
import { docco } from 'react-syntax-highlighter/dist/esm/styles/hljs';
import python from 'react-syntax-highlighter/dist/esm/languages/hljs/python';
import javascript from 'react-syntax-highlighter/dist/esm/languages/hljs/javascript';
import bash from 'react-syntax-highlighter/dist/esm/languages/hljs/bash';

SyntaxHighlighter.registerLanguage('python', python);
SyntaxHighlighter.registerLanguage('javascript', javascript);
SyntaxHighlighter.registerLanguage('bash', bash);

const MAX_RETRIES = 3;
const RETRY_DELAY = 1000;

function CodeEditor({ apiEndpoint }) {
  const [code, setCode] = useState('');
  const [output, setOutput] = useState('');
  const [language, setLanguage] = useState('python');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [savedSnippets, setSavedSnippets] = useState({});
  const abortControllerRef = useRef(null);

  const handleCodeChange = (e) => {
    setCode(e.target.value);
  };

  const handleLanguageChange = (e) => {
    setLanguage(e.target.value);
  };

  const runCode = useCallback(async (retryCount = 0) => {
    setIsLoading(true);
    setError(null);
    setOutput('');

    try {
      abortControllerRef.current = new AbortController();
      const response = await fetch(`${apiEndpoint}/run_code`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ code, language }),
        signal: abortControllerRef.current.signal,
      });

      if (!response.ok) {
        throw new Error('Network response was not ok');
      }

      const result = await response.json();
      setOutput(result.join('\n'));
      setIsLoading(false);
    } catch (error) {
      console.error('Error:', error);
      if (error.name === 'AbortError') {
        setError('Code execution was cancelled.');
      } else if (retryCount < MAX_RETRIES) {
        setTimeout(() => runCode(retryCount + 1), RETRY_DELAY);
      } else {
        setError('An error occurred while running the code. Please try again.');
      }
      setIsLoading(false);
    }
  }, [apiEndpoint, code, language]);

  const handleRunCode = () => {
    runCode();
  };

  const handleCancelExecution = () => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      setIsLoading(false);
      setError('Code execution was cancelled.');
    }
  };

  const handleSaveSnippet = () => {
    const snippetName = prompt('Enter a name for this code snippet:');
    if (snippetName) {
      setSavedSnippets(prevSnippets => ({
        ...prevSnippets,
        [snippetName]: { code, language }
      }));
    }
  };

  const handleLoadSnippet = (snippetName) => {
    const snippet = savedSnippets[snippetName];
    if (snippet) {
      setCode(snippet.code);
      setLanguage(snippet.language);
    }
  };

  return (
    <div className="code-editor">
      <div className="editor-controls">
        <select value={language} onChange={handleLanguageChange}>
          <option value="python">Python</option>
          <option value="javascript">JavaScript</option>
          <option value="bash">Bash</option>
        </select>
        <button onClick={handleSaveSnippet}>Save Snippet</button>
        <select onChange={(e) => handleLoadSnippet(e.target.value)}>
          <option value="">Load Snippet</option>
          {Object.keys(savedSnippets).map(name => (
            <option key={name} value={name}>{name}</option>
          ))}
        </select>
      </div>
      <SyntaxHighlighter
        language={language}
        style={docco}
        customStyle={{
          height: '300px',
          overflow: 'auto',
          fontSize: '14px',
          lineHeight: '1.5',
          padding: '10px',
        }}
      >
        {code}
      </SyntaxHighlighter>
      <textarea
        value={code}
        onChange={handleCodeChange}
        placeholder="Enter your code here..."
        rows={10}
        cols={50}
        style={{
          position: 'absolute',
          top: 0,
          left: 0,
          width: '100%',
          height: '100%',
          opacity: 0,
          zIndex: 1,
        }}
      />
      <div className="execution-controls">
        <button onClick={handleRunCode} disabled={isLoading}>
          {isLoading ? 'Running...' : 'Run Code'}
        </button>
        {isLoading && (
          <button onClick={handleCancelExecution}>Cancel Execution</button>
        )}
      </div>
      <div className="output">
        <h4>Output:</h4>
        {isLoading && <p>Running code...</p>}
        {error && <p className="error">{error}</p>}
        <pre>{output}</pre>
      </div>
    </div>
  );
}

export default CodeEditor;