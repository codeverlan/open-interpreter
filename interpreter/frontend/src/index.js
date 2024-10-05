import React from 'react';
import ReactDOM from 'react-dom';
import './index.css';
import App from './App';

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

// Global error handler
window.onerror = function(message, source, lineno, colno, error) {
  const errorMessage = `Global error caught: ${message} (${source}:${lineno}:${colno})`;
  sendLog(errorMessage, 'error');
  console.error(errorMessage, error);
  return false;
};

sendLog('Starting to render the app');

const rootElement = document.getElementById('root');

if (rootElement) {
  try {
    ReactDOM.render(
      <React.StrictMode>
        <App />
      </React.StrictMode>,
      rootElement
    );
    sendLog('App rendered successfully');
  } catch (error) {
    const errorMessage = `Error during initial render: ${error.message}`;
    sendLog(errorMessage, 'error');
    console.error(errorMessage, error);
    rootElement.innerHTML = `
      <div style="color: red; text-align: center;">
        <h1>An error occurred while loading the application</h1>
        <p>Error details: ${error.message}</p>
        <p>Please check the console for more information and try refreshing the page.</p>
      </div>
    `;
  }
} else {
  const errorMessage = 'Root element not found';
  sendLog(errorMessage, 'error');
  console.error(errorMessage);
  document.body.innerHTML = '<div style="color: red; text-align: center;"><h1>Unable to load the application. The root element is missing.</h1></div>';
}

// Add an unhandled promise rejection handler
window.addEventListener('unhandledrejection', function(event) {
  const errorMessage = `Unhandled promise rejection: ${event.reason}`;
  sendLog(errorMessage, 'error');
  console.error(errorMessage);
});

// Log when the script has finished executing
sendLog('index.js: Script finished');