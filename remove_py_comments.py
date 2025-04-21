import os
import re
import sys

def remove_python_comments(content):
    # Remove full-line comments
    content = re.sub(r'^\s*#.*$', '', content, flags=re.MULTILINE)
    # Remove end-of-line comments (but not inside strings)
    content = re.sub(r'(?<![\'"])#.*$', '', content, flags=re.MULTILINE)
    # Clean up any extra blank lines from removed comments
    content = re.sub(r'\n\s*\n\s*\n', '\n\n', content)
    return content

def process_file(file_path):
    print(f"Processing: {file_path}")
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        original_content = content
        content = remove_python_comments(content)
        
        # Only write the file if changes were made
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(content)
            print(f"Comments removed from {file_path}")
        else:
            print(f"No comments found in {file_path}")
            
    except Exception as e:
        print(f"Error processing {file_path}: {e}")

def process_directory(directory_path):
    for file in os.listdir(directory_path):
        if file.endswith('.py'):
            file_path = os.path.join(directory_path, file)
            if os.path.isfile(file_path):
                process_file(file_path)

if __name__ == "__main__":
    app_dir = "App"
    if not os.path.exists(app_dir):
        print(f"Directory {app_dir} not found!")
        sys.exit(1)
    
    # Process views directory
    views_dir = os.path.join(app_dir, "views")
    if os.path.exists(views_dir):
        print(f"Processing Python files in {views_dir}...")
        process_directory(views_dir)
    else:
        print(f"Views directory not found at {views_dir}")
    
    # Process models directory
    models_dir = os.path.join(app_dir, "models")
    if os.path.exists(models_dir):
        print(f"Processing Python files in {models_dir}...")
        process_directory(models_dir)
    else:
        print(f"Models directory not found at {models_dir}")
    
    print("Comment removal completed.") 