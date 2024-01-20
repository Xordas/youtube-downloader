import subprocess
import yt_dlp
import os
import inquirer
import subprocess
import yt_dlp
import os

# option list
questions = [
    inquirer.List('gpu',
                  message="Select the type of encoding:",
                  choices=['NVIDIA GPU (h264_nvenc)', 'AMD GPU (h264_amf)', 'Intel GPU (h264_vaapi)', 'CPU (libx264)']),
    inquirer.Text('video_url', message="Enter the YouTube video URL"),
    inquirer.List('resolution',
                  message="Select the desired resolution:",
                  choices=['360p', '480p', '720p', '1080p', '1440p', '2160p (4K)']),
    inquirer.Confirm('confirmation',
                     message="Do you have the necessary rights and permissions to download this content?",
                     default=False),
]
answers = inquirer.prompt(questions)

# maps
gpu = answers['gpu']
video_url = answers['video_url']
resolution = answers['resolution']
confirmation = answers['confirmation']

# check codec
def check_codec(codec):
    command = ['ffmpeg', '-hide_banner', '-encoders']
    output = subprocess.run(command, capture_output=True, text=True).stdout
    return codec in output

# define codec
if gpu == 'NVIDIA GPU (h264_nvenc)' and check_codec('h264_nvenc'):
    preferedcodec = 'h264_nvenc'
    extra_options = []
elif gpu == 'AMD GPU (h264_amf)' and check_codec('h264_amf'):
    preferedcodec = 'h264_amf'
    extra_options = []
elif gpu == 'Intel GPU (h264_vaapi)' and check_codec('h264_qsv'):
    preferedcodec = 'h264_qsv'
    extra_options = []
else:
    preferedcodec = 'libx264' 
    extra_options = []

# define res
if resolution == '360p':
    format_str = 'bestvideo[height=360]/best[height<=360]'
elif resolution == '480p':
    format_str = 'bestvideo[height=480]/best[height<=480]'
elif resolution == '720p':
    format_str = 'bestvideo[height=720]/best[height<=720]'
elif resolution == '1080p':
    format_str = 'bestvideo[height=1080]/best[height<=1080]'
elif resolution == '1440p':
    format_str = 'bestvideo[height=1440]/best[height<=1440]'
elif resolution == '2160p (4K)':
    format_str = 'bestvideo[height=2160]/best[height<=2160]'
else:
    format_str = 'bestvideo+bestaudio/best'  # default to best

ydl_opts_video = {
    'format': format_str,
    'outtmpl': 'video.%(ext)s',
    'quiet': True,
    'progress_hooks': [lambda d: print(d['status'], d['_percent_str'], d.get('_eta_str', ''))],
}

ydl_opts_audio = {
    'format': 'bestaudio',
    'outtmpl': 'audio.%(ext)s',
    'quiet': True,
    'progress_hooks': [lambda d: print(d['status'], d['_percent_str'], d.get('_eta_str', ''))],
}

# go when yes
if not confirmation:
    print("Download cancelled due to lack of necessary rights and permissions.")
    exit()

print("Starting download...")
try:
    # download video and audio
    with yt_dlp.YoutubeDL(ydl_opts_video) as ydl:
        ydl.download([video_url])
        print("\033[92m" + f"Successfully downloaded video!" + "\033[0m")
    with yt_dlp.YoutubeDL(ydl_opts_audio) as ydl:
        ydl.download([video_url])
        print("\033[92m" + f"Successfully downloaded audio!" + "\033[0m")

    # get the names
    video_file = [f for f in os.listdir() if f.startswith('video.')][0]
    audio_file = [f for f in os.listdir() if f.startswith('audio.')][0]

    # check for 10-bit support
    if preferedcodec == 'h264_nvenc' and not check_codec('hevc_nvenc'):
        preferedcodec = 'hevc_nvenc'  #use hvenc if nvenc doesn't support 10-bit

    # get res
    command = ['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=width,height', '-of', 'csv=s=x:p=0', video_file]
    output = subprocess.run(command, capture_output=True, text=True).stdout.strip()
    width, height = map(int, output.split('x'))

    # get fr
    command = ['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=r_frame_rate', '-of', 'default=noprint_wrappers=1:nokey=1', video_file]
    output = subprocess.run(command, capture_output=True, text=True).stdout.strip()
    framerate = eval(output)

    # set br based on the 2
    if width >= 3840 and height >= 2160:
        bitrate = '85000k' if framerate >= 48 else '56000k'  
    elif width >= 2560 and height >= 1440:
        bitrate = '30000k' if framerate >= 48 else '20000k'  
    elif width >= 1920 and height >= 1080:
        bitrate = '15000k' if framerate >= 48 else '10000k'  
    elif width >= 1280 and height >= 720:
        bitrate = '9500k' if framerate >= 48 else '6500k'  
    else:
        bitrate = '5000k'  

    # get video info
    with yt_dlp.YoutubeDL() as ydl:
        info_dict = ydl.extract_info(video_url, download=False)
        video_title = info_dict.get('title', None)

    # sanitize video title
    video_title = "".join(x for x in video_title if x.isalnum() or x in [" ", "-"]).rstrip()

    print(f"Starting video processing...")
    # ffmpeg merge
    if width < 1280 and height < 720:  # no re-encoding for low-res videos
        command = ['ffmpeg', '-i', video_file, '-i', audio_file, '-c:v', 'copy', '-c:a', 'aac', f'{video_title}.mp4']
    else:
        command = ['ffmpeg', '-i', video_file, '-i', audio_file] + extra_options + ['-vf', 'scale=4096:-1', '-b:v', bitrate, '-c:v', preferedcodec, '-c:a', 'aac', f'{video_title}.mp4']

    process = subprocess.Popen(command, stderr=subprocess.PIPE, universal_newlines=True)

    for line in process.stderr:
        if "speed" in line:  # ffmpeg status line contains speed
            print(line.strip())


    # delete the video and audio files
    os.remove(video_file)
    os.remove(audio_file)

    print("\033[92m" + f"Download completed successfully! The file is named {video_title}.mp4." + "\033[0m")


except Exception as e:
    print("An error occurred:", str(e))


print("Thanks for using this script! Made by github.com/Xordas")
input("Press Enter to close...")