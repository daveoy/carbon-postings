import sys
from postings import Source

# this is intended to be run with a single arg, path to a file to transcode
src = Source(sys.argv[1])
src.transcode()
info_json = {
    "event_source":"transcode",
    "project": src.project,
    "source_path":src.path,
    "transcode_path": src.output.path,
    "filename": src.output.filename,
    "msg":f"transcode complete"
}
src.post_to_teams(info_json)