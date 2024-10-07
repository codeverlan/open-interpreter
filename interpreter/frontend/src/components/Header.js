import React from 'react';
import { Search, Moon, Sun, Plus } from 'lucide-react';

function Header({ darkMode, setDarkMode, onCreateProject }) {
  return (
    <header className="flex justify-between items-center mb-8">
      <div className="relative">
        <input
          type="text"
          placeholder="Search projects..."
          className="pl-10 pr-4 py-2 rounded-full bg-white dark:bg-gray-700 shadow-sm"
        />
        <Search className="absolute left-3 top-2.5 text-gray-400" size={18} />
      </div>
      <div className="flex items-center space-x-4">
        <button 
          onClick={onCreateProject} 
          className="flex items-center px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
        >
          <Plus size={18} className="mr-2" />
          Create Project
        </button>
        <button 
          onClick={() => setDarkMode(!darkMode)} 
          className="p-2 rounded-full hover:bg-gray-200 dark:hover:bg-gray-700"
        >
          {darkMode ? <Sun size={20} /> : <Moon size={20} />}
        </button>
      </div>
    </header>
  );
}

export default Header;