# Agent Manager

The Agent Manager is a component that allows users to create, read, update, and delete agents in the Open Interpreter system.

## Features

1. **List Agents**: Displays a list of all existing agents with their names and descriptions.
2. **Create Agent**: Allows users to create a new agent by providing a name and description.
3. **Update Agent**: Enables users to edit the name and description of an existing agent.
4. **Delete Agent**: Provides the ability to remove an agent from the system with a confirmation dialog.
5. **Refresh**: Users can manually refresh the list of agents.
6. **Error Handling**: Displays error messages when operations fail.
7. **Success Notifications**: Shows success messages upon successful operations.

## Usage

The Agent Manager can be accessed through the main navigation bar in the Open Interpreter interface. Click on the "Agents" tab to view and interact with the Agent Manager.

### Creating an Agent

1. Scroll to the "Create New Agent" section at the bottom of the Agent Manager.
2. Enter a name for the agent in the "Agent Name" field.
3. Provide a description for the agent in the "Agent Description" field.
4. Click the "Create Agent" button to add the new agent to the system.

### Updating an Agent

1. Locate the agent you wish to edit in the list of existing agents.
2. Click the "Edit" button next to the agent's information.
3. Modify the name and/or description in the input fields that appear.
4. Click "Save" to update the agent's information or "Cancel" to discard changes.

### Deleting an Agent

1. Find the agent you want to remove in the list of existing agents.
2. Click the "Delete" button next to the agent's information.
3. Confirm the deletion in the popup dialog that appears.

## API Endpoints

The Agent Manager interacts with the following API endpoints:

- `GET /api/agents`: Fetches all agents
- `POST /api/agents`: Creates a new agent
- `PUT /api/agents/<agent_id>`: Updates an existing agent
- `DELETE /api/agents/<agent_id>`: Deletes an agent

## Future Enhancements

Potential improvements for the Agent Manager include:

1. Pagination or infinite scrolling for large numbers of agents
2. Search and filter functionality to easily find specific agents
3. Sorting options for the agent list
4. More detailed agent information and management options

For any issues or feature requests related to the Agent Manager, please contact the development team.