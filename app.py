from flask import Flask, render_template, request, jsonify, send_file
from downloader import YouTubeDownloader
import time
import os

app = Flask(__name__)
downloader = YouTubeDownloader()

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'GET':
        return render_template('index.html')
    
    if request.method == 'POST':
        url = request.form.get('url')
        resolution = request.form.get('resolution', 'highest')
        format_option = request.form.get('format', 'mp4')
        
        if not url:
            return jsonify({'error': 'Please enter a URL'})

        try:
            download_id = f'download_{time.time()}'
            downloader.add_to_queue(url, resolution, format_option, download_id)
            
            return jsonify({
                'message': 'Video added to download queue',
                'download_id': download_id
            })
        except Exception as e:
            return jsonify({'error': str(e)})

@app.route('/progress/<download_id>')
def get_progress(download_id):
    try:
        progress_info = downloader.get_progress(download_id)
        return jsonify(progress_info)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/download/<download_id>')
def download_file(download_id):
    try:
        file_path = downloader.get_download_path(download_id)
        if not file_path:
            return jsonify({'error': 'Download ID not found'}), 404
        
        if not os.path.exists(file_path):
            return jsonify({'error': f'File not found at path: {file_path}'}), 404
        
        filename = os.path.basename(file_path)
        
        try:
            return send_file(
                file_path,
                as_attachment=True,
                download_name=filename,
                mimetype='application/octet-stream'
            )
        except Exception as e:
            return jsonify({'error': f'Error sending file: {str(e)}'}), 500
            
    except Exception as e:
        return jsonify({'error': f'Error processing download: {str(e)}'}), 500

if __name__ == '__main__':
    try:
        print("Initializing download workers...")
        downloader.init_workers()
        print("Starting Flask application on http://localhost:5000")
        app.run(debug=True, port=5000)
    except Exception as e:
        print(f"Error starting application: {str(e)}")