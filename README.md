# Code Prompt Builder
Tool for creating promt for chatbots from project code

[Русская документация](README.ru.md)

## Features
- Recursively scans project directories
- Respects `.gitignore` rules
- Supports custom exclude patterns
- Handles binary files and Unicode names
- Cross-platform (Windows/macOS/Linux)

## Requirements
- Python 3.6+
- No external dependencies are required

## Installation
Simply download `code_prompt_builder.py` to your projects directory.

## Usage
```bash
python code_prompt_builder.py PROJECT_DIR [OUTPUT_FILE] [--exclude PATTERN1 PATTERN2...]
```

### Help message
Use the `-h` option to view the help message

### Platform Examples

#### Windows
- Basic usage
    ```
    python code_prompt_builder.py C:\my_project project_code.txt
    ```
- Exclude temp files
    ```
    python code_prompt_builder.py C:\my_project output.txt --exclude "*.tmp" "build\*"
    ```

#### macOS/Linux
- Basic usage
    ```
    python3 code_prompt_builder.py ./my_project output.txt
    ```

- Exclude hidden and swap files
    ```
    python3 code_prompt_builder.py ./my_project output.txt --exclude ".*" "*.swp"
    ```

## Testing
Run tests with:
```
python -m unittest test_code_prompt_builder.py
```
