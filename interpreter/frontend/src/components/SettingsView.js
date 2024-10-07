import React from 'react';

function SettingsView() {
  return (
    <div className="p-4 bg-white dark:bg-gray-800 rounded-lg shadow">
      <h2 className="text-2xl font-semibold mb-4 text-gray-800 dark:text-white">General Settings</h2>
      <div className="space-y-4">
        <div>
          <h3 className="text-lg font-medium mb-2 text-gray-700 dark:text-gray-300">API Configuration</h3>
          <input
            type="text"
            placeholder="API Key"
            className="w-full p-2 rounded bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-white"
          />
        </div>
        <div>
          <h3 className="text-lg font-medium mb-2 text-gray-700 dark:text-gray-300">Language Model</h3>
          <select
            className="w-full p-2 rounded bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-white"
          >
            <option>GPT-3.5</option>
            <option>GPT-4</option>
            <option>Claude</option>
          </select>
        </div>
        <div>
          <h3 className="text-lg font-medium mb-2 text-gray-700 dark:text-gray-300">Theme</h3>
          <div className="flex items-center space-x-4">
            <label className="flex items-center">
              <input type="radio" name="theme" value="light" className="mr-2" />
              <span className="text-gray-700 dark:text-gray-300">Light</span>
            </label>
            <label className="flex items-center">
              <input type="radio" name="theme" value="dark" className="mr-2" />
              <span className="text-gray-700 dark:text-gray-300">Dark</span>
            </label>
          </div>
        </div>
      </div>
    </div>
  );
}

export default SettingsView;