import os
import json
from moviepy.editor import VideoFileClip, concatenate_videoclips

from filter_ai import score_transcript_segment

INPUT_FOLDER = os.path.join("data", "in")
LOG_FOLDER = os.path.join("data", "logs")
OUTPUT_FOLDER = os.path.join("data", "out")

CONFIG = {
    "trigger_phrases": [
        "clip this",
        "watch this",
        "look at this",
        "this part is important"
    ],
    "min_clip_length": 1.0,
    "max_clip_length": 12.0
}

def load_transcript(name):
    path = os.path.join(LOG_FOLDER, name + ".json")
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf8") as f:
        return json.load(f)

def load_scenes(name):
    path = os.path.join(LOG_FOLDER, name + "_scenes.json")
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf8") as f:
        return json.load(f)

def find_trigger_intervals(transcript, triggers):
    if transcript is None or "segments" not in transcript:
        return []

    intervals = []

    for seg in transcript["segments"]:
        text = seg["text"]
        start = seg["start"]
        end = seg["end"]

        for t in triggers:
            if t.lower() in text.lower():
                print("Trigger found", t, "at", start)
                intervals.append((start, end))

    return intervals

def convert_scene_intervals(scene_data):
    intervals = []
    for s in scene_data:
        intervals.append((s["start_seconds"], s["end_seconds"]))
    return intervals

def merge_intervals(a, b):
    merged = []
    all_ints = a + b
    all_ints = sorted(all_ints, key=lambda x: x[0])

    for start, end in all_ints:
        if not merged:
            merged.append([start, end])
            continue

        prev_start, prev_end = merged[-1]

        if start <= prev_end:
            merged[-1][1] = max(prev_end, end)
        else:
            merged.append([start, end])

    return [(i[0], i[1]) for i in merged]

def process_video(file_name):
    base = os.path.splitext(file_name)[0]

    transcript = load_transcript(base)
    if transcript is None:
        print("No transcript found for", base)
        return []

    scenes = load_scenes(base)

    trigger_intervals = find_trigger_intervals(transcript, CONFIG["trigger_phrases"])
    scene_intervals = convert_scene_intervals(scenes)

    print("Trigger intervals", trigger_intervals)
    print("Scene intervals", scene_intervals)

    merged = merge_intervals(trigger_intervals, scene_intervals)

    print("Merged intervals", merged)

    return merged

def export_clips(video_path, intervals, base_name):
    clip = VideoFileClip(video_path)
    clips = []

    for start, end in intervals:
        if end - start < 0.5:
            continue
        try:
            sub = clip.subclip(start, end)
            clips.append(sub)
        except Exception:
            pass

    if not clips:
        print("No clips to export")
        clip.close()
        return

    final = concatenate_videoclips(clips, method="compose")
    out_path = os.path.join(OUTPUT_FOLDER, base_name + "_cut.mp4")

    final.write_videofile(out_path, codec="libx264", audio_codec="aac", fps=clip.fps, threads=4)

    clip.close()
    print("Saved", out_path)

def main():
    if not os.path.exists(OUTPUT_FOLDER):
        os.makedirs(OUTPUT_FOLDER)

    for file_name in os.listdir(INPUT_FOLDER):
        if not file_name.lower().endswith((".mp4", ".mov", ".mkv", ".avi")):
            continue

        print("Processing", file_name)

        intervals = process_video(file_name)

        if not intervals:
            print("No intervals found")
            continue

        video_path = os.path.join(INPUT_FOLDER, file_name)
        base = os.path.splitext(file_name)[0]

        export_clips(video_path, intervals, base)

if __name__ == "__main__":
    main()
