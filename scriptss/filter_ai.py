# Placeholder scoring module

def score_transcript_segment(text):
    # very simple scoring logic
    keywords = ["important", "clip this", "watch this", "look", "note"]
    score = 0

    for k in keywords:
        if k in text.lower():
            score += 1

    return score

def score_visual_frame(frame):
    # visual scoring placeholder
    return 0.0

def combine_scores(text_score, visual_score):
    return text_score + visual_score
