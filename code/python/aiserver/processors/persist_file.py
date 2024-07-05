# code/python/aiserver/processors/persist_file.py

import os


def persist_file(thread_id: str, file_path: str, file_type: str, file_content: str):
    base_dir = '/app/persisted_files/__threads'
    full_path = os.path.join(base_dir, thread_id, file_path.lstrip('/'))

    os.makedirs(os.path.dirname(full_path), exist_ok=True)

    with open(full_path, 'w') as f:
        f.write(file_content)

    print(f"File saved: {full_path}")