"""Preview strip of a rendered reel at given times: python3 frames.py reel.mp4 out.png 1.0 4.2 ..."""
import sys, subprocess
from PIL import Image
ts = sys.argv[3:]; c = Image.new('RGB', (270*len(ts), 480))
for i, t in enumerate(ts):
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-ss', t, '-i', sys.argv[1], '-frames:v', '1', '-vf', 'scale=270:480', '/tmp/_f.png']); c.paste(Image.open('/tmp/_f.png'), (270*i, 0))
c.save(sys.argv[2])
