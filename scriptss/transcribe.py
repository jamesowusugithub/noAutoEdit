import os
import json
import whisper

INPUT_FOLDER = os.path.join("data", "in")
LOG_FOLDER = os.path.join("data", "logs")

def transcribe_video(model, video_path):
    try:
        result = model.transcribe(video_path, language="en", fp16=False)
        return result
    except Exception as e:
        print("Audio failed for", video_path)
        print("Error", e)
        return None

def main():
    if not os.path.exists(LOG_FOLDER):
        os.makedirs(LOG_FOLDER)

    model = whisper.load_model("medium")

    for file_name in os.listdir(INPUT_FOLDER):
        if not file_name.lower().endswith((".mp4", ".mov", ".avi", ".mkv")):
            continue

        video_path = os.path.join(INPUT_FOLDER, file_name)
        print("Transcribing", video_path)

        transcript = transcribe_video(model, video_path)

        if transcript is None:
            print("Skipping, no transcript saved")
            continue

        out_name = os.path.splitext(file_name)[0] + ".json"
        out_path = os.path.join(LOG_FOLDER, out_name)

        with open(out_path, "w", encoding="utf8") as f:
            json.dump(transcript, f, indent=4)

        print("Saved transcript to", out_path)

    print("All videos transcribed")

if __name__ == "__main__":
    main()
