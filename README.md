# YouTube Video Downloader

This script allows you to download YouTube videos at various resolutions and encode them using different codecs.

## Prerequisites

You need to have the latest version of Python and the following Python packages installed:

- `yt-dlp`
- `inquirer`

You can install these packages using pip:

```bash
pip install yt-dlp inquirer
```

You also need to have ffmpeg and ffprobe installed on your system.

## Usage
Run the script with Python:
```bash
python yt.py
```

The script will ask for the Youtube video URL, and then ask for the resoloution. If you chose more than 720p the video will be processed in the chosen resoloution with the codec you provided.
This script has only been tested on systems with an Intel Arc A770 and a Nvidia Quadro P2000. If you're using a different GPU, your feedback would be greatly appreciated to help me improve the script. Please report any issues or bugs you encounter.

## Disclaimer
This script is for educational purposes only. Do not use it to download copyrighted content or other material that you do not have the rights to download. I am not responsible for any misuse of the script.

## License
This project is licensed under the MIT License.
