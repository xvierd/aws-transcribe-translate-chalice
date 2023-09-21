import uuid

import boto3
from chalice import Chalice

app = Chalice(app_name='transcribe-translate')

client_s3 = boto3.client('s3')
transcribe_client = boto3.client('transcribe')

s3_bucket = 'ml-transcribe'

s3_bucket_output = 'ml-transalate'


@app.on_s3_event(bucket=s3_bucket, events=['s3:ObjectCreated:*'])
def handler(event):
    print("Object uploaded for bucket: %s, key: %s"
          % (event.bucket, event.key))

    if not event.key.endswith(".mp4"):
        return

    # Get the key object from the event create a file object with srt extension
    key = event.key
    output_file_name = key.split('.')[0] + '.srt'
    transcribe_job_name = key.split('.')[0] + str(uuid.uuid4())
    video_full_path = "s3://" + s3_bucket + "/" + key

    response = transcribe_client.start_transcription_job(
        TranscriptionJobName=transcribe_job_name,
        LanguageCode='en-US',
        MediaFormat='mp4',
        Media={
            'MediaFileUri': video_full_path
        },
        OutputBucketName=s3_bucket_output,
        OutputKey=key.replace(".mp4", ""),
        Subtitles={
            'Formats': [
                'srt'
            ]}
    )

    transcribe_job = response['TranscriptionJob']['TranscriptionJobName']

    print("TranscriptionJobName : {}".format(transcribe_job))
