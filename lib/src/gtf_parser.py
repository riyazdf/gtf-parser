# Riyaz Faizullabhoy
# 7/9/2012
# GTF --> GTF Objects

import argparse
import bisect
import copy
import sys
import warnings

from bisect import *


def run():
    """Runs gtf_parser.py and creates transcript objects for the input GTF
    file.

    Usage: python gtf_parser.py <gtf-input-file-name>
    The GTF file must be in the current directory

    """
    parser = argparse.ArgumentParser()

    parser.add_argument(
        'gi',
        metavar='gtf_input',
        help="The GTF annotation input file name")

    try:
        args = parser.parse_args()
    except ValueError as IOError:
        print "Parsing Error, please use the following command-line format:\npython gtf_parser.py <GTF_FILE_NAME>"

    return gtf_parse(args.gi)


class transcript(object):

    """An object for a given transcript id in the GTF file.

    Will be in the output.

    """

    def __init__(
            self,
            transcript_id,
            seqname,
            strand,
            frame,
            gene_id_attributes,
            gene_id,
            source=None):
        self.transcript_id = transcript_id
        self.refname = seqname
        self.strand = strand
        if strand == "+":
            self.is_reverse = False
        else:
            self.is_reverse = True

        self.frame = frame
        self.gene_id_attributes = gene_id_attributes
        self.gene_id = gene_id
        self.exons = []
        self.furthest_added_exon = 0

        self.source = source

    def add_exon(self, exon):
        """Adds an exon to the transcript object.

        Throws an exception if the exon is out of order in the GTF file,
        or when it overlaps another exon.  If an exception is thrown for
        a given transcript, it will not be included for the output.

        """

        if exon[0] > exon[1]:
            raise Exception(
                "Invalid exon start/stop in transcript: " + str(self.transcript_id))

        # Add an exon to the end (i.e. exons are in order)
        if self.furthest_added_exon < exon[0]:
            self.exons += [exon]
            self.furthest_added_exon = exon[1]
            return

        for e in self.exons:
            if (e[1] >= self.exons[0]) and (self.exons[1] >= e[0]):
                raise Exception(
                    "Overlapping exon in transcript: " + str(self.transcript_id))
        index = bisect_left(
            self.exons,
            exon)  # Add an exon elsewhere, to keep exons sorted
        self.exons.insert(index, exon)

    @property
    def front_coordinate(self):
        """Returns the left-most coordinate of the left-most exon of the transcript object."""
        return self.exons[0][0]

    @property
    def end_coordinate(self):
        """Returns the right-most coordinate of the last (right-most) exon of the transcript object."""
        return self.exons[-1][1]

    def compatible(self, pos):
        """Returns the exon index if 'pos' is inside one of the exons.

        Else, returns -1

        """
        for i in xrange(len(self.exons)):
            if pos >= self.exons[i][0] and pos <= self.exons[i][1]:
                return i
        return -1

    def to_gtf(self):
        trans_str = []
        trans_str.append(self.refname)
        trans_str.append(self.source if self.source is not None else 'NA')
        trans_str.append('exon')

        all_exons = []
        for ex in self.exons:
            exon_str = copy.deepcopy(trans_str)
            exon_str.append(str(ex[0]))
            exon_str.append(str(ex[1]))
            exon_str.append('.')
            exon_str.append('-' if self.is_reverse else '+')
            exon_str.append(str(self.frame))
            exon_str.append('gene_id "' + self.gene_id + '";' +
                            ' transcript_id "' + self.transcript_id + '";')
            # FIXME: after gene_id_attributes is parsers correctly, add this line.
            # (and a space)
            # self.gene_id_attributes)
            all_exons.append('\t'.join(exon_str))

        return '\n'.join(all_exons)

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return '{0}\t{1}\t{2}\t{3}'.format(
            self.transcript_id,
            self.refname,
            self.front_coordinate,
            self.end_coordinate)


def gtf_parse(input_gtf):
    """Parses the input GTF file by line.

    Creates a list of transcript objects that include each transcript's id, refname, strand, frame, gene id, and its exons.  Uses 1-based inclusive coordinates.  For example, start: 1, end: 2 would be an exon of length two (at 1, 2).

    """
    transcript_dictionary = {}
    bad_transcripts = []
    current_transcript = None
    gtf_file = open(input_gtf, 'r')
    for line in gtf_file:

        if line.startswith('#'):
            continue

        gtf_line = (line.split("\t"))

        if gtf_line[2] != "exon":
            continue

        try:
            transcript_id = (
                gtf_line[8].split(";")[1].split(" ")[2].replace(
                    "\"",
                    ""))
            if transcript_id in bad_transcripts:
                continue

        except IndexError as i:
            print "GTF File Input missing 'transcript_id' field"

        if current_transcript is None:
            try:
                # FIXME: gene_id_attributes isn't being parsed correctly
                gene_id = gtf_line[8].split(";")[0].split(
                    " ")[1].replace("\"", "")
                current_transcript = transcript(
                    transcript_id,
                    gtf_line[0],
                    gtf_line[6],
                    gtf_line[7],
                    gtf_line[8].split(" ")[3],
                    gene_id,
                    gtf_line[1])
                transcript_dictionary[transcript_id] = current_transcript
                transcript_dictionary[transcript_id].add_exon(
                    (int(
                        gtf_line[3]), int(
                        gtf_line[4])))
            except IndexError as i:
                print "GTF File Input missing fields"
            except Exception as e:
                print(e)
                bad_transcripts += current_transcript.transcript_id
                current_transcript = None  # throw out the bad transcript
                transcript_dictionary[transcript_id] = None

        elif transcript_id != current_transcript.transcript_id:
            try:
                transcript_dictionary[transcript_id].add_exon(
                    (int(
                        gtf_line[3]), int(
                        gtf_line[4])))
                current_transcript = transcript_dictionary[transcript_id]
            except KeyError as k:
                gene_id = gtf_line[8].split(";")[0].split(
                    " ")[1].replace("\"", "")
                # FIXME: gene_id_attributes isn't being parsed correctly
                current_transcript = transcript(
                    transcript_id,
                    gtf_line[0],
                    gtf_line[6],
                    gtf_line[7],
                    gtf_line[8].split(" ")[
                        4:],
                    gene_id,
                    gtf_line[1])
                transcript_dictionary[transcript_id] = current_transcript
                transcript_dictionary[transcript_id].add_exon(
                    (int(
                        gtf_line[3]), int(
                        gtf_line[4])))

            except IndexError as i:
                print "GTF File Input missing fields"
            except Exception as e:
                print(e)
                bad_transcripts += current_transcript.transcript_id
                current_transcript = None
                transcript_dictionary[transcript_id] = None

        else:
            try:
                current_transcript.add_exon(
                    (int(
                        gtf_line[3]), int(
                        gtf_line[4])))
            except IndexError as i:
                print "GTF File Input missing fields"
            except Exception as e:
                print(e)
                bad_transcripts += current_transcript.transcript_id
                current_transcript = None
                transcript_dictionary[transcript_id] = None

    gtf_file.close()

    print >> sys.stderr, ("Number of transcript objects made: " +
                          str(len(transcript_dictionary.keys())))
    print >> sys.stderr, "Done."

    return transcript_dictionary


def gtf_write(all_trans, out_handle):
    for key in all_trans:
        cur_trans = all_trans[key]
        print >> out_handle, cur_trans.to_gtf()


if (__name__ == "__main__"):
    run()