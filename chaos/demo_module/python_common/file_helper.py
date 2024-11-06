from pathlib import Path

def get_file_text(filepath: str):
   
    file = Path(filepath)

    if file.exists():
        with open(str(file), 'r') as f:
            return f.read()
    return ''

if __name__ == "__main__":
    print(get_file_text(r'U:\Projects\NextGen Import\2023-10-05\assets\table.sql'))
