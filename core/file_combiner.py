import os

class FileCombiner:
    @staticmethod
    def combine_files(structure, output_file):
        # Generate the ASCII tree representation
        file_tree = FileCombiner.generate_file_tree(structure)

        with open(output_file, 'w', encoding='utf-8') as out_file:
            # Write the file tree at the beginning of the output file
            out_file.write("Combined File Structure:\n")
            out_file.write(file_tree)
            out_file.write("\n\n")

            # Combine the files
            FileCombiner._combine_files_recursive(structure, out_file)

    @staticmethod
    def _combine_files_recursive(structure, out_file, base_path=''):
        for name, info in structure.items():
            if isinstance(info, dict) and 'structure' in info:
                # It's a folder
                if not info.get('excluded', False):
                    FileCombiner._combine_files_recursive(info['structure'], out_file, os.path.join(base_path, name))
            elif isinstance(info, dict):
                # It's a file
                file_path = info['path']
                if info.get('excluded', False):
                    out_file.write(f"\n\n{'='*50}\n# File: {file_path} (EXCLUDED)\n{'='*50}\n\n")
                elif not os.path.exists(file_path):
                    out_file.write(f"\n\n{'='*50}\n# File: {file_path} (MISSING)\n{'='*50}\n\n")
                else:
                    out_file.write(f"\n\n{'='*50}\n# File: {file_path}\n{'='*50}\n\n")
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
                        content = file.read()
                        out_file.write(f'"""\n{content}\n"""\n')

    @staticmethod
    def generate_file_tree(structure, prefix=''):
        tree_str = ''
        items = list(structure.items())
        for i, (name, info) in enumerate(items):
            connector = '└── ' if i == len(items) - 1 else '├── '
            tree_str += f"{prefix}{connector}{name}\n"
            if isinstance(info, dict) and 'structure' in info:
                if not info.get('excluded', False):
                    extension = '    ' if i == len(items) - 1 else '│   '
                    tree_str += FileCombiner.generate_file_tree(info['structure'], prefix + extension)

        return tree_str
