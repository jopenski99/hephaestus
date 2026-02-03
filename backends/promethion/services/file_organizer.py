import os
import shutil
import logging

def create_filetype_directories(directory):
    """Creates directories for different file types."""
    filetypes = {
        'Images': ['.jpg', '.jpeg', '.png', '.gif', '.svg', '.webp', '.tiff', '.bmp'],
        'Programs': ['exe'],
        'Documents': ['.txt', '.pdf', '.doc', '.docx', '.xls', '.xlsx','csv'],
        'Audio': ['.mp3', '.wav', '.ogg'],
        'Video': ['.mp4', '.mov', '.avi'],
        'Web': ['.html', '.json', '.js', '.css','yml','yaml','.htm'],
        'Compressed': ['.zip', '.rar'],
        'Torrents': ['.torrent'],
        'Iso': ['.iso'],
        'Shortcuts': ['.lnk'],
        'Adobe': ['.psd', '.ai', '.indd'],
        'Fonts': ['.ttf', '.otf', '.woff'],
        'Scripts': ['.py', '.sh', '.bat', '.pl'],
    }

    for filetype, extensions in filetypes.items():
        for root, dirs, files in os.walk(directory):
            for file in files:
                logging.info('extensions: %s', extensions)
                if any(file.endswith(ext) for ext in extensions):
                    file_path = os.path.join(root, file)
                    dest_dir = os.path.join(directory, filetype)
                    os.makedirs(dest_dir, exist_ok=True)
                    shutil.move(file_path, os.path.join(dest_dir, file))

def create_subdirectories(directory):
    """Creates subdirectories in the given directory."""
    for root, dirs, files in os.walk(directory):
        for dir in dirs:
            dir_path = os.path.join(root, dir)
            if not os.path.exists(os.path.join(directory, dir)):
                os.makedirs(os.path.join(directory, dir))

def move_files_to_subdirectories(directory):
    """Moves files to their respective subdirectories."""
    for root, dirs, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            if os.path.isdir(file_path):
                continue
            file_ext = os.path.splitext(file)[1].lower()
            if file_ext in ['.zip', '.rar']:
                dest_dir = os.path.join(directory, 'compressed')
                shutil.move(file_path, os.path.join(dest_dir, file))
            else:
                for sub_dir in dirs:
                    sub_dir_path = os.path.join(root, sub_dir)
                    if os.path.exists(os.path.join(sub_dir_path, file)):
                        shutil.move(file_path, os.path.join(sub_dir_path, file))
                        break
def delete_empty_folders(directory):
    """Deletes empty folders in the given directory."""
    for root, dirs, files in os.walk(directory, topdown=False):
        for dir in dirs:
            dir_path = os.path.join(root, dir)
            if not os.listdir(dir_path):
                os.rmdir(dir_path)
# Usage
directory = 'C:/Users/Game/Downloads'
create_filetype_directories(directory)
create_subdirectories(directory)
move_files_to_subdirectories(directory)
delete_empty_folders(directory)