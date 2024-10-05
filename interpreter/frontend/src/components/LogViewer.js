import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';

const LogViewer = () => {
  const [logs, setLogs] = useState([]);
  const [filteredLogs, setFilteredLogs] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [filter, setFilter] = useState({ level: '', module: '', keyword: '' });

  const fetchLogs = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await axios.get('/api/get_logs', { params: filter });
      setLogs(response.data.logs);
    } catch (err) {
      setError('Failed to fetch logs. Please try again.');
      console.error('Error fetching logs:', err);
    } finally {
      setLoading(false);
    }
  }, [filter]);

  useEffect(() => {
    fetchLogs();
  }, [fetchLogs]);

  useEffect(() => {
    setFilteredLogs(logs);
  }, [logs]);

  const handleFilterChange = (e) => {
    setFilter({ ...filter, [e.target.name]: e.target.value });
  };

  const handleLevelFilter = (level) => {
    setFilter({ ...filter, level });
  };

  const handleRefresh = () => {
    fetchLogs();
  };

  return (
    <div className="log-viewer">
      <h2>Log Viewer</h2>
      <div className="filters">
        <input
          type="text"
          name="module"
          placeholder="Filter by module"
          value={filter.module}
          onChange={handleFilterChange}
        />
        <input
          type="text"
          name="keyword"
          placeholder="Search logs"
          value={filter.keyword}
          onChange={handleFilterChange}
        />
        <button onClick={() => handleLevelFilter('INFO')}>INFO</button>
        <button onClick={() => handleLevelFilter('WARNING')}>WARNING</button>
        <button onClick={() => handleLevelFilter('ERROR')}>ERROR</button>
        <button onClick={() => handleLevelFilter('')}>All Levels</button>
        <button onClick={handleRefresh} disabled={loading}>Refresh Logs</button>
      </div>
      {loading && <p>Loading logs...</p>}
      {error && <p className="error">{error}</p>}
      <ul className="log-list">
        {filteredLogs.map((log, index) => (
          <li key={index} className={`log-item ${log.level.toLowerCase()}`}>
            <span className="timestamp">{log.timestamp}</span>
            <span className="level">{log.level}</span>
            <span className="module">{log.module}</span>
            <span className="message">{log.message}</span>
          </li>
        ))}
      </ul>
    </div>
  );
};

export default LogViewer;