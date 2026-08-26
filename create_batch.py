from google import genai
from google.genai import types
from dotenv import load_dotenv
import csv
import json

INPUT_CSV = "input/Rerecords/new.csv"
OUTPUT_DIR = "output/Southern Rerecords"

BATCH_NAME = "Southern_new"

# only need to change the 3 above here for each batch

type = 'south'
# type = 'ga'

if type == 'south':
    VOICE = "Enceladus"
    PROMPT = "Say the following word clearly in a southern american accent: "
elif type == 'ga':
    VOICE = "Zephyr"
    PROMPT = "Say the following word clearly in a general american accent: "
else:
   raise ValueError(f'type is {type}, should be south or ga')

# change the one above here to modify the condition

REQUESTS_FILE = f"batch_data/{BATCH_NAME}_requests.jsonl"
JOB_INFO_FILE = f"batch_data/{BATCH_NAME}_job_info.json"

MODEL = "gemini-3.1-flash-tts-preview"


load_dotenv() # This script requires an environment variable called GEMINI_API_KEY that has your gemini api key

client = genai.Client()

# Read the word list
with open(INPUT_CSV, newline="") as f:
    words = [row[0].title() for row in csv.reader(f)]

# Build one JSON per word and output it to our JSONL file
key_to_word = {}
with open(REQUESTS_FILE, "w") as f:
    for i, word in enumerate(words):
        key = f"word-{i}" #using this instead of the word itself to be extra safe of duplicates
        key_to_word[key] = word
        request = {
            "key": key,
            "request": {
                "contents": [{
                    "parts": [{
                        "text": (PROMPT + f"{word}.")
                    }]
                }],
                "generation_config": {
                    "response_modalities": ["AUDIO"],
                    "speech_config": {
                        "voice_config": {
                            "prebuilt_voice_config": {"voice_name": VOICE}
                        }
                    }
                }
            }
        }
        f.write(json.dumps(request) + "\n")

print(f"Wrote {len(words)} requests to {REQUESTS_FILE}")

# Upload the JSONL file, then create the batch job from it
uploaded_file = client.files.upload(
    file=REQUESTS_FILE,
    config=types.UploadFileConfig(display_name=f"tts-batch-requests-{BATCH_NAME}", mime_type="jsonl"),
)

batch_job = client.batches.create(
    model=MODEL,
    src=uploaded_file.name, # type: ignore
    config={"display_name": BATCH_NAME},
)

# Save everything for the next script
with open(JOB_INFO_FILE, "w") as f:
    json.dump({
        "job_name": batch_job.name,
        "output_dir": OUTPUT_DIR,
        "key_to_word": key_to_word,
        "batch_name_used": BATCH_NAME,
    }, f, indent=2)

print(f"Saved job info to {JOB_INFO_FILE}.")