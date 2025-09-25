import PyInstaller.__main__
import os
import shutil

# --- Configuration ---
APP_NAME = "RFQ-Tracker"
ENTRY_POINT = "main.py"
ICON_PATH = "icon.ico"

# --- PyInstaller Options ---
pyinstaller_options = [
    f'--name={APP_NAME}',
    '--onedir', # Use one-directory mode
    '--windowed', # No console window
    f'--icon={ICON_PATH}',
    # Add data files. The format is 'source:destination_in_bundle'
    '--add-data=config.json:.',
    '--add-data=mock_projects:mock_projects',
    # Hidden imports that PyInstaller might miss
    '--hidden-import=PyQt6.sip',
    '--hidden-import=pymongo',
    '--hidden-import=requests',
]

def main():
    """Runs PyInstaller and performs post-build cleanup."""
    # Construct the command
    command = [ENTRY_POINT] + pyinstaller_options

    print(f"Running PyInstaller with command: {' '.join(command)}")

    # Run PyInstaller
    PyInstaller.__main__.run(command)

    print("\nPyInstaller build complete.")

    # --- Post-build steps ---
    # The 'vendor' directory will be created by the app at runtime,
    # so we don't need to create it here. The logic in main.py already handles this.

    dist_path = os.path.join('dist', APP_NAME)

    print("\nBuild process finished.")
    print(f"Executable and data files are in: {dist_path}")


if __name__ == '__main__':
    main()