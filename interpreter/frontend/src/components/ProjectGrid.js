import React from 'react';
import { Plus } from 'lucide-react';

function ProjectGrid({ darkMode }) {
  const projects = [1, 2, 3, 4, 5]; // This would be replaced with actual project data

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {projects.map((project) => (
        <div key={project} className={`p-6 rounded-lg shadow-md ${darkMode ? 'bg-gray-800' : 'bg-white'}`}>
          <h3 className="text-xl font-semibold mb-2">Project {project}</h3>
          <p className={`${darkMode ? 'text-gray-400' : 'text-gray-600'} mb-4`}>Last updated: 2 days ago</p>
          <button className="text-blue-500 hover:underline">Open Project</button>
        </div>
      ))}
      <div className={`p-6 rounded-lg shadow-md ${darkMode ? 'bg-gray-800' : 'bg-white'} flex items-center justify-center`}>
        <button className="flex items-center text-blue-500 hover:underline">
          <Plus size={20} className="mr-2" />
          New Project
        </button>
      </div>
    </div>
  );
}

export default ProjectGrid;