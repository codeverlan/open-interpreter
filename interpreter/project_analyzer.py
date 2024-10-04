import os
import ast
import json

class ProjectAnalyzer:
    def __init__(self, project_path):
        self.project_path = project_path

    def analyze_project(self):
        analysis_result = {
            'file_count': 0,
            'total_lines': 0,
            'language_stats': {},
            'function_count': 0,
            'class_count': 0,
            'import_count': 0,
            'top_level_functions': [],
            'top_level_classes': [],
        }

        for root, _, files in os.walk(self.project_path):
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    self.analyze_python_file(file_path, analysis_result)

        return analysis_result

    def analyze_python_file(self, file_path, analysis_result):
        with open(file_path, 'r') as file:
            content = file.read()
            analysis_result['file_count'] += 1
            analysis_result['total_lines'] += len(content.splitlines())

            if 'Python' not in analysis_result['language_stats']:
                analysis_result['language_stats']['Python'] = 0
            analysis_result['language_stats']['Python'] += 1

            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    analysis_result['function_count'] += 1
                    if node.col_offset == 0:
                        analysis_result['top_level_functions'].append(node.name)
                elif isinstance(node, ast.ClassDef):
                    analysis_result['class_count'] += 1
                    if node.col_offset == 0:
                        analysis_result['top_level_classes'].append(node.name)
                elif isinstance(node, ast.Import) or isinstance(node, ast.ImportFrom):
                    analysis_result['import_count'] += 1

    def generate_report(self):
        analysis_result = self.analyze_project()
        report = {
            "Project Summary": {
                "Total Files": analysis_result['file_count'],
                "Total Lines of Code": analysis_result['total_lines'],
                "Language Distribution": analysis_result['language_stats'],
            },
            "Code Metrics": {
                "Function Count": analysis_result['function_count'],
                "Class Count": analysis_result['class_count'],
                "Import Count": analysis_result['import_count'],
            },
            "Top-Level Definitions": {
                "Functions": analysis_result['top_level_functions'],
                "Classes": analysis_result['top_level_classes'],
            }
        }
        return json.dumps(report, indent=2)

# Example usage:
# analyzer = ProjectAnalyzer('/path/to/your/project')
# report = analyzer.generate_report()
# print(report)