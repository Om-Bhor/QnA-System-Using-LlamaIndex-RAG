import json
import os
from datetime import datetime
file_db = "uploaded_files.json"
def load_files_registry():
    if os.path.exists(file_db):
        with open(file_db,"r") as f:
            return json.load(f)
    return []

def save_file_registry(data):
    with open(file_db,"w") as f:
        json.dump(data,f,indent=4)

def register_file(filename):
    registry = load_files_registry()
    for file in registry:
        if file["filename"]==filename:
            return
    registry.append(
        {
            "filename":filename,
            "uploaded_date":str(datetime.now()),
            "processed":True
        }
    )
    save_file_registry(registry)

def get_uploaded_files():
    return [
        file
        for file in os.listdir("Data")
        if not file.startswith(".")
        ]
def delete_file(filename):
    if isinstance(filename,dict):
        filename = filename["filename"]
    file_path = os.path.join(
        "Data",
        filename
    )
    if os.path.exists(file_path):
        os.remove(file_path)
    registry = load_files_registry()
    registry = [
        file
        for file in registry
        if file["filename"] != filename
    ]

    save_file_registry(registry)

