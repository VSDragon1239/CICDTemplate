import os
import sys
import argparse
from pathlib import Path


def get_project_data_paths(project_dir, exclude_dirs=None, valid_extensions=None):
    """Собирает файлы .py, .ui, .qrc из проекта для включения в datas."""
    if exclude_dirs is None:
        exclude_dirs = ['__pycache__', 'build', 'dist', 'venv', 'ui_compiled']
    if valid_extensions is None:
        valid_extensions = ['.py', '.ui', '.qrc']

    data_paths = []
    for root, dirs, files in os.walk(project_dir):
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        for fn in files:
            ext = os.path.splitext(fn)[1].lower()
            if ext in valid_extensions:
                abs_path = os.path.join(root, fn)
                rel_path = os.path.relpath(root, project_dir).replace("\\", "/")
                data_paths.append((abs_path.replace("\\", "/"), rel_path))
    return data_paths


def generate_spec(project_dirs=None, main_script="manage.py", onefile=False, output_file="main.spec"):
    """Генерирует .spec файл для PyInstaller на основе списка директорий проектов."""
    all_data = []
    if project_dirs:
        for proj in project_dirs:
            all_data += get_project_data_paths(proj)
    else:
        all_data = get_project_data_paths("MainProject")

    entries = ["('%s', '%s')" % (src, dst or '.') for src, dst in all_data]
    data_entries = ",\n        ".join(entries)

    main_script_clean = main_script.replace("\\", "/")
    pathex_list = [p.replace("\\", "/") for p in project_dirs]

    if onefile:
        spec_content = f"""# -*- mode: python ; coding: utf-8 -*-
import os
block_cipher = None

a = Analysis(
    ['{main_script_clean}'],
    pathex={pathex_list},
    datas=[
        {data_entries}
    ],
    hiddenimports=[],
    hookspath=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    name='MyApp',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
)
"""
    else:
        spec_content = f"""# -*- mode: python ; coding: utf-8 -*-
import os
block_cipher = None

a = Analysis(
    ['{main_script_clean}'],
    pathex={pathex_list},
    datas=[
        {data_entries}
    ],
    hiddenimports=[],
    hookspath=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='MyApp',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    name='MyApp',
)
"""
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(spec_content)
    print(f"Spec file generated: {output_file}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate PyInstaller spec file for multi-project application.")
    parser.add_argument("project_dirs", nargs="+", help="List of project directories (relative to current dir)")
    parser.add_argument("--main-script", required=True,
                        help="Path to main script (e.g., WorkUserInterfaceManager/manage.py)")
    parser.add_argument("--onefile", action="store_true", help="Generate spec for one-file mode (single EXE)")
    parser.add_argument("--output", default="main.spec", help="Output spec file name")
    args = parser.parse_args()

    # Преобразуем относительные пути в абсолютные от текущей директории
    base = os.getcwd()
    project_dirs = [os.path.join(base, p) for p in args.project_dirs]
    main_script = os.path.join(base, args.main_script)

    generate_spec(project_dirs, main_script, onefile=args.onefile, output_file=args.output)
