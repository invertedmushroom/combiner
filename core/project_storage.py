import json
import os

class ProjectStorage:
    def __init__(self, storage_file="data/projects.json"):
        self.storage_file = storage_file
        self.projects = self.load_projects()

    def load_projects(self):
        if os.path.exists(self.storage_file):
            with open(self.storage_file, 'r') as f:
                return json.load(f)
        return {}

    def save_project(self, project_name, files):
        self.projects[project_name] = files
        with open(self.storage_file, 'w') as f:
            json.dump(self.projects, f)

    def get_project_files(self, project_name):
        return self.projects.get(project_name, [])
