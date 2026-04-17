import os
import re

directory = 'c:/Users/akhil/Documents/Desktop/Spam_detection (2)/Spam_detection/frontend/src'
for root, dirs, files in os.walk(directory):
    for file in files:
        if file.endswith('.jsx') or file.endswith('.js'):
            filepath = os.path.join(root, file)
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if 'http://127.0.0.1:5000' in content:
                # Replace backtick strings: `http://127.0.0.1:5000...`
                # becomes `${import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:5000'}...`
                content = re.sub(
                    r'`http://127\.0\.0\.1:5000(/.*?)`', 
                    r'`${import.meta.env.VITE_API_BASE_URL || \'http://127.0.0.1:5000\'}\1`', 
                    content
                )
                
                # Replace single quote strings: 'http://127.0.0.1:5000...'
                # becomes (import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:5000') + '/...'
                content = re.sub(
                    r'\'http://127\.0\.0\.1:5000(/.*?)\'', 
                    r'(import.meta.env.VITE_API_BASE_URL || \'http://127.0.0.1:5000\') + \'\1\'', 
                    content
                )
                
                # Replace double quote strings
                content = re.sub(
                    r'\"http://127\.0\.0\.1:5000(/.*?)\"', 
                    r'(import.meta.env.VITE_API_BASE_URL || \'http://127.0.0.1:5000\') + \"\1\"', 
                    content
                )
                
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f'Updated {filepath}')
