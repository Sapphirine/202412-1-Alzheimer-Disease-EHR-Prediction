import pandas as pd
import numpy as np
import re
from transformers import MarianMTModel, MarianTokenizer

tokenizer = MarianTokenizer.from_pretrained('Helsinki-NLP/opus-mt-zh-en')
model = MarianMTModel.from_pretrained('Helsinki-NLP/opus-mt-zh-en')

def remove_chinese(text):
    if not isinstance(text, str): 
        return "", text
    chinese_pattern = re.compile(r'[\u4e00-\u9fff，。！？、；：]+')
    # retrieve chinese part 
    chinese_parts = " ".join(chinese_pattern.findall(text))
    # remove chinese part
    cleaned_text = chinese_pattern.sub("", text)  
    return chinese_parts, cleaned_text

def translate_chinese_to_english(text):
    """Translate Chinese text to English."""
    if not text.strip(): 
        return ""
    inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True)
    translated = model.generate(**inputs)
    return tokenizer.decode(translated[0], skip_special_tokens=True)

def replace_chinese_with_translation(text):
    chinese_parts, cleaned_text = remove_chinese(text)  
    if chinese_parts:  
        translated_text = translate_chinese_to_english(chinese_parts) 
        
        return f"{cleaned_text} {translated_text}".strip()  
    return cleaned_text 