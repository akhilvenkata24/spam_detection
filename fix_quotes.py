import os

directory = r'c:\Users\akhil\Documents\Desktop\Spam_detection (2)\Spam_detection\frontend\src'
for root, _, files in os.walk(directory):
    for filename in files:
        if filename.endswith('.jsx'):
            filepath = os.path.join(root, filename)
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            if r"\'" in content:
                print(f'Fixing {filepath}')
                content = content.replace(r"\'", "'")
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
