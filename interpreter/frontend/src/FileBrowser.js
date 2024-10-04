import React, { useState } from 'react';
import { FaFolder, FaFile, FaArrowUp } from 'react-icons/fa';

const FileBrowser = ({ files, onFileSelect }) => {
  const [currentPath, setCurrentPath] = useState('/');

  const handleFileClick = (file) => {
    const newPath = currentPath === '/' ? `/${file}` : `${currentPath}/${file}`;
    if (file.endsWith('/')) {
      setCurrentPath(newPath);
      onFileSelect(newPath);
    } else {
      // Handle file selection (e.g., open file in editor)
      console.log(`Selected file: ${newPath}`);
    }
  };

  const handleBackClick = () => {
    const parentPath = currentPath.split('/').slice(0, -1).join('/') || '/';
    setCurrentPath(parentPath);
    onFileSelect(parentPath);
  };

  return (
    <div className="file-browser">
      <h2>File Browser</h2>
      <div className="current-path">{currentPath}</div>
      <ul>
        {currentPath !== '/' && (
          <li onClick={handleBackClick}>
            <FaArrowUp /> ..
          </li>
        )}
        {files.map((file, index) => (
          <li key={index} onClick={() => handleFileClick(file)}>
            {file.endsWith('/') ? (
              <>
                <FaFolder /> {file}
              </>
            ) : (
              <>
                <FaFile /> {file}
              </>
            )}
          </li>
        ))}
      </ul>
    </div>
  );
};

export default FileBrowser;