import os
import re
import pandas as pd
from langchain.llms import OpenAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.chat_models import ChatOpenAI

os.environ["OPENAI_API_KEY"] = "place_holder"

llm = ChatOpenAI(model_name='gpt-4')


def retrieve_info(df, max_tokens = 8194):
    context_strings = []
    for _, row in df.iterrows():
        s = row["主訴(S)"]
        a = row["診斷(A)"]
        p = row["計畫(P)"]
        cdr = row["CDR_score"]
        context = f"Subjective: {s}\nAssessment: {a}\nPlan: {p}\nCDR: {cdr}"
        context_strings.append(context)

    full_context = "\n\n".join(context_strings)
    return full_context

def estimate_tokens(text):
    return len(text) 

def split_text(text, max_tokens=8000):
    chunks = []
    current_chunk = ""
    for char in text:
        if estimate_tokens(current_chunk + char) < max_tokens:
            current_chunk += char
        else:
            chunks.append(current_chunk)
            current_chunk = char
    if current_chunk:
        chunks.append(current_chunk)
    return chunks

def transcribe_content(df):
    full_context = retrieve_info(df)
    template = '''
    Examine the following content and determine if it contains any Chinese text:

    {text}

    If Chinese text is present, translate it into English. 
    Integrate the translated portions smoothly with any existing English text, ensuring the entire content reads as a polished, 
    formal, and coherent document in English only. The goal is to produce a final version in English that flows naturally, 
    with no traces of the original Chinese language, making it easy for English-speaking readers to understand.
    '''
    prompt_template = PromptTemplate(
        input_variables=["text"],
        template= template
    )

    translation_chain = LLMChain(
        llm=llm,
        prompt=prompt_template
    )
    
    text_chunks = split_text(full_context, max_tokens=8000)

    translated_chunks = []
    for i, chunk in enumerate(text_chunks):
        print(f"Processing chunk {i + 1}/{len(text_chunks)}...")
        try:
            translated_chunk = translation_chain.run({"text": chunk})
            translated_chunks.append(translated_chunk)
        except Exception as e:
            print(f"Error processing chunk {i + 1}: {e}")
            translated_chunks.append(f"Error in chunk {i + 1}: {e}")

    # Combine translated chunks into the final output
    translated_text = "\n".join(translated_chunks)

    # # Run the translation
    # translated_text = translation_chain.run({"text": full_context})

    return translated_text


def split_translated_text(text):    
    records = re.findall(
        r"Subjective:\s*(.*?)(?=\nAssessment:|\Z)\nAssessment:\s*(.*?)(?=\nPlan:|\Z)\nPlan:\s*(.*?)(?=\nCDR:|\Z)\nCDR:\s*([0-9.]+)",
        text,
        re.DOTALL
    )
    
    parsed_records = [
        {
            "Subjective": match[0].strip(),
            "Assessment": match[1].strip(),
            "Plan": match[2].strip(),
            "CDR": match[3].strip(),
        }
        for match in records
    ]
    
    return parsed_records

def save_to_csv(translated_text, filename="translated_content.csv"):
    
    records = split_translated_text(translated_text)
    
    df = pd.DataFrame(records)
    
    df.to_csv(filename, index=False)
    print(f"Translated text saved to {filename}")