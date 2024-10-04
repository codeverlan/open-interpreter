import os
import ast

class ProjectAnalyzer:
    def __init__(self, root_dir):
        self.root_dir = root_dir

    def analyze_structure(self):
        structure = {}
        for root, dirs, files in os.walk(self.root_dir):
            current = structure
            path = os.path.relpath(root, self.root_dir).split(os.sep)
            for part in path:
                if part not in current:
                    current[part] = {}
                current = current[part]
            for file in files:
                current[file] = None
        return structure

    def analyze_python_file(self, file_path):
        with open(file_path, 'r') as file:
            content = file.read()
        
        tree = ast.parse(content)
        classes = [node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
        functions = [node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
        
        return {
            'classes': classes,
            'functions': functions
        }

    def get_project_summary(self):
        summary = "Open Interpreter Project Summary:\n\n"
        
        key_files = [
            'interpreter/__init__.py',
            'interpreter/core/core.py',
            'interpreter/terminal_interface/terminal_interface.py'
        ]
        
        for file in key_files:
            full_path = os.path.join(self.root_dir, file)
            if os.path.exists(full_path):
                analysis = self.analyze_python_file(full_path)
                summary += f"File: {file}\n"
                summary += f"  Classes: {', '.join(analysis['classes'])}\n"
                summary += f"  Functions: {', '.join(analysis['functions'])}\n\n"
        
        return summary

    def modify_file(self, file_path, modifications):
        full_path = os.path.join(self.root_dir, file_path)
        if not os.path.exists(full_path):
            return f"Error: File {file_path} does not exist."
        
        with open(full_path, 'r') as file:
            content = file.read()
        
        for old, new in modifications.items():
            content = content.replace(old, new)
        
        with open(full_path, 'w') as file:
            file.write(content)
        
        return f"File {file_path} has been modified successfully."

    def add_new_function(self, file_path, function_name, function_body):
        full_path = os.path.join(self.root_dir, file_path)
        if not os.path.exists(full_path):
            return f"Error: File {file_path} does not exist."
        
        with open(full_path, 'r') as file:
            content = file.read()
        
        new_function = f"\n\ndef {function_name}:{function_body}\n"
        content += new_function
        
        with open(full_path, 'w') as file:
            file.write(content)
        
        return f"Function '{function_name}' has been added to {file_path} successfully."

def main():
    analyzer = ProjectAnalyzer('open')
    print(analyzer.get_project_summary())
    
    while True:
        print("\nWhat would you like to do?")
        print("1. Modify a file")
        print("2. Add a new function")
        print("3. Exit")
        
        choice = input("Enter your choice (1/2/3): ")
        
        if choice == '1':
            file_path = input("Enter the file path to modify: ")
            old_text = input("Enter the text to replace: ")
            new_text = input("Enter the new text: ")
            print(analyzer.modify_file(file_path, {old_text: new_text}))
        elif choice == '2':
            file_path = input("Enter the file path to add the function: ")
            function_name = input("Enter the function name: ")
            function_body = input("Enter the function body (use \\n for new lines): ")
            print(analyzer.add_new_function(file_path, function_name, function_body))
        elif choice == '3':
            print("Exiting the program.")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()