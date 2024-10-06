# UI_changes

## UI Componets
### Chat: The User interacts with the AI in this window.
### Files: Lists the files in the project directory (defined elsewhere)
### Settings: Project settings
### Docs: References the agents may need to complete a task
### Status: A project outline. Things are added, deleted, changed or marked accomplished by the user OR the AI agents.
### Prompts: A place to store prompt history, as well as the result
### Logs: Live streaming server logs
### Agents: A place to use all agent capabilities, create new agents, modify and delete them.

## Changes (integrate into project_status.md)
### Files: This is a project-based program. Each project has it's own working directory. The files tab displays all files in the project directory. A check box is beside each file. If the box is checked, the file is provided to the AI as context.
### Settings: Delay changes until features are complete.
### Docs: Needs to accept a wide array of file types for the project to use as references. Functions as the /references directory does now.
### Status: Rename this to 'outline.' This functions as the project_status.md. It is updated by the user or the AI. It is a list of tasks that are checked off as they are completed. The outline is modified based on project goals and user directions. The AI should assume the task of updating this document after completion of every task. If there is a persistent error, the document is updated with what the error is, and the steps that have been taken to solve it.
### Prompts: This keeps a running log of prompts given by the user and the AI's response. It is a persists between sessions, acting as a transcript.
### Logs: These are streaming server logs. The AI should have access to this as well, so that it can understand the result of its terminal commands. The user should also be able to enter terminal commands here. Rename this section 'terminal.'
### Agents: Delay changes until features are complete. This will list the AI agents and allow them to be edited.