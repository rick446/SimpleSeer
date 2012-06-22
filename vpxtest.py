import time

import vpx
import numpy as np
from SimpleCV import Camera

from SimpleSeer.util import Clock
from SimpleSeer import models as M

RATE=24.0
NUM_FRAMES=24

def main():
    camera = Camera(0, dict(width=640, height=480))
    clock = Clock(RATE)

    # capture frames as scv images
    frames = list(capture_frames(camera, clock, NUM_FRAMES))

    print '=== REALTIME ==='
    decoded_frames = run_test(frames, vpx.VPX_DL_REALTIME)
    playback(clock, decoded_frames)
    print '=== GOOD QUALITY ==='
    decoded_frames = run_test(frames, vpx.VPX_DL_GOOD_QUALITY)
    playback(clock, decoded_frames)
    print '=== BEST QUALITY ==='
    decoded_frames = run_test(frames, vpx.VPX_DL_BEST_QUALITY)
    playback(clock, decoded_frames)

def capture_frames(camera, clock, num_frames):
    for fno in xrange(num_frames):
        clock.tick()
        yield camera.getImage()

def playback(clock, frames):
    for img in frames:
        clock.tick()
        img.show()

def run_test(frames, deadline):
    # Encode frames
    start = time.time()
    w,h = frames[0].width, frames[0].height
    clip = M.Clip.encode(w,h,frames, deadline=deadline)
    elapsed = time.time() - start
    print '%d frames encoded in %fs, %.2f fps (avg) (%d kB)' % (
        NUM_FRAMES, elapsed, NUM_FRAMES / elapsed,
        sum(len(p) for p in clip.packets) / 2**10)

    # Decode frames
    start = time.time()
    decoded_frames = clip.images
    elapsed = time.time() - start
    print '%d frames decoded in %fs, %.2f fps (avg)' % (
        NUM_FRAMES, elapsed, NUM_FRAMES / elapsed)

    print 'MSE: %.2f' % mse_clip(frames, decoded_frames)
    return decoded_frames


def mse_frame(org, new):
    orga = np.fromstring(org.toString(), dtype=np.uint8)
    newa = np.fromstring(new.toString(), dtype=np.uint8)
    se = np.sum((orga-newa)**2)
    return float(se) / len(orga)

def mse_clip(org_frames, new_frames):
    return sum(mse_frame(o,n) for o,n in zip(org_frames, new_frames)) / len(new_frames)

if __name__ == '__main__':
    main()
