import os
import re
import sys

def remove_python_comments(content):
    # Remove full-line comments
    content = re.sub(r'^\s*#.*$', '', content, flags=re.MULTILINE)
    # Remove end-of-line comments (but not inside strings)
    content = re.sub(r'(?<![\'"])#.*$', '', content, flags=re.MULTILINE)
    return content

def remove_html_comments(content):
    # Remove HTML comments
    content = re.sub(r'<!--[\s\S]*?-->', '', content)
    return content

def remove_js_comments(content):
    # Remove single-line JavaScript comments
    content = re.sub(r'^\s*\/\/.*$', '', content, flags=re.MULTILINE)
    # Remove multi-line JavaScript comments
    content = re.sub(r'\/\*[\s\S]*?\*\/', '', content)
    return content

def remove_css_comments(content):
    # Remove CSS comments
    content = re.sub(r'\/\*[\s\S]*?\*\/', '', content)
    return content

def process_file(file_path):
    print(f"Processing: {file_path}")
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        original_content = content
        
        # Apply appropriate comment removal based on file extension
        ext = os.path.splitext(file_path)[1].lower()
        if ext == '.py':
            content = remove_python_comments(content)
        elif ext in ['.html', '.htm']:
            content = remove_html_comments(content)
        elif ext in ['.js']:
            content = remove_js_comments(content)
        elif ext in ['.css']:
            content = remove_css_comments(content)
        else:
            # Skip unsupported file types
            print(f"Skipping unsupported file type: {file_path}")
            return
        
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
    for root, dirs, files in os.walk(directory_path):
        for file in files:
            file_path = os.path.join(root, file)
            process_file(file_path)

if __name__ == "__main__":
    target_dir = "App"
    if not os.path.exists(target_dir):
        print(f"Directory {target_dir} not found!")
        sys.exit(1)
        
    print(f"Removing comments from all files in {target_dir}...")
    process_directory(target_dir)
    print("Comment removal completed.") 