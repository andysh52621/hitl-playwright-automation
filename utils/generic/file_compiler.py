import os
import re
from pathlib import Path

# Define excluded folders
EXCLUDED_FOLDERS = {
    'venv',
    '.venv',
    '__pycache__',
    '.git',
    '.pytest_cache',
    'node_modules',
    'dist',
    'build',
    'venv310'
}


def is_target_file(file_path: str) -> bool:
    """Check if the file is one of the target types."""
    return file_path.endswith(('.py', '.yaml', '.yml'))


def is_excluded_folder(folder_path: str) -> bool:
    """Check if the folder should be excluded."""
    # Check if any part of the path contains an excluded folder
    return any(excluded in folder_path.split(os.sep) for excluded in EXCLUDED_FOLDERS)


def extract_imports(content: str) -> str:
    """Extract only import statements from Python content."""
    import_lines = []

    # Find all import statements
    import_pattern = r'^(import .*|from .* import .*)$'
    matches = re.finditer(import_pattern, content, re.MULTILINE)

    for match in matches:
        import_lines.append(match.group(0))

    return '\n'.join(import_lines) if import_lines else "No imports found"


def clean_python_content(content: str) -> str:
    """Clean Python content by removing package-related code test."""
    # Remove package-related code
    content = re.sub(r'^__version__.*$', '', content, flags=re.MULTILINE)
    content = re.sub(r'^__author__.*$', '', content, flags=re.MULTILINE)
    content = re.sub(r'^__all__.*$', '', content, flags=re.MULTILINE)

    # Remove empty lines and extra whitespace
    content = '\n'.join(line for line in content.split('\n') if line.strip())
    return content


def read_file_content(file_path: str) -> tuple[str, str]:
    """Read and return both imports and content from a file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()

            if file_path.endswith('.py'):
                imports = extract_imports(content)
                cleaned_content = clean_python_content(content)
                return imports, cleaned_content
            elif file_path.endswith(('.yaml', '.yml')):
                # For YAML files, return empty imports and full content
                return "No imports found", content
            return "Unsupported file type", "Unsupported file type"
    except Exception as e:
        error_msg = f"Error reading file {file_path}: {str(e)}"
        return error_msg, error_msg


def format_file_content(file_path: str, imports: str, content: str) -> str:
    """Format the file content with a header and separator."""
    separator = "=" * 80
    return f"\n{separator}\nFile: {file_path}\n{separator}\n\nIMPORTS:\n{imports}\n\nCONTENT:\n{content}\n"


def compile_files(start_dir: str, output_file: str):
    """
    Compile imports and content from .py, .yaml, and .yml files into a single output file.

    Args:
        start_dir: Directory to start searching from
        output_file: Path to the output file
    """
    # Convert to Path object for better handling
    start_path = Path(start_dir)

    # Ensure output directory exists
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Get all target files, excluding specified directories
    target_files = []
    for root, _, files in os.walk(start_dir):
        # Skip excluded folders
        if is_excluded_folder(root):
            continue

        for file in files:
            if is_target_file(file):
                full_path = os.path.join(root, file)
                target_files.append(full_path)

    # Sort files for consistent output
    target_files.sort()

    # Write to output file
    with open(output_file, 'w', encoding='utf-8') as outfile:
        # Write header
        outfile.write(f"Compiled Files from: {start_dir}\n")
        outfile.write(f"Excluded Folders: {', '.join(sorted(EXCLUDED_FOLDERS))}\n")
        outfile.write(f"Total Files: {len(target_files)}\n\n")

        # Write each file's content
        for file_path in target_files:
            imports, content = read_file_content(file_path)
            formatted_content = format_file_content(file_path, imports, content)
            outfile.write(formatted_content)


def main():
    # Get current directory as default
    current_dir = os.getcwd()

    # Get user input for directory and output file
    start_dir = input(f"Enter directory to scan (default: {current_dir}): ") or current_dir
    output_file = input("Enter output file path (default: compiled_files.txt): ") or "compiled_files.txt"

    print(f"\nScanning directory: {start_dir}")
    print(f"Excluded folders: {', '.join(sorted(EXCLUDED_FOLDERS))}")
    print(f"Output will be saved to: {output_file}")

    try:
        compile_files(start_dir, output_file)
        print(f"\nSuccessfully compiled files to {output_file}")
    except Exception as e:
        print(f"Error: {str(e)}")


if __name__ == "__main__":
    main()
