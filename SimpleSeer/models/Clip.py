import struct
import fractions

import mongoengine
import cv
import vpx
import pyvpx

from SimpleSeer.base import Image

from .base import SimpleDoc
from ..util import LazyProperty, Clock

class Clip(SimpleDoc, mongoengine.Document):
    width = mongoengine.IntField()
    height = mongoengine.IntField()
    rate = mongoengine.FloatField()
    packets = mongoengine.ListField(mongoengine.BinaryField())

    def __repr__(self):
        return '<Clip (%d x %d) @%.1f Hz (%d)>' % (
            self.width, self.height, self.rate, len(self.packets))

    @classmethod
    def encoder(cls, width, height, rate, frames_per_clip=10, deadline=vpx.VPX_DL_REALTIME):
        def result(img_iter):
            packets, images = [], []
            encoder = pyvpx.Encoder(width, height)
            for f_no, scv_img in enumerate(img_iter):
                images.append(scv_img)
                data = scv_img.toString()
                v8_img = pyvpx.Image(
                    width, height,
                    vpx.VPX_IMG_FMT_RGB24,
                    data=data)
                v8_img = v8_img.convertTo(vpx.VPX_IMG_FMT_I420)
                for kind, packet in encoder.encode(
                    v8_img, f_no, deadline=deadline):
                    packets.append(str(packet))
                if frames_per_clip is None: continue
                if f_no and f_no % frames_per_clip == 0:
                    result = cls(
                        width=width,
                        height=height,
                        rate=rate,
                        packets=packets)
                    result.images = images
                    yield result
                    encoder.close()
                    encoder = pyvpx.Encoder(width, height)
                    packets, images = [], []
            if packets:
                result = cls(
                    width=width,
                    height=height,
                    rate=rate,
                    packets=packets)
                result.images = images
                yield result
                encoder.close()
        return result

    @classmethod
    def encode(cls, width, height, frame_iter, deadline=vpx.VPX_DL_REALTIME):
        encoder = cls.encoder(width, height, frames_per_clip=None, deadline=deadline)
        return encoder(frame_iter).next()

    @LazyProperty
    def images(self):
        def gen():
            print 'Decoding clip', self.id
            with pyvpx.Decoder() as decoder:
                for packet in self.packets:
                    for image in decoder.decode(packet):
                        rgb = image.convertTo(vpx.VPX_IMG_FMT_RGB24)
                        cv_img = cv.CreateImageHeader(
                            (rgb.width, rgb.height), cv.IPL_DEPTH_8U, 3)
                        cv.SetData(cv_img, rgb.data)
                        yield Image(cv_img)
            print 'Clip decoded'
        return list(gen())

    def show(self):
        clock = Clock(self.rate)
        images = self.images
        print 'There are %d images at %f Hz' % (
            len(images), self.rate)
        for image in self.images:
            clock.tick()
            image.show()

    def ivf(self):
        '''Intel video format dump'''
        yield _ivf_file_header(
            self.width, self.height, self.rate, len(self.packets))
        for pts, packet in enumerate(self.packets):
            yield _ivf_frame_header(len(packet), pts)
            yield packet

def _ivf_file_header(width, height, rate, num_frames):
    timebase = fractions.Fraction(1.0/rate).limit_denominator(100)
    return 'DKIF' + struct.pack(
        '<HHLHHLLLL',
        0, # version,
        32, # headersize,
        0x30385056, # fourcc
        width,
        height,
        timebase.denominator,
        timebase.numerator,
        num_frames,
        0)

def _ivf_frame_header(frame_size, pts):
    return struct.pack('<LQ', frame_size, pts)

