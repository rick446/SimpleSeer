import unittest
from datetime import datetime

from SimpleSeer.models.base import SONScrub

class TestSonScrub(unittest.TestCase):

    def setUp(self):
        self.registry = SONScrub.clear_registry()
        self.scrubber = SONScrub()

    def tearDown(self):
        SONScrub.restore_registry(self.registry)

    def test_default(self):
        obj = dict(a=1, b=[2,3], c=dict(d='foo'))
        d = self.scrubber.transform_incoming(obj, None)
        self.assertEqual(d, obj)

    def test_scrub(self):
        class Custom(object): pass
        self.scrubber.scrub_type(Custom)
        d = self.scrubber.transform_incoming(dict(a=Custom()), None)
        self.assertEqual(d, {})

    def test_scrub_subobj(self):
        class Custom(object): pass
        self.scrubber.scrub_type(Custom)
        d = self.scrubber.transform_incoming(
            dict(a=dict(a=Custom())), None)
        self.assertEqual(d, {'a':{}})

    def test_scrub_array(self):
        class Custom(object): pass
        self.scrubber.scrub_type(Custom)
        d = self.scrubber.transform_incoming(
            dict(a=[Custom()]), None)
        self.assertEqual(d, {'a':[]})

    def test_scrub_subclass(self):
        class Custom(object): pass
        class Custom1(Custom): pass
        self.scrubber.scrub_type(Custom)
        d = self.scrubber.transform_incoming(
            dict(a=Custom1()), None)
        self.assertEqual(d, {})

    def test_bsonify(self):
        class Custom(object): pass
        self.scrubber.register_bsonifier(Custom, lambda v,c: 42)
        d = self.scrubber.transform_incoming(dict(a=Custom()), None)
        self.assertEqual(d, {'a': 42})

    def test_bintype(self):
        class Custom(object): pass
        self.scrubber.register_bintype(
            Custom,
            lambda v,c: '42',
            lambda v,c: Custom())
        d = self.scrubber.transform_incoming(dict(a=Custom()), None)
        d = self.scrubber.transform_outgoing(d, None)
        self.assert_(isinstance(d['a'], Custom))

    def test_bintype_array(self):
        class Custom(object): pass
        self.scrubber.register_bintype(
            Custom,
            lambda v,c: '42',
            lambda v,c: Custom())
        d = self.scrubber.transform_incoming(dict(a=[Custom()]), None)
        d = self.scrubber.transform_outgoing(d, None)
        self.assert_(isinstance(d['a'][0], Custom))

    def test_no_serializer(self):
        class Custom(object): pass
        obj = dict(a=Custom())
        d = self.scrubber.transform_incoming(obj, None)
        self.assertEqual(d, obj)
