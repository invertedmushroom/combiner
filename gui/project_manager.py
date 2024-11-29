import tkinter as tk
from tkinter.simpledialog import askstring
from tkinter import filedialog, messagebox
import json
import os

class ProjectManager(tk.Frame):
    def __init__(self, master, file_selector, storage_file="data/projects.json"):
        super().__init__(master)
        self.file_selector = file_selector  # Store the file_selector instance
        self.storage_file = storage_file
        self.project_list = self.load_projects()

        self.label = tk.Label(self, text="Select a project:")
        self.label.pack()

        self.listbox = tk.Listbox(self)
        self.listbox.pack(fill=tk.BOTH, expand=True)
        self.load_listbox()

        self.save_button = tk.Button(self, text="Save Current Project", command=self.save_project)
        self.save_button.pack(pady=5)

        self.load_button = tk.Button(self, text="Load Selected Project", command=self.load_project)
        self.load_button.pack(pady=5)

        self.remove_project_button = tk.Button(self, text="Remove Selected Project", command=self.remove_project)
        self.remove_project_button.pack(pady=5)

    def load_projects(self):
        if os.path.exists(self.storage_file):
            with open(self.storage_file, 'r') as f:
                return json.load(f)
        return {}

    def load_listbox(self):
        self.listbox.delete(0, tk.END)
        for project_name in self.project_list:
            self.listbox.insert(tk.END, project_name)

    def save_project(self):
        project_name = askstring("Project Name", "Enter project name:")
        if project_name:
            # Get the folder structure from the TreeView
            project_structure = self.file_selector.get_project_structure()

            # Save the project structure to the JSON file
            self.project_list[project_name] = project_structure
            with open(self.storage_file, 'w') as f:
                json.dump(self.project_list, f, indent=4)
            self.load_listbox()

    def load_project(self):
        selected_project = self.listbox.get(tk.ACTIVE)
        if selected_project:
            project_structure = self.project_list.get(selected_project, {})
            if project_structure:
                self.file_selector.clear_files()  # Clear current selection
                self.file_selector.load_project_structure(project_structure)
            else:
                messagebox.showerror("Error", "No structure found for this project.")
        else:
            messagebox.showerror("Error", "Please select a project to load.")

    def remove_project(self):
        selected_project = self.listbox.get(tk.ACTIVE)
        if selected_project:
            confirm = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete the project '{selected_project}'?")
            if confirm:
                del self.project_list[selected_project]
                with open(self.storage_file, 'w') as f:
                    json.dump(self.project_list, f, indent=4)
                self.load_listbox()
                self.file_selector.clear_files()  # Clear current selection
        else:
            messagebox.showerror("Error", "Please select a project to remove.")
