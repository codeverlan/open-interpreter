# PromptManager Component Documentation

The PromptManager component is responsible for managing prompts within a project, including the default system message and user-created prompts.

## Features

1. View and edit the default system message for a project
2. Create new prompts
3. View existing prompts
4. Edit existing prompts
5. Delete prompts

## Usage

To use the PromptManager component, import it into your React component and pass the `projectId` as a prop:

```jsx
import PromptManager from './components/PromptManager';

function ProjectView({ projectId }) {
  return (
    <div>
      <h1>Project View</h1>
      <PromptManager projectId={projectId} />
    </div>
  );
}
```

## API Endpoints

The PromptManager component interacts with the following API endpoints:

1. GET `/api/projects/{projectId}/prompts`
   - Fetches all prompts for a given project
2. POST `/api/projects/{projectId}/prompts`
   - Creates a new prompt for the project
3. PUT `/api/projects/{projectId}/prompts/{promptId}`
   - Updates an existing prompt
4. DELETE `/api/projects/{projectId}/prompts/{promptId}`
   - Deletes a prompt
5. GET `/api/projects/{projectId}/prompts/default_system_message`
   - Fetches the default system message for the project
6. PUT `/api/projects/{projectId}/prompts/default_system_message`
   - Updates the default system message for the project

## Component Structure

The PromptManager component is structured as follows:

1. Default System Message section
   - Displays and allows editing of the default system message
2. Create New Prompt section
   - Provides input fields for creating a new prompt
3. Existing Prompts section
   - Lists all existing prompts with options to edit or delete each prompt

## State Management

The component uses React hooks (useState, useEffect, useCallback, and useMemo) to manage its state and side effects. Key state variables include:

- `prompts`: An array of all prompts for the current project
- `newPrompt`: An object representing the new prompt being created
- `editingPrompt`: An object representing the prompt currently being edited
- `defaultSystemMessage`: An object representing the default system message
- `isLoading`: A boolean indicating whether an API request is in progress
- `error`: A string containing any error messages

## Error Handling

The component implements error handling for all API requests. If an error occurs, it is displayed to the user, and the relevant action (e.g., creating a prompt) is prevented.

## Performance Optimization

The component uses debounced functions for updating state to prevent excessive re-renders and API calls when the user is typing in input fields.

## Styling

The component's styles are defined in the `PromptManager.css` file. Ensure this file is imported in the component for proper styling.

## Future Improvements

1. Implement prompt versioning
2. Add a system for prompt templates
3. Enhance authentication and authorization
4. Improve state management, possibly by implementing a global state management solution
5. Optimize performance for projects with a large number of prompts
6. Implement comprehensive unit and integration tests

For any questions or issues, please refer to the project's issue tracker or contact the development team.