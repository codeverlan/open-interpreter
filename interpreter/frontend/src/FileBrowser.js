import React from 'react';
import { FaFolder, FaFile, FaArrowUp } from 'react-icons/fa';

const FileBrowser = ({ files, onFileSelect, currentPath }) => {
  const handleFileClick = (file) => {
    console.log('Clicked file:', file);
    try {
      const newPath = currentPath === '/' ? `/${file.name}` : `${currentPath}/${file.name}`;
      if (file.type === 'directory') {
        onFileSelect(newPath);
      } else {
        // Handle file selection (e.g., open file in editor)
        console.log(`Selected file: ${newPath}`);
      }
    } catch (error) {
      console.error('Error in handleFileClick:', error);
    }
  };

  const handleBackClick = () => {
    try {
      const parentPath = currentPath.split('/').slice(0, -1).join('/') || '/';
      onFileSelect(parentPath);
    } catch (error) {
      console.error('Error in handleBackClick:', error);
    }
  };

  console.log('Rendering FileBrowser with files:', files);

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
        {Array.isArray(files) ? files.map((file, index) => (
          <li key={index} onClick={() => handleFileClick(file)}>
            {file && typeof file === 'object' ? (
              <>
                {file.type === 'directory' ? <FaFolder /> : <FaFile />} {file.name}
              </>
            ) : (
              <span>Invalid file object</span>
            )}
          </li>
        )) : (
          <li>No files to display</li>
        )}
      </ul>
    </div>
  );
};

export default FileBrowser;