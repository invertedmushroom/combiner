from tkinterdnd2 import DND_FILES, TkinterDnD
import tkinter as tk
from tkinter import Frame, Label, filedialog, StringVar, Entry, Button, Menu, ttk
import os

class FileSelector(Frame):
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.file_list = []
        self.excluded_items = set()
        self.extensions = StringVar(value=".py, .txt, .md")  # Default to Python, Text, Markdown files

        # Create the TreeView for displaying the directory structure
        self.tree = ttk.Treeview(self, selectmode='extended')
        self.tree.pack(fill="both", expand=True)

        # Add the TreeView scrollbar
        self.tree_scroll = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.tree_scroll.pack(side='right', fill='y')
        self.tree.configure(yscrollcommand=self.tree_scroll.set)

        # Bind right-click to open the context menu
        self.tree.bind("<Button-3>", self.show_context_menu)

        # Enable drag-and-drop for the TreeView
        self.tree.drop_target_register(DND_FILES)
        self.tree.dnd_bind('<<Drop>>', self.drop_file)

        # File extensions entry
        self.ext_label = Label(self, text="Extensions filter (comma separated):")
        self.ext_label.pack(pady=5)
        self.ext_entry = Entry(self, textvariable=self.extensions)
        self.ext_entry.pack(pady=5)

        # Add buttons
        self.folder_button = Button(self, text="Add Folder", command=self.open_folder_dialog)
        self.folder_button.pack(pady=5)
        self.file_button = Button(self, text="Add Files", command=self.open_file_dialog)
        self.file_button.pack(pady=5)

        # Context menu
        self.context_menu = Menu(self, tearoff=0)
        self.context_menu.add_command(label="Remove", command=self.remove_item)
        self.context_menu.add_command(label="Exclude", command=self.exclude_item)
        self.context_menu.add_command(label="Include", command=self.include_item)

    def open_file_dialog(self, event=None):
        extensions = self._get_file_types()
        files = filedialog.askopenfilenames(filetypes=extensions)
        self.add_files(files)

    def open_folder_dialog(self, event=None):
        folder = filedialog.askdirectory()
        if folder:
            self.add_folder(folder)

    def add_folder(self, folder):
        node = self.tree.insert('', 'end', text=os.path.basename(folder), open=True)
        self._populate_tree(node, folder)

    def _populate_tree(self, parent, path):
        extensions = self._get_extensions()  # Get the extensions list for filtering
        for p in os.listdir(path):
            full_path = os.path.join(path, p)
            
            # Skip hidden directories and unwanted system directories like `.conda`
            if p.startswith('.'):
                continue
            
            if os.path.isdir(full_path):
                node = self.tree.insert(parent, 'end', text=p, open=False)
                self._populate_tree(node, full_path)
            else:
                if any(full_path.endswith(ext) for ext in extensions):
                    self.tree.insert(parent, 'end', text=p, open=False, values=[full_path])
                    self.file_list.append(full_path)

    def _get_file_types(self):
        ext = self.extensions.get().split(',')
        file_types = [(f"{e.strip().upper()} Files", f"*{e.strip()}") for e in ext]
        file_types.append(("All Files", "*.*"))  # Add 'All Files' option
        return file_types

    def _get_extensions(self):
        ext = self.extensions.get().split(',')
        return [e.strip() for e in ext]  # Return only the extensions as a list of strings

    def show_context_menu(self, event):
        selected_item = self.tree.selection()
        if selected_item:
            item_tags = self.tree.item(selected_item, 'tags')
            if 'excluded' in item_tags:
                self.context_menu.entryconfig("Include", state="normal")
                self.context_menu.entryconfig("Exclude", state="disabled")
            else:
                self.context_menu.entryconfig("Include", state="disabled")
                self.context_menu.entryconfig("Exclude", state="normal")
            self.context_menu.tk_popup(event.x_root, event.y_root)

    def remove_item(self):
        selected_item = self.tree.selection()[0]
        file_path = self.tree.item(selected_item, 'values')
        if file_path:  # If it's a file (file path exists)
            self.file_list.remove(file_path[0])
        self.excluded_items.discard(self.tree.item(selected_item, 'text'))  # Remove from exclusions if necessary
        self.tree.delete(selected_item)

    def exclude_item(self):
        selected_item = self.tree.selection()[0]
        item_text = self.tree.item(selected_item, 'text')
        item_values = self.tree.item(selected_item, 'values')
        full_path = item_values[0] if item_values else None

        if full_path:
            self.excluded_items.add(full_path)
        else:
            self.excluded_items.add(item_text)

        self.tree.item(selected_item, tags='excluded')
        self.tree.tag_configure('excluded', background='red')

    def include_item(self):
        selected_item = self.tree.selection()[0]
        item_text = self.tree.item(selected_item, 'text')
        item_values = self.tree.item(selected_item, 'values')
        full_path = item_values[0] if item_values else None

        if full_path:
            self.excluded_items.discard(full_path)
        else:
            self.excluded_items.discard(item_text)

        self.tree.item(selected_item, tags='')  # Remove the 'excluded' tag
        self.tree.tag_configure('excluded', background='')  # Reset the background color

    def drop_file(self, event):
        files = self.master.tk.splitlist(event.data)
        for path in files:
            if os.path.isdir(path):
                self.add_folder(path)
            else:
                self.add_files([path])

    def add_files(self, files):
        extensions = self._get_extensions()  # Filter based on extensions
        for file in files:
            if any(file.endswith(ext) for ext in extensions):
                if file not in self.file_list:
                    node = self.tree.insert('', 'end', text=os.path.basename(file), values=[file])
                    self.file_list.append(file)

    def get_selected_files(self):
        return self.file_list

    def get_project_structure(self):
        return {
            'structure': self._get_tree_structure('')
        }

    def _get_tree_structure(self, parent):
        structure = {}
        for child in self.tree.get_children(parent):
            item_text = self.tree.item(child, "text")
            item_values = self.tree.item(child, "values")
            tags = self.tree.item(child, 'tags')

            if self.tree.get_children(child):
                # It's a folder
                structure[item_text] = {
                    'structure': self._get_tree_structure(child)
                }
                if 'excluded' in tags:
                    structure[item_text]['excluded'] = True
            else:
                # It's a file
                if item_values and len(item_values) > 0:
                    structure[item_text] = {
                        'path': item_values[0]
                    }
                    if 'excluded' in tags:
                        structure[item_text]['excluded'] = True
                else:
                    print(f"Warning: No values found for item {item_text} (Tree node: {child})")  # Debugging statement

        return structure

    def load_project_structure(self, project_data, parent=''):
        structure = project_data.get('structure', {})

        for key, value in structure.items():
            if isinstance(value, dict) and 'structure' in value:
                # It's a folder
                node = self.tree.insert(parent, 'end', text=key, open=True)
                self.load_project_structure(value, node)
                if value.get('excluded', False):
                    self.tree.item(node, tags='excluded')
                    self.tree.tag_configure('excluded', background='red')
            else:
                # It's a file
                path = value['path']
                node = self.tree.insert(parent, 'end', text=key, values=[path])
                self.file_list.append(path)
                
                # Check if the file exists
                if not os.path.exists(path):
                    self.tree.item(node, tags='missing')
                    self.tree.tag_configure('missing', background='orange')
                elif value.get('excluded', False):
                    self.tree.item(node, tags='excluded')
                    self.tree.tag_configure('excluded', background='red')

    def mark_missing_files(self, missing_files):
        for item in self.tree.get_children():
            file_path = self.tree.item(item, 'values')[0]
            if file_path in missing_files:
                self.tree.item(item, tags='missing')
                self.tree.tag_configure('missing', background='orange')

    def clear_files(self):
        self.file_list = []
        self.excluded_items = set()
        self.tree.delete(*self.tree.get_children())
