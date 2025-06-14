import subprocess
import os
import shutil
from .constants.constants import INDEX_DIR,FILE_DIR
def index():
    shutil.rmtree(INDEX_DIR+'cache', ignore_errors=True)
    shutil.rmtree(INDEX_DIR+'logs', ignore_errors=True)
    shutil.rmtree(INDEX_DIR+'output', ignore_errors=True)
    # check file in directory
    if not os.path.exists(INDEX_DIR) or not os.listdir(INDEX_DIR):
        return True
    result = subprocess.run(
        ["graphrag", "index", "--root", INDEX_DIR],
       
    )
    if result.returncode == 0:
        print("Indexing completed successfully.")
        return True
    else:
        print("Indexing failed.")
        return False
def update():
    result = subprocess.run(
        ["graphrag", "update", "--root", INDEX_DIR],
       
    )
    if result.returncode == 0:
        print("Updating completed successfully.")
        return True
    else:
        print("Updating failed.")
        return False
