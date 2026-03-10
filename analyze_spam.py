import pandas as pd
from collections import Counter
import re

def get_top_spam_words(file_path, top_n=50):
    try:
        # Load the dataset
        df = pd.read_csv(file_path, encoding='latin-1')
        
        # Keep only the first two columns (label and text) and rename them
        df = df.iloc[:, :2]
        df.columns = ['label', 'message']
        
        # Filter only spam messages
        spam_msgs = df[df['label'] == 'spam']['message'].dropna()
        
        # Tokenize and count
        all_words = []
        for msg in spam_msgs:
            # simple tokenization, lowercase, remove non-alpha
            words = re.findall(r'\b[a-z]{4,}\b', str(msg).lower())
            all_words.extend(words)
            
        counter = Counter(all_words)
        
        print("Top 50 words in SPAM messages:")
        for word, count in counter.most_common(top_n):
            print(f"{word}: {count}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    get_top_spam_words('spam.csv')
