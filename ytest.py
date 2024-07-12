import yt_dlp as youtube_dl
import os

def download_video(url):
    os.makedirs('downloads', exist_ok=True)
    ydl_opts = {
        'outtmpl': 'downloads/%(title)s.%(ext)s',
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        try:
            ydl.download([url])
            print("Download completed!")
        except Exception as e:
            print(f"Error: {str(e)}")

if __name__ == "__main__":
    url = input("Enter the YouTube video URL: ")
    download_video(url)
