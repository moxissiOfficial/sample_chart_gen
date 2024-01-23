import os
import shutil


class RemoveFiles:
    def __init__(self) -> None:
        pass

    def remove_files(self, UPLOAD_FOLDER):
        # Verify that the folder exists
        if os.path.exists(UPLOAD_FOLDER):
            # Delete folder contents (files and subfolders)
            shutil.rmtree(UPLOAD_FOLDER)
            # Create an empty folder
            os.makedirs(UPLOAD_FOLDER)
            print(f"Obsah složky {UPLOAD_FOLDER} byl úspěšně vymazán.")
        else:
            print(f"Složka {UPLOAD_FOLDER} neexistuje.")
