import yt_dlp
import os
import threading
from queue import Queue
import tempfile
import uuid

class DownloadProgress:
    def __init__(self):
        self.progress = 0
        self.status = "Initializing..."
        self.error = None
        self.completed = False
        self.file_path = None

class YouTubeDownloader:
    def __init__(self):
        self.download_queue = Queue()
        self.download_progress = {}
        self.worker_threads = []
        self.temp_dir = tempfile.gettempdir()

    def get_progress(self, download_id):
        if download_id in self.download_progress:
            dp = self.download_progress[download_id]
            return {
                'progress': dp.progress,
                'status': dp.status,
                'error': dp.error,
                'completed': dp.completed,
                'file_path': dp.file_path
            }
        return {
            'progress': 0,
            'status': 'Download not found',
            'error': 'Invalid download ID',
            'completed': False,
            'file_path': None
        }

    def get_download_path(self, download_id):
        if download_id in self.download_progress:
            return self.download_progress[download_id].file_path
        return None

    def progress_hook(self, download_id):
        def hook(d):
            if d['status'] == 'finished':
                self.download_progress[download_id].status = 'Processing...'
                self.download_progress[download_id].progress = 100
                # Store the final merged filepath
                if 'filepath' in d:  # sometimes yt-dlp uses 'filepath' instead of 'filename'
                    self.download_progress[download_id].file_path = d['filepath']
                elif 'filename' in d:
                    self.download_progress[download_id].file_path = d['filename']
            elif d['status'] == 'downloading':
                try:
                    percent = float(d['_percent_str'].replace('%', ''))
                    self.download_progress[download_id].progress = percent
                    self.download_progress[download_id].status = f'Downloading: {d["_percent_str"]}'
                except:
                    pass
        return hook

    def download_worker(self):
        while True:
            try:
                download_data = self.download_queue.get()
                if download_data is None:
                    break

                url, resolution, format_option, download_id = download_data
                threading.current_thread().name = download_id

                # Create a unique filename using UUID
                unique_filename = str(uuid.uuid4())
                output_path = os.path.join(self.temp_dir, unique_filename)
                
                # Configure yt-dlp options
                ydl_opts = {
                    'outtmpl': f'{output_path}.%(ext)s',
                    'progress_hooks': [self.progress_hook(download_id)],
                    'merge_output_format': 'mp4' if format_option == 'mp4' else 'webm',  # Force output format
                }

                # Handle different format options
                if format_option == 'audio':
                    ydl_opts.update({
                        'format': 'bestaudio/best',
                        'postprocessors': [{
                            'key': 'FFmpegExtractAudio',
                            'preferredcodec': 'mp3',
                            'preferredquality': '192',
                        }],
                    })
                else:
                    if resolution == 'highest':
                        ydl_opts['format'] = 'bestvideo+bestaudio/best'
                    else:
                        height = resolution[:-1]  # Remove 'p' from '720p'
                        ydl_opts['format'] = f'bestvideo[height<={height}]+bestaudio/best'

                self.download_progress[download_id].status = "Starting download..."
                
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    # Get video info first
                    info = ydl.extract_info(url, download=False)
                    title = info.get('title', unique_filename)
                    ext = 'mp3' if format_option == 'audio' else ydl_opts['merge_output_format']
                    
                    # Download the video
                    ydl.download([url])
                    
                    # Find the downloaded file
                    expected_path = f'{output_path}.{ext}'
                    if os.path.exists(expected_path):
                        self.download_progress[download_id].file_path = expected_path
                        self.download_progress[download_id].status = "Download complete!"
                        self.download_progress[download_id].completed = True
                    else:
                        # Fallback: try to find any file with the UUID
                        for file in os.listdir(self.temp_dir):
                            if file.startswith(unique_filename):
                                full_path = os.path.join(self.temp_dir, file)
                                self.download_progress[download_id].file_path = full_path
                                self.download_progress[download_id].status = "Download complete!"
                                self.download_progress[download_id].completed = True
                                break
                        else:
                            raise Exception("Could not locate downloaded file")

            except Exception as e:
                if download_id in self.download_progress:
                    self.download_progress[download_id].error = str(e)
                    self.download_progress[download_id].status = f"Error: {str(e)}"
            finally:
                self.download_queue.task_done()

    def init_workers(self, num_workers=3):
        for _ in range(num_workers):
            t = threading.Thread(target=self.download_worker, daemon=True)
            t.start()
            self.worker_threads.append(t)

    def add_to_queue(self, url, resolution, format_option, download_id):
        self.download_progress[download_id] = DownloadProgress()
        self.download_queue.put((url, resolution, format_option, download_id))
        return download_id