from flask import Flask, render_template, request, redirect, url_for, send_file, after_this_request
import yt_dlp as youtube_dl
import os
import tempfile
import shutil
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

@app.route('/')
def index():
    message = request.args.get('message')
    return render_template('download.html', message=message)

def progress_hook(d):
    if d['status'] == 'downloading':
        percent = d['_percent_str']
        socketio.emit('progress', {'percent': percent}, namespace='/download')
    elif d['status'] == 'finished':
        socketio.emit('progress', {'percent': '100%'}, namespace='/download')

@app.route('/download', methods=['POST'])
def download():
    url = request.form['url']
    download_type = request.form['type']
    
    tempdir = tempfile.mkdtemp()

    try:
        ydl_opts = {
            'outtmpl': os.path.join(tempdir, '%(title)s.%(ext)s'),
            'progress_hooks': [progress_hook],
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
            ydl.download([url])

        # Find the downloaded file in the temp directory
        for filename in os.listdir(tempdir):
            filepath = os.path.join(tempdir, filename)
            
            @after_this_request
            def remove_file(response):
                try:
                    # Delay the cleanup to ensure the file is no longer in use
                    import threading
                    def delayed_cleanup():
                        try:
                            shutil.rmtree(tempdir)
                        except Exception as e:
                            app.logger.error(f"Error removing or closing downloaded file handle: {e}")
                    threading.Timer(5, delayed_cleanup).start()
                except Exception as e:
                    app.logger.error(f"Error scheduling file cleanup: {e}")
                return response

            response = send_file(filepath, as_attachment=True, download_name=filename)
            response.headers["Access-Control-Expose-Headers"] = "Content-Disposition"
            response.headers['Refresh'] = '3; url=/?message=Download+Completed'  # Redirect back to the main page with a message after 3 seconds

            return response

    except Exception as e:
        shutil.rmtree(tempdir)  # Clean up the temp directory if an error occurs
        return redirect(url_for('index', message=f"Error: {str(e)}"))

if __name__ == '__main__':
    socketio.run(app, debug=True)
