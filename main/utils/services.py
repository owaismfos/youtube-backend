from backend.settings import BASE_DIR, MEDIA_ROOT
from threading import Thread

from main.models.video_model import Video

# from moviepy import VideoFileClip

import subprocess
import json
import sys
import re
import os

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

def getVideoDuration(path):
    probe = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0",
         "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1",
        path],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    try:
        total_duration = float(probe.stdout.strip())
        return total_duration
    except:
        print("[ERROR] Couldn't get video duration")
        return 0

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


def compressUploadVideo(path, uuid):
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




def compress_video_to_hls(video_id):
    video = Video.objects.get(uniqueId=video_id)
    input_file = video.videoOriginal.path
    output_dir = os.path.join(MEDIA_ROOT, f"hls/{video_id}")
    os.makedirs(output_dir, exist_ok=True)

    output_master = os.path.join(output_dir, "master.m3u8")

    cmd = [
        "ffmpeg", "-i", input_file,
        "-preset", "veryfast", "-g", "48", "-sc_threshold", "0",
        "-map", "0:v", "-map", "0:a",
        "-s:v:0", "1920x1080", "-b:v:0", "5000k",
        "-s:v:1", "1280x720",  "-b:v:1", "3000k",
        "-s:v:2", "854x480",   "-b:v:2", "1500k",
        "-s:v:3", "640x360",   "-b:v:3", "800k",
        "-var_stream_map", "v:0,a:0 v:1,a:0 v:2,a:0 v:3,a:0",
        "-hls_time", "6", "-hls_list_size", "0", "-f", "hls",
        "-master_pl_name", "master.m3u8",
        "-hls_segment_filename", os.path.join(output_dir, "v%v/segment_%03d.ts"),
        os.path.join(output_dir, "v%v/stream.m3u8")
    ]

    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True
    )

    # Progress parsing in separate thread
    # def track_progress():
    for line in process.stdout:
        print("[FFMPEG]", line.strip())
        if "frame=" in line:
            # Estimate progress roughly using frame count (optional)
            print("[PROGRESS]", line.strip())
            # Optional: update video.progress = X and save()

    # Thread(target=track_progress).start()
    process.wait()

    # Save output in DB
    video.videoHlsPlayList.name = f"hls/{video_id}/master.m3u8"
    video.resolutions = ["1080p", "720p", "480p", "360p"]
    video.save()