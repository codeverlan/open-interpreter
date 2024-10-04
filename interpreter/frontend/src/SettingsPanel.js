import React, { useState, useEffect } from 'react';

function SettingsPanel({ settings, onSettingsUpdate }) {
  const [localSettings, setLocalSettings] = useState(settings);

  useEffect(() => {
    setLocalSettings(settings);
  }, [settings]);

  const handleSettingChange = (key, value) => {
    const updatedSettings = { ...localSettings, [key]: value };
    setLocalSettings(updatedSettings);
    onSettingsUpdate(updatedSettings);
  };

  return (
    <div className="settings-panel">
      <h3>Settings</h3>
      {Object.entries(localSettings).map(([key, value]) => (
        <div key={key}>
          <label>
            {key}:
            {typeof value === 'boolean' ? (
              <input
                type="checkbox"
                checked={value}
                onChange={(e) => handleSettingChange(key, e.target.checked)}
              />
            ) : typeof value === 'number' ? (
              <input
                type="number"
                value={value}
                onChange={(e) => handleSettingChange(key, Number(e.target.value))}
              />
            ) : (
              <input
                type="text"
                value={value}
                onChange={(e) => handleSettingChange(key, e.target.value)}
              />
            )}
          </label>
        </div>
      ))}
    </div>
  );
}

export default SettingsPanel;