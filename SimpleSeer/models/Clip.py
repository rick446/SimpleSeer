import mongoengine
import cv
import vpx
import pyvpx

from SimpleSeer.base import Image

from .base import SimpleDoc
from ..util import LazyProperty

class Clip(SimpleDoc, mongoengine.Document):
    packets = mongoengine.ListField(mongoengine.BinaryField())

    @classmethod
    def encode(cls, width, height, frame_iter, deadline=vpx.VPX_DL_REALTIME):
        packets = []
        with pyvpx.Encoder(width, height) as encoder:
            for f_no, scv_img in enumerate(frame_iter):
                data = scv_img.toString()
                v8_img = pyvpx.Image(
                    width, height,
                    vpx.VPX_IMG_FMT_RGB24,
                    data=data)
                v8_img = v8_img.convertTo(vpx.VPX_IMG_FMT_I420)
                for kind, packet in encoder.encode(
                    v8_img, f_no, deadline=deadline):
                    packets.append(str(packet))
        return cls(packets=packets)

    @LazyProperty
    def images(self):
        def gen():
            with pyvpx.Decoder() as decoder:
                for packet in self.packets:
                    for image in decoder.decode(packet):
                        rgb = image.convertTo(vpx.VPX_IMG_FMT_RGB24)
                        cv_img = cv.CreateImageHeader(
                            (rgb.width, rgb.height), cv.IPL_DEPTH_8U, 3)
                        cv.SetData(cv_img, rgb.data)
                        yield Image(cv_img)
        return list(gen())
