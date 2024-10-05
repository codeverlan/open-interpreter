# Open Interpreter Project Status

## Vision
The goal in modifying this program is to create a React Frontend with a modular, project-based environment. This allows users to customize the program's functionality on a per-project basis, primarily intended for open-source software. Our modifications prioritize the ability to reference specific documentation and customize prompts for each project. The program adheres to programming best practices rather than being creative.

## Current Task

1. Redesign UI to follow best practices. 
   -Use a series of tabs across the top of the interface. 
   -Disable or delete the save snippits fuction.
   -Consider which elements belong on which tabs in order for the user to use the program best. 
   -The entire preferences screen needs to be redesigned and have its own tab. 
   -The knowledgebase feature needs to have the function to upload single files, as well as reference   entire directories. 
   -The pojects feature needs to be able to add and delete projects. When the project is added, the user should be prompted for the location of the project directory, AND the associated conda environment. This should be saved, paired and stored.

2. API Endpoint Mismatches:
   - Some API calls are returning 404 errors, specifically:
     - GET /api/get_settings/get_settings
     - GET /api/get_settings/get_projects

## Next Steps

1. Ability to list, edit, and save Open Interpreter prompts on a per project basis.

2. Improve Log Utilization:
   - Develop a strategy for more effectively analyzing and using the logs generated in the terminal
   - Implement a log parsing system to extract relevant information for debugging

3. Fix API Endpoint Mismatches:
   - Review and correct API endpoint URLs in the frontend code
   - Ensure backend routes match the frontend expectations

4. Enhance Error Handling:
   - Implement more robust error handling in individual components
   - Add user-friendly error messages and recovery options

5. Improve State Management:
   - Review and optimize state management in the App component and its children
   - Ensure that state updates are handled correctly, especially after API calls

6. Testing:
   - Develop unit tests for React components, focusing on the FileBrowser component
   - Implement integration tests for API and backend interactions

7. Documentation:
   - Update API documentation to reflect any changes made
   - Document the current issues and their potential causes for future reference

This file will be updated as we make progress on resolving the current issues and improving the overall stability and functionality of the application.