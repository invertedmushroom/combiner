import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tkinterdnd2 import TkinterDnD
from gui.file_selector import FileSelector
from gui.project_manager import ProjectManager
from core.file_combiner import FileCombiner
from tkinter import Button, filedialog, messagebox

class MainWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("File Combiner Application")

        # Initialize GUI components
        self.file_selector = FileSelector(self.root)
        self.project_manager = ProjectManager(self.root, self.file_selector)
        self.combine_button = Button(self.root, text="Combine Files", command=self.combine_files)

        # Layout management
        self.file_selector.pack()
        self.project_manager.pack()
        self.combine_button.pack()

    def combine_files(self):
        print("Combine Files button clicked")  # Debugging statement

        # Prompt user to select the output file path
        output_file = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")],
            title="Save Combined File As"
        )

        if not output_file:
            print("No output file selected, operation cancelled.")  # Debugging statement
            return

        # Check if the file already exists and confirm overwrite
        if os.path.exists(output_file):
            if not messagebox.askyesno("Overwrite Confirmation", f"'{output_file}' already exists. Do you want to overwrite it?"):
                print("User chose not to overwrite the existing file.")  # Debugging statement
                return

        selected_files_structure = self.file_selector.get_project_structure()['structure']
        print(f"Selected Files Structure: {selected_files_structure}")  # Debugging statement

        # Combine the selected files into the output file
        FileCombiner.combine_files(selected_files_structure, output_file)
        print("File combining process completed")  # Debugging statement

        # Inform the user of success
        # messagebox.showinfo("Success", f"Files have been successfully combined into '{output_file}'.")

if __name__ == "__main__":
    root = TkinterDnD.Tk()  # Use TkinterDnD.Tk instead of Tk.Tk
    app = MainWindow(root)
    root.mainloop()
