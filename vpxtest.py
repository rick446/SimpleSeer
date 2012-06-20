import struct
import PIL
import vpx
import pyvpx
import gevent.monkey

from SimpleCV import Camera, Image, ColorSpace

from SimpleSeer.util import Clock

RATE=20.0

def main():
    test = Test()
    gevent.monkey.patch_all()
    camera = Camera(0, {})
    clock = Clock(RATE)

    stream = test.encode(camera, clock)
    saved_stream = []

    saved_stream = list(stream)

    with pyvpx.Decoder() as decoder:
        for kind, packet in saved_stream:
            try:
                for img in decoder.decode(packet):
                    img = img.convertTo(vpx.VPX_IMG_FMT_RGB24)
                    pil_img = img.asPilImage()
                    scv_img = Image(pil_img)
                    scv_img.show()
            except Exception, ex:
                print 'Error', ex

class Test(object):

    def __init__(self):
        self.stop = False

    def encode(self, camera, clock):
        img = camera.getImage()
        w,h = img.width, img.height

        with pyvpx.Encoder(w,h) as encoder:
            for f_no, scv_img in enumerate(
                self.capture_iter(camera, clock)):
                v8_img = pyvpx.Image(
                    w, h, vpx.VPX_IMG_FMT_RGB24,
                    data=scv_img.toString())
                v8_img = v8_img.convertTo(vpx.VPX_IMG_FMT_I420)
                for kind, packet in encoder.encode(v8_img, f_no):
                    yield kind, str(packet)
                if f_no == 10: break
                print f_no

    def capture_iter(self, camera, clock):
        while not self.stop:
            clock.tick()
            yield camera.getImage()

if __name__ == '__main__':
    main()
