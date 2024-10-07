import { useState } from 'react'
import { Search, Plus, ChevronLeft, ChevronRight } from 'lucide-react'

export default function Component() {
  const [showNewProjectWizard, setShowNewProjectWizard] = useState(false)
  const [wizardStep, setWizardStep] = useState(1)
  const [projectName, setProjectName] = useState('')
  const [projectType, setProjectType] = useState('')

  const projects = [
    { id: 1, name: "Web App", lastUpdated: "2 days ago" },
    { id: 2, name: "Mobile App", lastUpdated: "1 week ago" },
    { id: 3, name: "Data Analysis", lastUpdated: "3 days ago" },
    { id: 4, name: "ML Model", lastUpdated: "1 day ago" },
  ]

  const nextStep = () => setWizardStep(wizardStep + 1)
  const prevStep = () => setWizardStep(wizardStep - 1)

  return (
    <div className="min-h-screen bg-gray-100 p-8">
      <header className="mb-8">
        <h1 className="text-3xl font-bold mb-4">Open Interpreter</h1>
        <div className="flex justify-between items-center">
          <div className="relative">
            <input
              type="text"
              placeholder="Search projects..."
              className="pl-10 pr-4 py-2 rounded-full bg-white shadow-sm"
            />
            <Search className="absolute left-3 top-2.5 text-gray-400" size={18} />
          </div>
          <button 
            onClick={() => setShowNewProjectWizard(true)}
            className="bg-blue-500 text-white py-2 px-4 rounded-full hover:bg-blue-600 flex items-center"
          >
            <Plus size={20} className="mr-2" />
            New Project
          </button>
        </div>
      </header>

      {!showNewProjectWizard ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {projects.map((project) => (
            <div key={project.id} className="bg-white p-6 rounded-lg shadow-md">
              <h3 className="text-xl font-semibold mb-2">{project.name}</h3>
              <p className="text-gray-600 mb-4">Last updated: {project.lastUpdated}</p>
              <button className="text-blue-500 hover:underline">Open Project</button>
            </div>
          ))}
        </div>
      ) : (
        <div className="bg-white p-8 rounded-lg shadow-md max-w-md mx-auto">
          <h2 className="text-2xl font-bold mb-6">Create New Project</h2>
          
          <div className="mb-6">
            <div className="flex justify-between mb-2">
              {[1, 2, 3].map((step) => (
                <div
                  key={step}
                  className={`w-8 h-8 rounded-full flex items-center justify-center ${
                    step <= wizardStep ? 'bg-blue-500 text-white' : 'bg-gray-200'
                  }`}
                >
                  {step}
                </div>
              ))}
            </div>
            <div className="h-2 bg-gray-200 rounded-full">
              <div
                className="h-full bg-blue-500 rounded-full transition-all duration-300 ease-in-out"
                style={{ width: `${(wizardStep - 1) * 50}%` }}
              ></div>
            </div>
          </div>
          
          {wizardStep === 1 && (
            <div>
              <label className="block mb-2 font-medium">Project Name</label>
              <input
                type="text"
                value={projectName}
                onChange={(e) => setProjectName(e.target.value)}
                className="w-full p-2 border rounded mb-4"
                placeholder="Enter project name"
              />
            </div>
          )}
          
          {wizardStep === 2 && (
            <div>
              <label className="block mb-2 font-medium">Project Type</label>
              <select
                value={projectType}
                onChange={(e) => setProjectType(e.target.value)}
                className="w-full p-2 border rounded mb-4"
              >
                <option value="">Select a type</option>
                <option value="web">Web Application</option>
                <option value="mobile">Mobile App</option>
                <option value="data">Data Analysis</option>
                <option value="ml">Machine Learning</option>
              </select>
            </div>
          )}
          
          {wizardStep === 3 && (
            <div>
              <h3 className="text-xl font-semibold mb-4">Confirm Details</h3>
              <p><strong>Project Name:</strong> {projectName}</p>
              <p><strong>Project Type:</strong> {projectType}</p>
            </div>
          )}
          
          <div className="flex justify-between mt-6">
            {wizardStep > 1 && (
              <button onClick={prevStep} className="flex items-center text-blue-500">
                <ChevronLeft size={20} className="mr-1" /> Back
              </button>
            )}
            {wizardStep < 3 ? (
              <button onClick={nextStep} className="ml-auto flex items-center text-blue-500">
                Next <ChevronRight size={20} className="ml-1" />
              </button>
            ) : (
              <button 
                onClick={() => {
                  // Here you would typically save the new project
                  setShowNewProjectWizard(false)
                  setWizardStep(1)
                  setProjectName('')
                  setProjectType('')
                }} 
                className="ml-auto bg-blue-500 text-white py-2 px-4 rounded hover:bg-blue-600"
              >
                Create Project
              </button>
            )}
          </div>
        </div>
      )}
    </div>
  )
}