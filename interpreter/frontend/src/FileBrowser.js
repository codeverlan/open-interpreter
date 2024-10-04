import React, { useState, useEffect } from 'react';

function FileBrowser({ apiEndpoint }) {
  const [files, setFiles] = useState([]);
  const [currentPath, setCurrentPath] = useState('/');

  useEffect(() => {
    fetchFiles(currentPath);
  }, [currentPath, apiEndpoint]);

  const fetchFiles = (path) => {
    fetch(`${apiEndpoint}?path=${encodeURIComponent(path)}`)
      .then(response => response.json())
      .then(data => {
        setFiles(data);
      })
      .catch(error => {
        console.error('Error fetching files:', error);
      });
  };

  const handleFileClick = (file) => {
    if (file.type === 'directory') {
      setCurrentPath(`${currentPath}${file.name}/`);
    } else {
      // TODO: Implement file opening logic
      console.log('Opening file:', file.name);
    }
  };

  const handleBackClick = () => {
    if (currentPath !== '/') {
      const newPath = currentPath.split('/').slice(0, -2).join('/') + '/';
      setCurrentPath(newPath);
    }
  };

  return (
    <div className="file-browser">
      <h3>Current Path: {currentPath}</h3>
      <button onClick={handleBackClick} disabled={currentPath === '/'}>Back</button>
      <ul>
        {files.map((file, index) => (
          <li key={index} onClick={() => handleFileClick(file)}>
            {file.name} ({file.type})
          </li>
        ))}
      </ul>
    </div>
  );
}

export default FileBrowser;