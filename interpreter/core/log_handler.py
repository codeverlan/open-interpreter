import re
from datetime import datetime

class LogHandler:
    def __init__(self):
        self.logs = []

    def parse_log(self, log_line):
        """
        Parse a log line and extract relevant information.
        """
        # Example log format: [TIMESTAMP] [LEVEL] [MODULE] Message
        log_pattern = r'\[(.*?)\] \[(.*?)\] \[(.*?)\] (.*)'
        match = re.match(log_pattern, log_line)
        
        if match:
            timestamp, level, module, message = match.groups()
            return {
                'timestamp': timestamp,
                'level': level.strip('[]'),  # Remove square brackets from level
                'module': module.strip('[]'),  # Remove square brackets from module
                'message': message
            }
        else:
            # If the log doesn't match the expected format, store it as is
            return {
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S,%f'),
                'level': 'INFO',
                'module': 'UNKNOWN',
                'message': log_line
            }

    def add_log(self, log_line):
        """
        Add a parsed log to the logs list.
        """
        parsed_log = self.parse_log(log_line)
        self.logs.append(parsed_log)

    def get_logs_by_level(self, level):
        """
        Retrieve logs of a specific level.
        """
        return [log for log in self.logs if log['level'].upper() == level.upper()]

    def get_logs_by_module(self, module):
        """
        Retrieve logs from a specific module.
        """
        return [log for log in self.logs if log['module'].upper() == module.upper()]

    def search_logs(self, keyword):
        """
        Search logs for a specific keyword.
        """
        return [log for log in self.logs if keyword.lower() in log['message'].lower()]

    def get_recent_logs(self, n=10):
        """
        Retrieve the n most recent logs.
        """
        return self.logs[-n:]

    def clear_logs(self):
        """
        Clear all stored logs.
        """
        self.logs = []

# Example usage
if __name__ == "__main__":
    log_handler = LogHandler()
    
    # Example log lines
    log_lines = [
        "[2023-06-01 10:30:15,123] [INFO] [PromptManager] Fetching prompts for project_id: 123",
        "[2023-06-01 10:30:16,456] [ERROR] [Database] Failed to connect to database",
        "[2023-06-01 10:30:17,789] [DEBUG] [API] Received request: GET /api/projects/123/prompts"
    ]
    
    for line in log_lines:
        log_handler.add_log(line)
    
    print("All logs:", log_handler.logs)
    print("Error logs:", log_handler.get_logs_by_level("ERROR"))
    print("API logs:", log_handler.get_logs_by_module("API"))
    print("Logs containing 'project':", log_handler.search_logs("project"))
    print("Recent logs:", log_handler.get_recent_logs(2))