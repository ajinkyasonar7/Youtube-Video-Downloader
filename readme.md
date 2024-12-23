```markdown
# TubeGrab - YouTube Video Downloader

TubeGrab is a web-based YouTube video downloader application built with Flask and yt-dlp that allows users to download videos in various formats and resolutions.

## Features

- Download YouTube videos in multiple resolutions
- Support for both video (MP4/WebM) and audio (MP3) formats
- Real-time download progress tracking
- Queue-based download system
- User-friendly web interface
- Supports concurrent downloads

## Prerequisites

- Python 3.8 or higher
- FFmpeg (required for audio extraction and video processing)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/ajinkyasonar7/TubeGrab.git
cd TubeGrab
```

2. Create a virtual environment and activate it:
```bash
python -m venv venv
# On Windows
venv\Scripts\activate
# On Unix or MacOS
source venv/bin/activate
```

3. Install the required packages:
```bash
pip install -r requirements.txt
```

## Usage

1. Start the application:
```bash
python app.py
```

2. Open your web browser and navigate to `http://localhost:5000`

3. Enter a YouTube URL and select your preferred:
   - Resolution (highest available or specific resolution)
   - Format (MP4, WebM, or MP3 audio)

4. Click download and wait for the process to complete

## Project Structure

```
TubeGrab/
│
├── app.py              # Main Flask application
├── downloader.py       # YouTube download logic
├── requirements.txt    # Project dependencies
├── static/            # Static files (CSS, JS)
└── templates/         # HTML templates
```

## Technical Details

- Built with Flask web framework
- Uses yt-dlp for video downloading
- Implements a threaded download queue for handling multiple downloads
- Temporary file management for downloads
- Progress tracking system
- Error handling and status reporting

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- [yt-dlp](https://github.com/yt-dlp/yt-dlp) for the video downloading functionality
- [Flask](https://flask.palletsprojects.com/) for the web framework

## Support

If you encounter any issues or have questions, please open an issue on the GitHub repository.
```