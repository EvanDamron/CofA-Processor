import boto3
import psycopg2

bucket_name = 'cofa-pdf-storage'
local_file_path = 'viscoplex_cofa.pdf'
s3_key = f'uploads/{local_file_path}'
region = 'us-east-1'

s3 = boto3.client('s3')

try:
    s3.upload_file(local_file_path,
    bucket_name,
    s3_key,
    ExtraArgs={'ACL': 'public-read'}) # Extra Args makes the ocject publicly accessible
    print(f"Uploaded {local_file_path} to s3")
except Exception as e:
    print(f"Upload failed: {e}")