from cPickle import dumps
import unittest

from SimpleSeer.models.base import SONScrub

class _Custom(object): pass
class _Custom1(_Custom): pass


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
        self.scrubber.scrub_type(_Custom)
        d = self.scrubber.transform_incoming(dict(a=_Custom()), None)
        self.assertEqual(d, {})

    def test_scrub_subobj(self):
        self.scrubber.scrub_type(_Custom)
        d = self.scrubber.transform_incoming(
            dict(a=dict(a=_Custom())), None)
        self.assertEqual(d, {'a':{}})

    def test_scrub_array(self):
        self.scrubber.scrub_type(_Custom)
        d = self.scrubber.transform_incoming(
            dict(a=[_Custom()]), None)
        self.assertEqual(d, {'a':[]})

    def test_scrub_subclass(self):
        self.scrubber.scrub_type(_Custom)
        d = self.scrubber.transform_incoming(
            dict(a=_Custom1()), None)
        self.assertEqual(d, {})

    def test_bsonify(self):
        self.scrubber.register_bsonifier(_Custom, lambda v,c: 42)
        d = self.scrubber.transform_incoming(dict(a=_Custom()), None)
        self.assertEqual(d, {'a': 42})

    def test_bintype(self):
        self.scrubber.register_bintype(
            _Custom,
            lambda v,c: '42',
            lambda v,c: _Custom())
        d = self.scrubber.transform_incoming(dict(a=_Custom()), None)
        d = self.scrubber.transform_outgoing(d, None)
        self.assert_(isinstance(d['a'], _Custom))

    def test_bintype_ambiguous(self):
        self.scrubber.register_bintype(
            _Custom,
            lambda v,c: '42',
            lambda v,c: _Custom())
        self.assertRaises(
            ValueError, self.scrubber.register_bintype,
            _Custom, lambda v,c: '42', lambda v,c: _Custom())

    def test_bintype_array(self):
        self.scrubber.register_bintype(
            _Custom,
            lambda v,c: '42',
            lambda v,c: _Custom())
        d = self.scrubber.transform_incoming(dict(a=[_Custom()]), None)
        d = self.scrubber.transform_outgoing(d, None)
        self.assert_(isinstance(d['a'][0], _Custom))

    def test_pickle(self):
        obj = dict(a=_Custom())
        d = self.scrubber.transform_incoming(obj, None)
        d1 = self.scrubber.transform_outgoing(d, None)
        self.assertEqual(str(d['a']), dumps(_Custom(), protocol=2))
        self.assert_(isinstance(d1['a'], _Custom))

    def test_too_many_bintypes(self):
        def gen_type():
            class Custom(object): pass
            return Custom
        for x in xrange(127):
            self.scrubber.register_bintype(
                gen_type(), lambda v,c:None, lambda v,c:None)
        self.assertRaises(ValueError, self.scrubber.register_bintype,
                          gen_type(), lambda v,c:None, lambda v,c:None)

    def test_typeid_conflict(self):
        class Custom1(object): pass
        class Custom2(object): pass
        self.scrubber.register_bintype(
            Custom1, lambda v,c:None, lambda v,c:None,
            type_id=129)
        self.assertRaises(
            ValueError, self.scrubber.register_bintype,
            Custom2, lambda v,c:None, lambda v,c:None,
            type_id=129)
