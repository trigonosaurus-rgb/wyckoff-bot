from youtube_transcript_api import YouTubeTranscriptApi

video_id = "NfZhOuRGTto"
try:
    # Try fetching Russian transcript
    transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
    
    # Try getting manually created ones, fallback to generated
    try:
        transcript = transcript_list.find_transcript(['ru', 'en'])
    except:
        # get any available and translate to ru
        transcript = transcript_list.find_transcript(['en']).translate('ru')
        
    text_data = transcript.fetch()
    text = " ".join([t['text'] for t in text_data])
    
    with open("transcript.txt", "w", encoding="utf-8") as f:
        f.write(text)
    print("Transcript saved successfully.")
except Exception as e:
    print("Error:", e)
    
    # Let's just try basic fetch
    try:
        data = YouTubeTranscriptApi.get_transcript(video_id, languages=['ru', 'en'])
        text = " ".join([t['text'] for t in data])
        with open("transcript.txt", "w", encoding="utf-8") as f:
            f.write(text)
        print("Transcript saved using basic fetch.")
    except Exception as e2:
        print("Basic fetch error:", e2)
