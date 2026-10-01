# Makes the jersey mask for a card picture: parts/cards/<card>-mask.png, white
# where the game recolours the jerseys to a team's colours, black elsewhere.
#
#   python tools/card_mask.py <card> <red|navy> [min_blob]
#
# red  = jerseys painted red   (the Cyclops: his own side)
# navy = jerseys painted navy  (Beowulf: the men he is hitting)
# Stray specks and thin streaks that happen to match the colour are dropped:
# only blobs of at least min_blob pixels (default 900, on the 800x600 picture)
# and solid enough to be cloth, and not running off the edge, are kept.
import os, sys
from collections import deque
from PIL import Image, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
CARDS = os.path.join(HERE, '..', 'parts', 'cards')

def is_red(r, g, b):
    return r >= 45 and g <= r * 0.40 and b <= r * 0.52 and r - max(g, b) >= 28

def is_navy(r, g, b):                      # navy, not the teal of a stadium at night
    return 45 <= b <= 160 and b - g >= 18 and b - r >= 24 and g - r <= 22 and r < 105

def main():
    card, kind = sys.argv[1], sys.argv[2]
    min_blob = int(sys.argv[3]) if len(sys.argv) > 3 else 900
    test = is_red if kind == 'red' else is_navy
    im = Image.open(os.path.join(CARDS, card + '.jpg')).convert('RGB')
    w, h = im.size
    px = im.load()
    hit = bytearray(w * h)
    for y in range(h):
        for x in range(w):
            if test(*px[x, y]):
                hit[y * w + x] = 1
    keep = bytearray(w * h)
    seen = bytearray(w * h)
    for start in range(w * h):
        if not hit[start] or seen[start]:
            continue
        blob = []
        q = deque([start]); seen[start] = 1
        x0 = y0 = 10 ** 9; x1 = y1 = -1
        while q:
            i = q.popleft(); blob.append(i)
            x, y = i % w, i // w
            x0 = min(x0, x); x1 = max(x1, x); y0 = min(y0, y); y1 = max(y1, y)
            for j in (i - 1, i + 1, i - w, i + w):
                if 0 <= j < w * h and hit[j] and not seen[j] and abs(j % w - x) <= 1:
                    seen[j] = 1; q.append(j)
        fill = len(blob) / float((x1 - x0 + 1) * (y1 - y0 + 1))
        edge = x0 <= 2 or y0 <= 2 or x1 >= w - 3 or y1 >= h - 3   # the crowd and the sky run off the picture; a jersey does not
        if len(blob) >= min_blob and fill >= 0.18 and not edge:   # cloth, not a streak
            for i in blob:
                keep[i] = 1
    mask = Image.frombytes('L', (w, h), bytes(255 if k else 0 for k in keep))
    mask = mask.filter(ImageFilter.MaxFilter(3)).filter(ImageFilter.MinFilter(3))   # close pinholes in the cloth
    out = os.path.join(CARDS, card + '-mask.png')
    mask.save(out, optimize=True)
    print('wrote', out, sum(keep), 'pixels')

if __name__ == '__main__':
    main()
