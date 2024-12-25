
# Alzheimer's Disease Prediction using Big Data Solutions and LLM
We investigate the application of Multi-Agent LLMs to preprocess natural language and detect Alzheimer’s Disease. We build classification models, 
which predict the discrete CDR(Clinical Dementia Rating) label from 4-column natural language data (SOAP). We use prompt engineering skills to
handle dirty and incomplete data. After cleaning the data, we also test the performance of different models in predicting the
Alzheimer’s Disease EHR.

Author: Kuo Gong      (kg3175)
        FeiYang Chen  (fc2795)

## Data Type
The Data is semi-structured Electronic Health Records of Alzheimer’s Disease (EHRs). The Data contains both text fields and a numerical Target Field, which mixes unstruc-
tured(Text) and structured (Numerical) Data. The columns (S), (A), and (P) are input data, and the CDR score is the label data which used as the output for prediction. The data consist
of one year of raw data collected by Taiwan Hospital. There are a total of 3702 records and 5 features.

Because it is private data from private Hospital. We need to follow the data privacy, and we upload test data for tesing our project.

## Project Structure 
In this project, we have four folders. 
* BioBERT              - This is training process for Bert/BioBert model, and performance measure
* Data_prepprocess  - This is Airflow DAG for process data, and Translation Agent
    * airflow_DAG.py (we implement the airflow to organize the workflow of preprocess the raw data, use pyspark to extract the important columns)
    * fetch_data.ipynb  (we use the fetch the data from the Google Cloud bucket, use pyspark to clean the label data in the input column, and upload the cleaned data back to the google bucket)
    * translate.ipynb  (implement of translate the Chinese to English)
    * translate.py     (The Translation Model agent class)
* front-end         - This is a Front-end Website Demo
    * index.html                     (Data Visulization Website)
    * server.py                      (Server BackEnd Source Code)
* LLM_predict       - This is a Agent build class, and mutli-agent
    * agent_library.py               (Define what the purpose of each agent)
    * agent_class.py                 (Define class of each agent)
    * transcribe.py                  (Basic Util Function for Project)
    * one_agent_prediction.ipynb     (One Agent Prediction)
    * multi_agent_prediction.ipynb   (Multi Agent Prediction)
    * Rest of file are csv test file. 
    
## Youtube Link

https://www.youtube.com/watch?v=wneqUt-Czjg