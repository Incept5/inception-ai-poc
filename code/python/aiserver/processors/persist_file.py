# processors/persist_file.py

def persist_file(thread_id: str, file_path: str, file_type: str, file_content: str):
    print(f"Received file for thread {thread_id}:")
    print(f"  Path: {file_path}")
    print(f"  Type: {file_type}")
    print(f"  Content length: {len(file_content)} characters")
    print("  (File not actually saved, just printing information)")