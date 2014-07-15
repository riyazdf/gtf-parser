import unittest

from gtf_parser import *

class TestTranscript(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_constructor(self):
        trans = Transcript('trans0', 'chr1', '+', None, None, 'gene0')
        self.assertFalse( trans.is_reverse )
        self.assertEqual( trans._furthest_added_exon, None )
        self.assertEqual( trans.exons, [] )

    def test_add_exon(self):
        trans = Transcript('trans0', 'chr1', '+', None, None, 'gene0')

        self.assertRaises( Exception, trans.add_exon, (30, 15) )

        trans.add_exon( (15, 30) )
        self.assertEqual( len(trans.exons), 1 )
        self.assertEqual( trans.exons[0], (15, 30) )
        self.assertEqual( trans._furthest_added_exon, 30 )

        self.assertRaises( Exception, trans.add_exon, (30, 35) )
        self.assertEqual( len(trans.exons), 1 )

        trans.add_exon( (31, 35) )
        self.assertEqual( len(trans.exons), 2 )
        self.assertEqual( trans.exons[1], (31, 35) )
        self.assertEqual( trans._furthest_added_exon, 35 )

        self.assertRaises( Exception, trans.add_exon, (32, 37) )

        self.assertRaises( Exception, trans.add_exon, (30, 37) )


