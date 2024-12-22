from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator

default_args = {
    'owner': 'your_username',
    'depends_on_past': False,
    'email': ['your_email@example.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'cdr_preprocessing_pipeline',
    default_args=default_args,
    description='DAG for preprocessing CDR data',
    schedule_interval=None,
    start_date=datetime(2023, 10, 18),
    catchup=False,
)

# Tasks

def read_data_from_local_csv(**kwargs):
    import pandas as pd
    df = pd.read_csv('1yr_data.csv')
    df.to_csv('airflow/data/raw_cdr_data.csv', index=False)

def preprocess(**kwargs):
    from pyspark.sql import SparkSession
    from pyspark.sql.functions import regexp_replace, col

    # Initialize Spark session
    spark = SparkSession.builder \
        .appName("CDR Preprocessing") \
        .getOrCreate()

    # Load the raw data
    input_path = '/tmp/raw_cdr_data.csv'
    df = spark.read.csv(input_path, header=True, inferSchema=True)

    # Select only the required columns
    columns_to_keep = ["主訴(S)", "診斷(A)", "計畫(P)", "CDR_score"]
    df = df.select(*columns_to_keep)

    # Drop duplicates based on specific columns
    df = df.dropDuplicates(["主訴(S)", "診斷(A)", "計畫(P)", "CDR_score"])

    # Clean the "診斷(A)" column using regex
    pattern = r'cdr[:= ]?\d+(\.\d+)?'  # Regex pattern to remove CDR score
    df = df.withColumn("診斷(A)", regexp_replace(col("診斷(A)"), pattern, "").alias("診斷(A)"))

    # Save the preprocessed data to a new CSV file
    output_path = '/tmp/preprocessed_cdr_data.csv'
    df.write.csv(output_path, header=True, mode="overwrite")

    # Stop Spark session
    spark.stop()

def save_the_csv(**kwargs):
    import shutil
    import os
    import glob

    # Rename and save cleaned data locally
    temp_file = '/tmp/preprocessed_cdr_data.csv'
    final_output_file = '/tmp/cleaned_data.csv'
    shutil.move(temp_file, final_output_file)

    # Upload to Google Cloud Storage (GCS)
    bucket_name = '6893_final_project_1'
    destination_blob_name = f'gs://{bucket_name}/cleaned_data.csv'
    os.system(f"gsutil cp {final_output_file} {destination_blob_name}")
    print(f"File uploaded to {destination_blob_name}")

# Define the tasks
read_csv = PythonOperator(
    task_id='read_data_from_local_csv',
    python_callable=read_data_from_local_csv,
    dag=dag,
)

preprocess_data = PythonOperator(
    task_id='preprocess',
    python_callable=preprocess,
    dag=dag,
)

save_csv = PythonOperator(
    task_id='save_the_csv',
    python_callable=save_the_csv,
    dag=dag,
)

# Define task dependencies
read_csv >> preprocess_data >> save_csv