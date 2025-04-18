from pathlib import Path
import subprocess

ffmpeg = r"ffmpeg-4.2.1-win64-static\bin\ffmpeg.exe"

paths = Path('.').glob('*.flv')
for path in paths:
    path_in_str = str(path)
    print(path_in_str)
    subprocess.call([ffmpeg, "-i", str(path), "-c:v", "libx264", "-crf", "18", "-strict", "experimental", "%s.mp4" %(path.stem)])