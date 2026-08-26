from google import genai
from dotenv import load_dotenv
import wave
import base64
import json
import os

load_dotenv() # Requires the GEMINI_API_KEY environment variable

# BATCH_NAME = "test_batch"
# BATCH_NAME = "one_syllable_pseudo_candidates"
# BATCH_NAME = "two_syllable_pseudo_candidates"
# BATCH_NAME = "GA_one_syllable_real"
# BATCH_NAME = "GA_two_syllable_real"
# BATCH_NAME = "Southern_two_syllable_real"
# BATCH_NAME = "Southern_one_syllable_pseudo"
# BATCH_NAME = "Southern_two_syllable_pseudo"
# BATCH_NAME = "Southern_one_syllable_real"
# BATCH_NAME = "GA_rerecords"
# BATCH_NAME = "Southern_rerecords"
# BATCH_NAME = "GA_re2"
# BATCH_NAME = "southern_2"
# BATCH_NAME = "southern_3"
BATCH_NAME = "Southern_new"
# BATCH_NAME = "GA_new"



JOB_INFO_FILE = f"batch_data/{BATCH_NAME}_job_info.json"


def wave_file(filename, pcm, channels=1, rate=24000, sample_width=2):
    with wave.open(filename, "wb") as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(sample_width)
        wf.setframerate(rate)
        wf.writeframes(pcm)


client = genai.Client()

with open(JOB_INFO_FILE) as f:
    job_info = json.load(f)

job_name = job_info["job_name"]
output_dir = job_info["output_dir"]
key_to_word = job_info["key_to_word"]

batch_job = client.batches.get(name=job_name)
state = batch_job.state.name # type: ignore
print(f"Job state: {state}")

if state == "JOB_STATE_SUCCEEDED":
    os.makedirs(output_dir, exist_ok=True)


    result_file_name = batch_job.dest.file_name # type: ignore
    file_content = client.files.download(file=result_file_name).decode("utf-8") # type: ignore

    good = 0
    failed = []
    for line in file_content.splitlines():
        
        if not line:
            continue # this deals with a trailing "" line without throwing an error
        
        entry = json.loads(line)
        key = entry.get("key")
        word = key_to_word.get(key, key)

        if entry.get("response"):
            parts = entry["response"]["candidates"][0]["content"]["parts"] #this is just parsing the tree of the REST response
            audio_part = next((p for p in parts if "inlineData" in p), None) #find the part of the response that has audio (strictly speaking just non-text bytes)
            if audio_part:
                data_field = audio_part.get("inlineData")
                pcm = base64.b64decode(data_field["data"])
                filepath = os.path.join(output_dir, f"{word}.wav")
                wave_file(filepath, pcm)
                good = good + 1
            else:
                failed.append((word, "no audio in response"))
        elif entry.get("error"):
            failed.append((word, entry["error"]))

    print(f"Wrote {good} WAV files to {output_dir}")
    if failed:
        print(f"{len(failed)} words failed:")
        for word, err in failed:
            print(f"  {word}: {err}")

elif state == "JOB_STATE_FAILED":
    print(f"Job failed with this error: {batch_job.error}")