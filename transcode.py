import sys
from postings import Source

# this is intended to be run with a single arg, path to a file to transcode
src = Source(sys.argv[1])
src.transcode()