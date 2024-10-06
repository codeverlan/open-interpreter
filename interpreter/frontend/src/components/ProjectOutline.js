import React, { useState, useEffect } from 'react';

const ProjectOutline = ({ apiEndpoint, currentProject }) => {
  const [outline, setOutline] = useState('');
  const [isEditing, setIsEditing] = useState(false);

  useEffect(() => {
    if (currentProject) {
      fetchOutline();
    }
  }, [currentProject]);

  const fetchOutline = async () => {
    try {
      const response = await fetch(`${apiEndpoint}/get_project_outline?project=${currentProject}`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      if (data.success) {
        setOutline(data.outline);
      } else {
        throw new Error(data.error || 'Failed to fetch project outline');
      }
    } catch (error) {
      console.error('Error fetching project outline:', error);
    }
  };

  const updateOutline = async () => {
    try {
      const response = await fetch(`${apiEndpoint}/update_project_outline`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ project: currentProject, outline }),
      });
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      if (!data.success) {
        throw new Error(data.error || 'Failed to update project outline');
      }
      setIsEditing(false);
    } catch (error) {
      console.error('Error updating project outline:', error);
    }
  };

  const handleEdit = () => {
    setIsEditing(true);
  };

  const handleSave = () => {
    updateOutline();
  };

  const handleChange = (e) => {
    setOutline(e.target.value);
  };

  if (!currentProject) {
    return <div>Please select a project to view its outline.</div>;
  }

  return (
    <div className="project-outline">
      <h2>Project Outline</h2>
      {isEditing ? (
        <>
          <textarea
            value={outline}
            onChange={handleChange}
            rows={10}
            cols={50}
          />
          <button onClick={handleSave}>Save</button>
        </>
      ) : (
        <>
          <pre>{outline}</pre>
          <button onClick={handleEdit}>Edit</button>
        </>
      )}
    </div>
  );
};

export default ProjectOutline;