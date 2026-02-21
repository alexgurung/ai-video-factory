import requests
import google.generativeai as genai
import edge_tts
import asyncio
import os
import whisper

os.environ["IMAGEMAGICK_BINARY"] = r"C:\Program Files\ImageMagick-7.1.2-Q16-HDRI\magick.exe"

from moviepy.editor import VideoFileClip, AudioFileClip, TextClip, CompositeVideoClip

# --- HARDCODE IMAGEMAGICK PATH ---

# --- 1. Configuration ---
GEMINI_API_KEY = "AIzaSyDXMqPxvYQ6wHSRgkmfJfXmdzDMjgG9XkM"
PEXELS_API_KEY = "vHV5YzHDftuVyZaS81A6PcCB0L6ej79DxNbrOtdVCF89V8KnR7isM1Rw"
BACKGROUND_VIDEO_FILE = "background.mp4"

def get_top_news():
    print("1. Fetching news from HackerNews...")
    top_stories_url = "https://hacker-news.firebaseio.com/v0/topstories.json"
    top_story_id = requests.get(top_stories_url).json()[0]
    story_url = f"https://hacker-news.firebaseio.com/v0/item/{top_story_id}.json"
    story_data = requests.get(story_url).json()
    return story_data['title']

def write_script(news_title):
    print("2. Writing script with Gemini AI...")
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-2.5-flash')
    prompt = f"Write a fast-paced, 30-second TikTok script about: '{news_title}'. No stage directions, just text."
    return model.generate_content(prompt).text.strip()

def download_background(query):
    print(f"3. Searching Pexels for: '{query}'...")
    headers = {"Authorization": PEXELS_API_KEY}
    url = f"https://api.pexels.com/videos/search?query={query}&orientation=portrait&per_page=1"
    r = requests.get(url, headers=headers).json()
    
    if r.get('videos'):
        video_url = r['videos'][0]['video_files'][0]['link']
        with open(BACKGROUND_VIDEO_FILE, 'wb') as f:
            f.write(requests.get(video_url).content)
        return True
    return False

async def generate_audio(script_text):
    print("4. Generating AI Voiceover...")
    communicate = edge_tts.Communicate(script_text, "en-US-ChristopherNeural")
    await communicate.save("voiceover.mp3")

def create_video_with_captions(audio_path, background_path):
    print("5. Transcribing & Rendering Video...")
    model = whisper.load_model("base")
    result = model.transcribe(audio_path, word_timestamps=True)
    
    audio = AudioFileClip(audio_path)
    video = VideoFileClip(background_path).subclip(0, audio.duration)
    clips = [video.set_audio(audio)]
    
    for segment in result['segments']:
        for wd in segment['words']:
            txt = (TextClip(wd['word'].strip().upper(), fontsize=100, color='yellow', 
                            font='Arial-Bold', stroke_color='black', stroke_width=2)
                   .set_start(wd['start']).set_duration(wd['end'] - wd['start']).set_position('center'))
            clips.append(txt)

    CompositeVideoClip(clips).write_videofile("final_video.mp4", fps=24, codec="libx264")

async def main():
    title = get_top_news()
    script = write_script(title)
    await generate_audio(script)
    
    # Try to download news-relevant video, fallback to default if search fails
    if not download_background(title):
        print("Using default background...")

    create_video_with_captions("voiceover.mp3", BACKGROUND_VIDEO_FILE)
    
    # Cleanup
    if os.path.exists("voiceover.mp3"): os.remove("voiceover.mp3")

if __name__ == "__main__":
    asyncio.run(main())