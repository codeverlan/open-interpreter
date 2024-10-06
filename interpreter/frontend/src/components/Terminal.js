import React, { useState, useEffect, useRef } from 'react';

const Terminal = ({ apiEndpoint }) => {
  const [logs, setLogs] = useState([]);
  const [command, setCommand] = useState('');
  const logEndRef = useRef(null);

  useEffect(() => {
    const fetchLogs = async () => {
      try {
        const response = await fetch(`${apiEndpoint}/get_logs`);
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        if (data.success) {
          setLogs(data.logs);
        } else {
          throw new Error(data.error || 'Failed to fetch logs');
        }
      } catch (error) {
        console.error('Error fetching logs:', error);
      }
    };

    fetchLogs();
    const intervalId = setInterval(fetchLogs, 5000); // Fetch logs every 5 seconds

    return () => clearInterval(intervalId);
  }, [apiEndpoint]);

  useEffect(() => {
    logEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [logs]);

  const handleCommandSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await fetch(`${apiEndpoint}/execute_command`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ command }),
      });
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      if (data.success) {
        setLogs(prevLogs => [...prevLogs, { type: 'command', content: command }, { type: 'output', content: data.output }]);
        if (data.error) {
          setLogs(prevLogs => [...prevLogs, { type: 'error', content: data.error }]);
        }
        setCommand('');
      } else {
        throw new Error(data.error || 'Failed to execute command');
      }
    } catch (error) {
      console.error('Error executing command:', error);
      setLogs(prevLogs => [...prevLogs, { type: 'error', content: error.message }]);
    }
  };

  return (
    <div className="terminal">
      <h2>Terminal</h2>
      <div className="terminal-output">
        {logs.map((log, index) => (
          <div key={index} className={`log-entry ${log.type}`}>
            {log.type === 'command' ? '> ' : ''}{log.content}
          </div>
        ))}
        <div ref={logEndRef} />
      </div>
      <form onSubmit={handleCommandSubmit}>
        <input
          type="text"
          value={command}
          onChange={(e) => setCommand(e.target.value)}
          placeholder="Enter command..."
        />
        <button type="submit">Execute</button>
      </form>
    </div>
  );
};

export default Terminal;