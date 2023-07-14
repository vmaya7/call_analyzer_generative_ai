import time
import urllib.request
from datetime import datetime
import json
import boto3
import pandas as pd

dt = datetime.now()
ts = datetime.timestamp(dt)

client = boto3.client('transcribe')
s3 = boto3.resource('s3')
s3_client = boto3.client('s3')

def lambda_handler(event, context):
    """Lambda handler or main"""
    # print("Received event: " + json.dumps(event, indent=2))

    bucket = event['Records'][0]['s3']['bucket']['name']
    key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')
    job_name = f"TranscribeAudio-{key}-{ts}"
    try:
        response = s3_client.get_object(Bucket=bucket, Key=key)
        print(f"📨 File received: {key}, CONTENT TYPE: {response['ContentType']}")


        response = client.start_transcription_job(
            TranscriptionJobName= job_name,
            LanguageCode= "es-US",
            Settings={
                'ShowSpeakerLabels': True,
                'MaxSpeakerLabels': 2,
            },
            MediaFormat= key[-3:],
            Media= {
                "MediaFileUri": f"s3://{bucket}/{key}"
            }
        )
        max_tries = 60
        while max_tries > 0:
            max_tries -= 1
            job = client.get_transcription_job(TranscriptionJobName=job_name)
            job_status = job['TranscriptionJob']['TranscriptionJobStatus']
            if job_status in ['COMPLETED', 'FAILED']:
                print(f"Job {job_name} is {job_status}.")
                if job_status == 'COMPLETED':
                    print(
                        f"Download the transcript from\n"
                        f"\t{job['TranscriptionJob']['Transcript']['TranscriptFileUri']}.")
                break
            else:
                print(f"⏳ Waiting for {job_name}. Current status is {job_status}.")
            time.sleep(10)

        print(f"⌛ Transcription complete.")

        with urllib.request.urlopen(job['TranscriptionJob']['Transcript']['TranscriptFileUri']) as url:
            s = url.read()
            data = json.loads(s)
            df = pd.DataFrame(data['results']['items'])
            df['confidence'] = df.alternatives.map(lambda x: x[0]['confidence'])
            df['content'] = df.alternatives.map(lambda x: x[0]['content'])
            scam_text = ' '.join(df.content)
            s3object = s3.Object('wizeline-generative-hackaton-transcribed', f"{job_name}.json")
            result = s3object.put(
                Body=(bytes(json.dumps(data).encode('UTF-8')))
            )
            print ("✅ JSON uploaded to wizeline-generative-hackaton-transcribed")

    except Exception as e:
        printf(f"🔥 Error: {e}")
        raise e

if __name__ == "__main__":
    lambda_handler(None, None)
