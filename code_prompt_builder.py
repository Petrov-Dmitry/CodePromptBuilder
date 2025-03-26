#!/usr/bin/env python3
"""
Code Prompt Builder - Creates AI-ready prompts from project code
Usage:
  python code_prompt_builder.py <directory> [output_file] [--exclude PATTERNS]
"""

import sys
import re
import fnmatch
import mimetypes
import argparse
from pathlib import Path

def debug_log(message):
    """Вывод отладочной информации в stderr"""
    print(f"DEBUG: {message}", file=sys.stderr)

def parse_gitignore(gitignore_path):
    """Парсер .gitignore с поддержкой сложных шаблонов"""
    patterns = []
    if not gitignore_path.exists():
        return patterns
    
    try:
        with open(gitignore_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    line = line.replace('\\', '/')
                    patterns.append(line)
    except Exception as e:
        debug_log(f"Error reading {gitignore_path}: {e}")
    
    return patterns

def should_ignore(path, ignore_patterns, root_dir, exclude_patterns=None):
    """Проверка, должен ли файл/директория быть проигнорирован"""
    try:
        rel_path = str(path.relative_to(root_dir)).replace('\\', '/')
    except ValueError:
        return False

    # Проверка явных исключений (инвертированные правила)
    for pattern in ignore_patterns:
        if pattern.startswith('!'):
            clean_pattern = pattern[1:].replace('\\', '/')
            if fnmatch.fnmatch(rel_path, clean_pattern) or fnmatch.fnmatch(path.name, clean_pattern):
                return False

    # Явное исключение для .git директории
    if path.name == '.git' and path.is_dir():
        return True

    # Проверка дополнительных исключений (--exclude)
    if exclude_patterns:
        for pattern in exclude_patterns:
            pattern = pattern.replace('\\', '/')
            if '/' not in pattern and fnmatch.fnmatch(path.name, pattern):
                return True
            elif fnmatch.fnmatch(rel_path, pattern):
                return True

    # Всегда включаем сам .gitignore файл (если не исключен явно)
    if path.name == '.gitignore':
        return bool(exclude_patterns and '.gitignore' in exclude_patterns)

    # Обрабатываем .gitignore правила
    for pattern in ignore_patterns:
        if pattern.startswith('!'):
            continue  # Пропускаем инвертированные правила

        pattern = pattern.replace('\\', '/')
        is_dir_pattern = pattern.endswith('/')
        clean_pattern = pattern.rstrip('/')

        if pattern.startswith('/'):
            if rel_path == clean_pattern[1:]:
                return True
            if is_dir_pattern and rel_path.startswith(clean_pattern[1:] + '/'):
                return True
            continue

        regex = fnmatch.translate(clean_pattern)
        regex = regex.replace(r'.*', r'[^/]*')
        regex = regex.replace(r'\Z', r'($|/)') if is_dir_pattern else regex.replace(r'\Z', r'$')

        if '/' in pattern:
            regex = regex.replace(r'\/', r'(/|\\)')
            if not re.search(r'(^|/)' + regex, rel_path):
                continue
        else:
            if not re.search(r'(^|/)' + regex + r'$', rel_path):
                continue

        return True

    return False

def collect_files(directory, root_dir, ignore_patterns, exclude_patterns=None):
    """Рекурсивный сбор файлов с учётом всех исключений"""
    files = []
    try:
        for item in directory.iterdir():
            rel_path = str(item.relative_to(root_dir)).replace('\\', '/')
            
            in_ignored_dir = False
            for part in Path(rel_path).parts:
                test_path = root_dir / part
                if should_ignore(test_path, ignore_patterns, root_dir, exclude_patterns):
                    in_ignored_dir = True
                    break
            
            if in_ignored_dir:
                continue

            if should_ignore(item, ignore_patterns, root_dir, exclude_patterns):
                continue

            if item.is_dir():
                files.extend(collect_files(item, root_dir, ignore_patterns, exclude_patterns))
            else:
                files.append(item)
    except PermissionError:
        debug_log(f"Permission denied: {directory}")
    return files

def get_file_type(file_path):
    """Определяем тип файла для бинарных файлов"""
    mime_type, _ = mimetypes.guess_type(file_path)
    if mime_type:
        return mime_type.split('/')[-1]
    return 'binary'

def parse_arguments():
    """Парсинг аргументов командной строки"""
    parser = argparse.ArgumentParser(
        description='Process directory and create output file',
        epilog='Examples:\n'
               '  Windows:\n'
               '    python code_prompt_builder.py C:\\project output.txt --exclude "*.tmp"\n'
               '  macOS/Linux:\n'
               '    python3 code_prompt_builder.py ./project output.txt --exclude "*.swp"',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument('directory', help='Directory to process')
    parser.add_argument('output_file', nargs='?', help='Output file path')
    parser.add_argument('--exclude', nargs='+', help='Exclude patterns (supports *)')
    return parser.parse_args()

def main():
    args = parse_arguments()
    
    try:
        target_dir = Path(args.directory).resolve()
    except Exception as e:
        print(f"Error processing directory path: {e}", file=sys.stderr)
        sys.exit(1)

    output_file = Path(args.output_file).resolve() if args.output_file else Path(f"{target_dir.name}.txt").resolve()
    exclude_patterns = [p.replace('\\', '/') for p in args.exclude] if args.exclude else None

    if not target_dir.exists() or not target_dir.is_dir():
        print(f"Error: Invalid directory: {target_dir}", file=sys.stderr)
        sys.exit(1)

    gitignore_path = target_dir / '.gitignore'
    ignore_patterns = parse_gitignore(gitignore_path)
    files = collect_files(target_dir, target_dir, ignore_patterns, exclude_patterns)
    
    if (gitignore_path.exists() and 
        gitignore_path not in files and 
        (not exclude_patterns or '.gitignore' not in exclude_patterns)):
        files.append(gitignore_path)

    debug_log(f"Total files to process: {len(files)}")

    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            for file in sorted(files, key=lambda x: str(x).lower()):
                rel_path = file.relative_to(target_dir)
                display_path = str(rel_path).replace('\\', '/')
                
                try:
                    content = file.read_text(encoding='utf-8')
                    if not content.strip():
                        f.write(f"{display_path} - is empty (no content)\n\n")
                        continue
                    
                    f.write(f"{display_path}\n>>>>>>>>>>>>>>>>>>>>>>>>\n")
                    f.write(f"{content}\n<<<<<<<<<<<<<<<<<<<<<<<<\n\n")
                except UnicodeDecodeError:
                    f.write(f"{display_path} - binary file ({get_file_type(file)})\n\n")
                except Exception as e:
                    f.write(f"{display_path} - error reading file: {e}\n\n")
        
        print(f"Success: Saved {len(files)} files to {output_file}")
    except Exception as e:
        print(f"Error writing output: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
