import streamlit as st
import yt_dlp as youtube_dl
import os
import tempfile
import shutil

st.set_page_config(page_title="YouTube Video Downloader", page_icon="📹", layout="centered")
st.title("YouTube Video Downloader")

# Define a function to download video
def download_video(url, download_type):
    tempdir = tempfile.mkdtemp()
    try:
        ydl_opts = {
            'outtmpl': os.path.join(tempdir, '%(title)s.%(ext)s'),
            'ffmpeg_location': 'C:/ffmpeg/bin',  # Ensure this path points to the location of ffmpeg and ffprobe
        }

        if download_type == 'video':
            ydl_opts['format'] = 'bestvideo+bestaudio'
        elif download_type == 'audio':
            ydl_opts['format'] = 'bestaudio'
            ydl_opts['postprocessors'] = [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }]
        
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            return filename, tempdir
    except Exception as e:
        shutil.rmtree(tempdir)
        st.error(f"Error: {str(e)}")
        return None, None

# User input
url = st.text_input("YouTube Video URL", placeholder="Enter YouTube URL")
download_type = st.selectbox("Download as", ["Select format", "Video (MP4)", "Audio (MP3)"])

# Download button
if st.button("Download"):
    if url and download_type != "Select format":
        filename, tempdir = download_video(url, download_type.lower())
        if filename:
            with open(filename, "rb") as file:
                btn = st.download_button(
                    label="Download file",
                    data=file,
                    file_name=os.path.basename(filename),
                    mime='application/octet-stream'
                )
            st.success("Download Completed")
            shutil.rmtree(tempdir)
        else:
            st.error("Failed to download the video.")
    else:
        st.warning("Please provide a valid URL and select a download format.")
