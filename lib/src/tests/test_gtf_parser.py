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

        self.assertEqual( trans.front_coordinate, 15 )
        self.assertEqual( trans.end_coordinate, 35 )

        # TODO: test bisect op

    def test_to_gtf(self):
        trans = Transcript('trans0', 'chr1', '+', None, None, 'gene0')

        self.assertRaises( Exception, trans.to_gtf )

    def test_compatible(self):
        trans = Transcript('trans0', 'chr1', '+', None, None, 'gene0')
        trans.add_exon( (15, 30) )

        self.assertEqual( trans.compatible( 90 ), None )
        self.assertEqual( trans.compatible( 30 ), None )
        self.assertEqual( trans.compatible( 29 ), 0 )

        trans.add_exon( (35, 40) )
        self.assertEqual( trans.compatible( 90 ), None )
        self.assertEqual( trans.compatible( 30 ), None )
        self.assertEqual( trans.compatible( 29 ), 0 )
        self.assertEqual( trans.compatible( 35 ), 1 )
        self.assertEqual( trans.compatible( 37 ), 1 )

class TestGTFParse(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_gtf_parse_snippet(self):
        fname = 'tests/inputs/snippet.gtf'

        transcripts = gtf_parse(fname)
        self.assertEqual( len(transcripts), 1 )
        self.assertEqual( transcripts.keys(), ['NM_021025'] )

    # TODO: test gtf_parse more thoroughly
    

# TODO: test gtf_write
