import React, { useState, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';

function DocumentationViewer({ apiEndpoint, currentProject }) {
  const [docs, setDocs] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [isEditing, setIsEditing] = useState(false);
  const [editContent, setEditContent] = useState('');
  const [docFiles, setDocFiles] = useState([]);
  const [selectedFile, setSelectedFile] = useState('main');

  useEffect(() => {
    if (currentProject) {
      fetchDocumentation();
      fetchDocumentationFiles();
    }
  }, [currentProject]);

  const fetchDocumentation = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await fetch(`${apiEndpoint}/get_project_documentation?project=${currentProject}`);
      if (!response.ok) {
        throw new Error('Failed to fetch documentation');
      }
      const data = await response.json();
      setDocs(data.content);
    } catch (error) {
      console.error('Error fetching documentation:', error);
      setError('Failed to fetch documentation. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const fetchDocumentationFiles = async () => {
    try {
      const response = await fetch(`${apiEndpoint}/get_documentation_file_list?project=${currentProject}`);
      if (!response.ok) {
        throw new Error('Failed to fetch documentation files');
      }
      const data = await response.json();
      setDocFiles(data.files);
    } catch (error) {
      console.error('Error fetching documentation files:', error);
    }
  };

  const handleFileSelect = async (file) => {
    setSelectedFile(file);
    setIsLoading(true);
    setError(null);
    try {
      const response = await fetch(`${apiEndpoint}/read_documentation_file?project=${currentProject}&file=${file}`);
      if (!response.ok) {
        throw new Error('Failed to fetch documentation file');
      }
      const data = await response.json();
      setDocs(data.content);
    } catch (error) {
      console.error('Error fetching documentation file:', error);
      setError('Failed to fetch documentation file. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleEdit = () => {
    setIsEditing(true);
    setEditContent(docs);
  };

  const handleSave = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await fetch(`${apiEndpoint}/write_documentation_file`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          project: currentProject,
          file: selectedFile,
          content: editContent,
        }),
      });
      if (!response.ok) {
        throw new Error('Failed to save documentation');
      }
      setDocs(editContent);
      setIsEditing(false);
    } catch (error) {
      console.error('Error saving documentation:', error);
      setError('Failed to save documentation. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleCancel = () => {
    setIsEditing(false);
    setEditContent('');
  };

  const handleNewFile = async () => {
    const fileName = prompt('Enter the name for the new documentation file:');
    if (fileName) {
      try {
        await fetch(`${apiEndpoint}/write_documentation_file`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            project: currentProject,
            file: fileName,
            content: '# New Documentation\n\nEnter your content here.',
          }),
        });
        fetchDocumentationFiles();
        handleFileSelect(fileName);
      } catch (error) {
        console.error('Error creating new documentation file:', error);
        setError('Failed to create new documentation file. Please try again.');
      }
    }
  };

  return (
    <div className="documentation-viewer">
      <h2>Project Documentation</h2>
      <div className="documentation-controls">
        <select onChange={(e) => handleFileSelect(e.target.value)} value={selectedFile}>
          {docFiles.map((file) => (
            <option key={file} value={file}>
              {file}
            </option>
          ))}
        </select>
        <button onClick={handleNewFile}>New File</button>
        {!isEditing && <button onClick={handleEdit}>Edit</button>}
        {isEditing && (
          <>
            <button onClick={handleSave}>Save</button>
            <button onClick={handleCancel}>Cancel</button>
          </>
        )}
      </div>
      {isLoading && <p>Loading documentation...</p>}
      {error && <p className="error-message">{error}</p>}
      {!isLoading && !error && (
        <div className="documentation-content">
          {isEditing ? (
            <textarea
              value={editContent}
              onChange={(e) => setEditContent(e.target.value)}
              rows={20}
              cols={80}
            />
          ) : (
            <ReactMarkdown>{docs}</ReactMarkdown>
          )}
        </div>
      )}
    </div>
  );
}

export default DocumentationViewer;