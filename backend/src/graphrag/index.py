import subprocess
from .constants.constants import INDEX_DIR
def index():
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
