import React from 'react';
import { Home, Users, Settings } from 'lucide-react';

function Sidebar({ setCurrentView }) {
  const navItems = [
    { name: 'Projects', icon: Home, view: 'projects' },
    { name: 'Agents', icon: Users, view: 'agents' },
    { name: 'Settings', icon: Settings, view: 'settings' },
  ];

  return (
    <aside className="w-64 h-screen p-4 bg-white dark:bg-gray-800 shadow-lg">
      <h1 className="text-2xl font-bold mb-8 dark:text-white">Open Interpreter</h1>
      <nav>
        <ul className="space-y-2">
          {navItems.map((item) => (
            <li key={item.name}>
              <button
                onClick={() => setCurrentView(item.view)}
                className="flex items-center w-full py-2 px-4 rounded hover:bg-blue-500 hover:text-white transition-colors duration-200 dark:text-gray-300 dark:hover:text-white"
              >
                <item.icon size={18} className="mr-2" />
                {item.name}
              </button>
            </li>
          ))}
        </ul>
      </nav>
    </aside>
  );
}

export default Sidebar;