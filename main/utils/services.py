from backend.settings import BASE_DIR
from threading import Thread
import subprocess
import json
import sys
import re

def getVideoResolution(path):
    cmd = [
        'ffprobe', '-v', 'error',
        '-select_streams', 'v:0',
        '-show_entries', 'stream=width,height',
        '-of', 'json',
        path
    ]

    result = subprocess.run(cmd, stdout=subprocess.PIPE, text=True)
    info = json.loads(result.stdout)
    width = info['streams'][0]['width']
    height = info['streams'][0]['height']
    return (width, height)


def enhanceVideoQuality(input_file, output_file):
    # First, get video duration using ffprobe
    probe = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0",
         "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1",
         input_file],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    try:
        total_duration = float(probe.stdout.strip())
    except:
        print("[ERROR] Couldn't get video duration")
        return

    print(total_duration)

    # FFmpeg command
    cmd = [
        "ffmpeg",
        "-i", input_file,
        "-vf", "hqdn3d,unsharp=5:5:1.0,eq=contrast=1.2:brightness=0.05:saturation=1.2",
        "-c:v", "libx264",
        "-crf", "20",
        "-preset", "slow",
        "-c:a", "aac",
        "-b:a", "128k",
        "-progress", "pipe:1",  # Optional, modern progress (not used here)
        "-nostats",  # Prevent default stats output
        "-hide_banner",
        output_file
    ]

    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)

    # Regex to extract timestamp
    time_pattern = re.compile(r"time=(\d+:\d+:\d+\.\d+)")

    def timestamp_to_seconds(ts):
        h, m, s = map(float, ts.split(':'))
        return h * 3600 + m * 60 + s

    print("[INFO] Enhancing video...")

    for line in process.stdout:
        line = line.strip()
        match = time_pattern.search(line)
        if match:
            current_time = timestamp_to_seconds(match.group(1))
            progress = (current_time / total_duration) * 100
            sys.stdout.write(f"\rProgress: {progress:.2f}%")
            sys.stdout.flush()

    process.wait()
    if process.returncode != 0:
        print("Process: ", process)
        error_output = process.stderr.read()
        print("\n[ERROR] FFmpeg failed:\n", error_output)
        return
    print("\n[DONE] Saved to:", output_file)



def compressVideo1080(path, output):
    cmd = [
            "ffmpeg", "-i", path,
            "-vf", f"scale=1920x1080",
            "-c:v", "libx264",           # H.264 codec
            "-crf", "20",                # Lower = better quality (18–28)
            "-preset", "slow",           # Encoding speed: ultrafast → veryslow
            "-c:a", "aac",               # Audio codec
            "-b:a", "128k",              # Audio bitrate
            output
        ]
    subprocess.run(cmd)

def compressVideo720(path, output):
    cmd = [
            "ffmpeg", "-i", path,
            "-vf", f"scale=1280x720",
            "-c:v", "libx264",           # H.264 codec
            "-crf", "22",                # Lower = better quality (18–28)
            "-preset", "slow",           # Encoding speed: ultrafast → veryslow
            "-c:a", "aac",               # Audio codec
            "-b:a", "128k",              # Audio bitrate
            output
        ]
    subprocess.run(cmd)

def compressVideo480(path, output):
    cmd = [
            "ffmpeg", "-i", path,
            "-vf", f"scale=854x480",
            "-c:v", "libx264",           # H.264 codec
            "-crf", "22",                # Lower = better quality (18–28)
            "-preset", "slow",           # Encoding speed: ultrafast → veryslow
            "-c:a", "aac",               # Audio codec
            "-b:a", "128k",              # Audio bitrate
            output
        ]
    subprocess.run(cmd)


def compressUploadVideo(path, uudi):
    width, height = getVideoResolution(path)

    if width >= 1080:
        output1080 = str(BASE_DIR) + f"/media/videos/1080/{uuid}1080.mp4"
        Thread(target=compressVideo1080, args=(path, output1080)).start()

    if width >= 720:
        output720 = str(BASE_DIR) + f"/media/videos/720/{uuid}720.mp4"
        Thread(target=compressVideo720, args=(path, output720)).start()

    if width >= 480:
        output480 = str(BASE_DIR) + f"/media/videos/480/{uuid}480.mp4"
        Thread(target=compressVideo480, args=(path, output480)).start()
