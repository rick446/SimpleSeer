import unittest
from datetime import datetime

import mock
from SimpleCV.ImageClass import Image

from SimpleSeer import models as M
from .. import utils

class TestFrame(unittest.TestCase):

    @mock.patch('SimpleSeer.realtime.ChannelManager')
    def setUp(self, cm):
        img = Image('lenna')
        frame = M.Frame(capturetime=datetime.utcnow(), camera='test')
        frame.image = img
        self.frame = frame
        utils.register_mim_connection()
        self.frame.save()

    def test_get_image_in_cache(self):
        assert isinstance(self.frame.image, Image)

    def test_get_image_from_db(self):
        frame = M.Frame.objects[0]
        assert isinstance(frame.image, Image)

    def test_serialize(self):
        result = self.frame.serialize()
        self.assertEqual(
            sorted(result.keys()),
            [ 'content_type', 'data' ])
        assert result['content_type'] in ('image/webp', 'image/jpeg')
        
        
