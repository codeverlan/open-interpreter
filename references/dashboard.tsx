import { useState } from 'react'
import { Search, Plus, Moon, Sun, Menu } from 'lucide-react'

export default function Component() {
  const [darkMode, setDarkMode] = useState(false)
  
  return (
    <div className={`min-h-screen ${darkMode ? 'bg-gray-900 text-white' : 'bg-gray-100'}`}>
      <div className="flex">
        {/* Left Sidebar */}
        <aside className={`w-64 h-screen p-4 ${darkMode ? 'bg-gray-800' : 'bg-white'} shadow-lg`}>
          <h1 className="text-2xl font-bold mb-8">Open Interpreter</h1>
          <nav>
            <ul className="space-y-2">
              <li><a href="#" className="block py-2 px-4 rounded hover:bg-blue-500 hover:text-white">Dashboard</a></li>
              <li><a href="#" className="block py-2 px-4 rounded hover:bg-blue-500 hover:text-white">Projects</a></li>
              <li><a href="#" className="block py-2 px-4 rounded hover:bg-blue-500 hover:text-white">Agents</a></li>
              <li><a href="#" className="block py-2 px-4 rounded hover:bg-blue-500 hover:text-white">Settings</a></li>
            </ul>
          </nav>
        </aside>
        
        {/* Main Content */}
        <main className="flex-1 p-8">
          <header className="flex justify-between items-center mb-8">
            <div className="relative">
              <input
                type="text"
                placeholder="Search projects..."
                className={`pl-10 pr-4 py-2 rounded-full ${darkMode ? 'bg-gray-700' : 'bg-white'} shadow-sm`}
              />
              <Search className="absolute left-3 top-2.5 text-gray-400" size={18} />
            </div>
            <div className="flex items-center space-x-4">
              <select className={`p-2 rounded ${darkMode ? 'bg-gray-700' : 'bg-white'} shadow-sm`}>
                <option>Select a project</option>
                <option>Project 1</option>
                <option>Project 2</option>
              </select>
              <button onClick={() => setDarkMode(!darkMode)} className="p-2 rounded-full hover:bg-gray-200 dark:hover:bg-gray-700">
                {darkMode ? <Sun size={20} /> : <Moon size={20} />}
              </button>
            </div>
          </header>
          
          <h2 className="text-2xl font-semibold mb-4">Recent Projects</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[1, 2, 3, 4, 5].map((project) => (
              <div key={project} className={`p-6 rounded-lg shadow-md ${darkMode ? 'bg-gray-800' : 'bg-white'}`}>
                <h3 className="text-xl font-semibold mb-2">Project {project}</h3>
                <p className="text-gray-600 dark:text-gray-400 mb-4">Last updated: 2 days ago</p>
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
        </main>
      </div>
    </div>
  )
}