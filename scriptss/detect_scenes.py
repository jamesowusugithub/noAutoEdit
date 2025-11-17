import os
import json
from scenedetect import VideoManager, SceneManager
from scenedetect.detectors import ContentDetector

INPUT_FOLDER = os.path.join("data", "in")
LOG_FOLDER = os.path.join("data", "logs")

def detect_scenes_for_video(video_path):
    video_manager = VideoManager([video_path])
    scene_manager = SceneManager()
    scene_manager.add_detector(ContentDetector(threshold=20.0))

    video_manager.start()
    scene_manager.detect_scenes(frame_source=video_manager)

    scenes = scene_manager.get_scene_list()
    video_manager.release()

    out = []
    for i, (start, end) in enumerate(scenes):
        out.append({
            "scene": i,
            "start_seconds": start.get_seconds(),
            "end_seconds": end.get_seconds()
        })

    return out

def main():
    if not os.path.exists(LOG_FOLDER):
        os.makedirs(LOG_FOLDER)

    for file_name in os.listdir(INPUT_FOLDER):
        if not file_name.lower().endswith((".mp4", ".mov", ".mkv", ".avi")):
            continue

        print("Detecting scenes for", file_name)

        video_path = os.path.join(INPUT_FOLDER, file_name)
        scenes = detect_scenes_for_video(video_path)

        print("Found", len(scenes), "scenes")

        base = os.path.splitext(file_name)[0]
        out_path = os.path.join(LOG_FOLDER, base + "_scenes.json")

        with open(out_path, "w", encoding="utf8") as f:
            json.dump(scenes, f, indent=4)

        print("Saved scenes to", out_path)

if __name__ == "__main__":
    main()
