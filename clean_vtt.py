import re

def clean_vtt(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Remove WEBVTT and headers
    content = re.sub(r'WEBVTT.*?\n\n', '', content, flags=re.DOTALL)
    # Remove timestamps like 00:00:01.240 --> 00:00:04.150 align:start position:0%
    content = re.sub(r'\d{2}:\d{2}:\d{2}\.\d{3} --> \d{2}:\d{2}:\d{2}\.\d{3}.*\n', '', content)
    # Remove tags like <00:00:01.560><c>
    content = re.sub(r'<[^>]+>', '', content)
    
    lines = content.split('\n')
    cleaned_lines = []
    prev_line = ""
    for line in lines:
        line = line.strip()
        if not line or line == prev_line:
            continue
        cleaned_lines.append(line)
        prev_line = line
        
    full_text = " ".join(cleaned_lines)
    # Remove duplicate consecutive words (VTT generated captions often have a lot of duplicates)
    full_text = re.sub(r'\b(\w+)( \1\b)+', r'\1', full_text)
    
    with open("cleaned_transcript.txt", "w", encoding='utf-8') as f:
        f.write(full_text)

clean_vtt('ОБУЧЕНИЕ скальпингу 📚🍏 (Работает в 2026!) [NfZhOuRGTto].ru.vtt')
print("Cleaned!")
