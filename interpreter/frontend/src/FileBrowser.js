import React, { useState, useEffect, useCallback } from 'react';
import { FaFile, FaFolder, FaFolderOpen, FaTrash, FaPlus, FaEdit, FaDownload, FaUpload } from 'react-icons/fa';

const MAX_RETRIES = 3;
const RETRY_DELAY = 1000;

function FileBrowser({ apiEndpoint }) {
  const [files, setFiles] = useState([]);
  const [currentPath, setCurrentPath] = useState('/');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [selectedFile, setSelectedFile] = useState(null);
  const [fileContent, setFileContent] = useState('');
  const [isEditing, setIsEditing] = useState(false);

  const fetchWithRetry = useCallback(async (url, options, retryCount = 0) => {
    try {
      const response = await fetch(url, options);
      if (!response.ok) {
        throw new Error('Network response was not ok');
      }
      return response;
    } catch (error) {
      if (retryCount < MAX_RETRIES) {
        await new Promise(resolve => setTimeout(resolve, RETRY_DELAY));
        return fetchWithRetry(url, options, retryCount + 1);
      }
      throw error;
    }
  }, []);

  const fetchFiles = useCallback(async (path) => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await fetchWithRetry(`${apiEndpoint}/list_files?path=${encodeURIComponent(path)}`);
      const data = await response.json();
      setFiles(data);
    } catch (error) {
      console.error('Error fetching files:', error);
      setError('Failed to fetch files. Please try again.');
    } finally {
      setIsLoading(false);
    }
  }, [apiEndpoint, fetchWithRetry]);

  useEffect(() => {
    fetchFiles(currentPath);
  }, [currentPath, fetchFiles]);

  const handleFileClick = (file) => {
    if (file.type === 'directory') {
      setCurrentPath(`${currentPath}${file.name}/`);
    } else {
      setSelectedFile(file);
      fetchFileContent(`${currentPath}${file.name}`);
    }
  };

  const fetchFileContent = async (path) => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await fetchWithRetry(`${apiEndpoint}/read_file?path=${encodeURIComponent(path)}`);
      const content = await response.json();
      setFileContent(content);
    } catch (error) {
      console.error('Error fetching file content:', error);
      setError('Failed to fetch file content. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleBackClick = () => {
    if (currentPath !== '/') {
      const newPath = currentPath.split('/').slice(0, -2).join('/') + '/';
      setCurrentPath(newPath);
    }
  };

  const handleCreateItem = async (type) => {
    const name = prompt(`Enter ${type} name:`);
    if (name) {
      setIsLoading(true);
      setError(null);
      try {
        await fetchWithRetry(`${apiEndpoint}/create_directory`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ path: `${currentPath}${name}` }),
        });
        fetchFiles(currentPath);
      } catch (error) {
        console.error(`Error creating ${type}:`, error);
        setError(`Failed to create ${type}. Please try again.`);
      } finally {
        setIsLoading(false);
      }
    }
  };

  const handleDeleteItem = async (item) => {
    if (window.confirm(`Are you sure you want to delete ${item.name}?`)) {
      setIsLoading(true);
      setError(null);
      try {
        await fetchWithRetry(`${apiEndpoint}/delete_file`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ path: `${currentPath}${item.name}` }),
        });
        fetchFiles(currentPath);
      } catch (error) {
        console.error('Error deleting item:', error);
        setError('Failed to delete item. Please try again.');
      } finally {
        setIsLoading(false);
      }
    }
  };

  const handleEditFile = () => {
    setIsEditing(true);
  };

  const handleSaveFile = async () => {
    setIsLoading(true);
    setError(null);
    try {
      await fetchWithRetry(`${apiEndpoint}/write_file`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ path: `${currentPath}${selectedFile.name}`, content: fileContent }),
      });
      setIsEditing(false);
    } catch (error) {
      console.error('Error saving file:', error);
      setError('Failed to save file. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (file) {
      setIsLoading(true);
      setError(null);
      try {
        const formData = new FormData();
        formData.append('file', file);
        formData.append('path', currentPath);
        await fetchWithRetry(`${apiEndpoint}/write_file`, {
          method: 'POST',
          body: formData,
        });
        fetchFiles(currentPath);
      } catch (error) {
        console.error('Error uploading file:', error);
        setError('Failed to upload file. Please try again.');
      } finally {
        setIsLoading(false);
      }
    }
  };

  const handleFileDownload = async (file) => {
    try {
      const response = await fetchWithRetry(`${apiEndpoint}/read_file?path=${encodeURIComponent(`${currentPath}${file.name}`)}`);
      const content = await response.text();
      const blob = new Blob([content], { type: 'text/plain' });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = file.name;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Error downloading file:', error);
      setError('Failed to download file. Please try again.');
    }
  };

  return (
    <div className="file-browser">
      <h3>Current Path: {currentPath}</h3>
      <button onClick={handleBackClick} disabled={currentPath === '/'}>Back</button>
      <button onClick={() => handleCreateItem('file')}><FaPlus /> New File</button>
      <button onClick={() => handleCreateItem('directory')}><FaPlus /> New Folder</button>
      <input type="file" onChange={handleFileUpload} style={{ display: 'none' }} id="file-upload" />
      <label htmlFor="file-upload" className="button">
        <FaUpload /> Upload File
      </label>
      {isLoading && <p>Loading...</p>}
      {error && <p className="error">{error}</p>}
      <ul>
        {files.map((file, index) => (
          <li key={index} className="file-item">
            <span onClick={() => handleFileClick(file)}>
              {file.type === 'directory' ? <FaFolder /> : <FaFile />} {file.name}
            </span>
            <div>
              {file.type !== 'directory' && (
                <>
                  <button onClick={() => handleFileDownload(file)}><FaDownload /></button>
                  <button onClick={handleEditFile}><FaEdit /></button>
                </>
              )}
              <button onClick={() => handleDeleteItem(file)}><FaTrash /></button>
            </div>
          </li>
        ))}
      </ul>
      {selectedFile && (
        <div className="file-preview">
          <h4>File Preview: {selectedFile.name}</h4>
          {isLoading ? (
            <p>Loading file content...</p>
          ) : isEditing ? (
            <>
              <textarea
                value={fileContent}
                onChange={(e) => setFileContent(e.target.value)}
                rows={10}
                cols={50}
              />
              <button onClick={handleSaveFile}>Save</button>
            </>
          ) : (
            <pre>{fileContent}</pre>
          )}
        </div>
      )}
    </div>
  );
}

export default FileBrowser;