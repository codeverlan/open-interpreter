import React, { useState, useEffect } from 'react';
import axios from 'axios';

const ApiKeyManager = () => {
  const [apiKey, setApiKey] = useState('');
  const [message, setMessage] = useState('');
  const [isError, setIsError] = useState(false);

  useEffect(() => {
    // Clear message after 5 seconds
    const timer = setTimeout(() => {
      setMessage('');
      setIsError(false);
    }, 5000);

    return () => clearTimeout(timer);
  }, [message]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await axios.post('http://localhost:5159/api/set_api_key', { api_key: apiKey });
      if (response.data.success) {
        setMessage('API key set successfully');
        setIsError(false);
        setApiKey('');
        // Trigger a refresh of the AI models list
        // You'll need to implement this function in the parent component
        // and pass it down as a prop
        // refreshAiModels();
      } else {
        throw new Error(response.data.error || 'Failed to set API key');
      }
    } catch (error) {
      setMessage('Error setting API key: ' + error.message);
      setIsError(true);
    }
  };

  return (
    <div className="api-key-manager">
      <h2>API Key Management</h2>
      <form onSubmit={handleSubmit}>
        <input
          type="password"
          value={apiKey}
          onChange={(e) => setApiKey(e.target.value)}
          placeholder="Enter OpenRouter API Key"
          required
        />
        <button type="submit">Set API Key</button>
      </form>
      {message && (
        <p className={isError ? 'error-message' : 'success-message'}>
          {message}
        </p>
      )}
    </div>
  );
};

export default ApiKeyManager;