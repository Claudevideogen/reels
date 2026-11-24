"""Contact sheet of fetched clips: python3 contact.py clips/<name> out.png  (rows = request lines, cols = a-d)"""
import sys, glob, os, subprocess
from PIL import Image, ImageDraw
d = sys.argv[1].rstrip('/'); fs = sorted(glob.glob(d + '/*.mp4')); rows = max(int(os.path.basename(f)[:2]) for f in fs)
c = Image.new('RGB', (4*256, rows*165), (0, 0, 0)); dr = ImageDraw.Draw(c)
for f in fs:
    n = os.path.basename(f)[:-4]; r = int(n[:2]) - 1; col = 'abcd'.index(n[2]); tmp = f'/tmp/_cs_{n}.png'
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-ss', '2', '-i', f, '-frames:v', '1', '-vf', 'scale=256:144:force_original_aspect_ratio=decrease,pad=256:144:(ow-iw)/2:(oh-ih)/2', tmp])
    if os.path.exists(tmp): c.paste(Image.open(tmp), (col*256, r*165+18)); os.remove(tmp)
    dr.text((col*256+4, r*165+2), n, fill=(255, 255, 0))
c.save(sys.argv[2]); print(sys.argv[2])
