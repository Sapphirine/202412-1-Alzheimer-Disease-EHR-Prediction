

from flask import Flask, request, jsonify, send_file
import pandas as pd
import numpy as np
from sklearn.metrics import confusion_matrix
import seaborn as sns
import matplotlib.pyplot as plt
import io
import base64
from flask_cors import CORS
from wordcloud import WordCloud

from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.chat_models import ChatOpenAI
from agent_library import library
# from tools import PubMedTool
import os

import re
import time

app = Flask(__name__)
CORS(app)  # Accept the request

os.environ["OPENAI_API_KEY"] = "place_holder_for_api_key"


llm = ChatOpenAI(model_name='gpt-4')

class DoctorAgent:
    def __init__(self, profile):
        #self.llm = ChatOpenAI(model_name='gpt-4')
        self.profile = profile  # Store the profile
        
        self.prompt_template = PromptTemplate(
            input_variables=['subjective', 'assessment', 'plan'], 
            template = f"""
            {profile}
            
            Subjective: {{subjective}}
            Assessment: {{assessment}}
            Plan: {{plan}}
            
            Predict if the patient is diagnosed with Alzheimer's disease. 
            This is a categorization problem, predict the label data in 4 number of CDR level.
            If the patient is diagnosed, determine the Clinical Dementia Rating (CDR) level. 
            The CDR level can only be one of the following values: 0.5, 1.0, 2.0, 3.0.
    
            Your response must include a CDR level in the exact format: "CDR level is X", where X is one of the allowed values. 
            If no diagnosis can be made, explicitly state that no conclusion is possible, but you must give a CDR level,"CDR level is X" closest to the given information.

            Reply with your prediction and the CDR level. Conclude your response with the word 'TERMINATE'.
            """
        )
        self.chain = LLMChain(llm = llm, prompt = self.prompt_template)
        self.last_response = ""
        
    def predict(self, subjective, assessment, plan):
        response = self.chain.run({
            'subjective': subjective, 
            'assessment': assessment, 
            'plan': plan
        })
        self.last_response = response.strip()
        return self.last_response
    
    def revise(self, feedback, subjective, assessment, plan):
        revised_prompt_template = PromptTemplate(
            input_variables=['profile', 'last_response', 'feedback', 'subjective', 'assessment', 'plan'],
            template="""
            {profile}
            
            You previously provided the following response:
            {last_response}
            
            The Critical Evaluator provided the following feedback:
            {feedback}
            
            Based on this feedback, revise your original response if necessary.
            Provide your updated prediction and CDR level. Please use 'CDR level is X' Format. When done, reply 'TERMINATE'.
            """
        )
        revised_chain = LLMChain(llm= llm, prompt=revised_prompt_template)
        revised_response = revised_chain.run({
            'profile': self.profile,
            'last_response': self.last_response,
            'feedback': feedback,
            'subjective': subjective,
            'assessment': assessment,
            'plan': plan
        })
        self.last_response = revised_response.strip()
        return self.last_response
    
def remove_cdr_score(text):
    # Define a regex pattern to match 'cdr X' where X can be a float (e.g., 3.0)
    pattern = r'cdr[:= ]?\d+(\.\d+)?'
    # Remove matches from the text
    cleaned_text = re.sub(pattern, '', text, flags=re.IGNORECASE)
    return cleaned_text.strip()  # Remove leading/trailing whitespace

def extract_predicted_cdr(prediction_text):
    pattern = r'CDR.*?(\d+(\.\d+)?)'
    match = re.search(pattern, prediction_text, re.IGNORECASE)
    if match:
        return float(match.group(1))
    else:
        return None
    

doctor_agent = DoctorAgent(profile = library['Doctor']['profile'])

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"success": False, "message": "No file part"})

    file = request.files['file']
    if file.filename == '':
        return jsonify({"success": False, "message": "No selected file"})

    # try:
<<<<<<< HEAD
        # Reading CSV File
    df = pd.read_csv(file).head(2)
=======
        # 读取 CSV 文件
    df = pd.read_csv(file).head(20)
>>>>>>> d5d4c24cc6fa225fb39150ee1a0161238862e29a
    df = df.drop_duplicates(subset=["主訴(S)", "診斷(A)", "計畫(P)"])
    true_label = df['CDR_score'].to_list()
    unique_values = df['CDR_score'].unique()
    print(f"Unique CDR_score values: {unique_values}")
    df['診斷(A)'] = df['診斷(A)'].apply(remove_cdr_score)
    results = []
    for _, row in df.iterrows():
        subjective = row['主訴(S)']
        assessment = row['診斷(A)']
        plan = row['計畫(P)']
        time.sleep(1)
        prediction = doctor_agent.predict(subjective, assessment, plan)
        print("A prediction is back !")

        results.append({
                "Subjective": subjective,
                "Assessment": assessment,
                "Plan": plan,
                "Prediction": prediction
            })
        # print(results)
    print(results)
    predicted_cdrs = []
    for result in results:
        prediction_text = result['Prediction']
        
        # Extract predicted and actual CDR levels
        predicted_cdr = extract_predicted_cdr(prediction_text)
        predicted_cdrs.append(predicted_cdr)

        # print(predicted_cdr)

    # 渲染结果df
    df["predicted_cdr"] = predicted_cdrs   

    # fig, ax = plt.subplots(figsize=(5, 2))
    # ax.axis('tight')
    # ax.axis('off')
    # table = ax.table(cellText=df.values, colLabels=df.columns, loc='center', cellLoc='center')

    # buf_table = io.BytesIO()
    # plt.savefig(buf_table, format='png', bbox_inches='tight')
    # buf_table.seek(0)
    # base64_cdrTable = base64.b64encode(buf_table.read()).decode('utf-8')
    # buf_table.close()

    
    # 绘制饼图
    column_name = "predicted_cdr"
    value_counts = df[column_name].value_counts()
    plt.figure(figsize=(6, 6))
    plt.pie(value_counts, labels=value_counts.index, autopct='%1.1f%%', startangle=140,radius=0.8)
    
    # 保存饼图为图片
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    buf.seek(0)
    base64_pieChart = base64.b64encode(buf.read()).decode('utf-8')
    buf.close()

    label_map = {0: 0, 0.5: 1, 1: 2, 2: 3, 3: 4}
    predicted_label = [label_map[label] for label in predicted_cdrs]
    true_label = [label_map[label] for label in true_label]
    print(predicted_label)
    print(true_label)

    text_data = " ".join(df['診斷(A)'].astype(str))

    # Data Visulization Which generate the WordCloud
    wordcloud = WordCloud(width=800, height=400, background_color='white').generate(text_data)

    # Convert the graph to base64
    buf_wc = io.BytesIO()
    wordcloud.to_image().save(buf_wc, format='png')
    buf_wc.seek(0)
    base64_wordcloud = base64.b64encode(buf_wc.getvalue()).decode('utf-8')
    buf_wc.close()

<<<<<<< HEAD

    # Caluculate the confusion matrix
=======
    # 计算混淆矩阵
>>>>>>> d5d4c24cc6fa225fb39150ee1a0161238862e29a
    labels = sorted(set(label_map.values()))
    cm = confusion_matrix(true_label, predicted_label, labels=labels)

    # Draw the confusion matrix
    plt.figure(figsize=(8, 6))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=labels, yticklabels=labels)
    plt.xlabel('Predicted')
    plt.ylabel('True')
    plt.title('Confusion Matrix')

    # Save the figure base64
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    base64_confusion = base64.b64encode(buf.getvalue()).decode('utf-8')
    buf.close()

    df = df.rename(columns={"病歷編號":"ID","主訴(S)":"Subjective","診斷(A)":"Assessment","計畫(P)":"Plan","CDR_score":"CDR","predicted_cdr":"Predicted CDR"})
    print(df.columns)
    return jsonify({"success": True, "confusion_matrix": base64_confusion, "keyword_chart": base64_wordcloud,"cdrTable":df.to_dict(orient='records'),"pieChart":base64_pieChart})

    # except Exception as e:
    #     return jsonify({"success": False, "message": str(e)})

if __name__ == '__main__':
    app.run(debug=True)
