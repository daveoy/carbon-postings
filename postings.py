import ffmpeg
import os

# this class describes the transcoded output
class Transcode:
    def __init__(self,source):
        self.filename = source.filename.replace('.mov','.mp4')
        self.clean_source_date = source.date.replace('_','').replace('-','').replace(' ','')
        self.date = f"{self.clean_source_date[0:4]}_{self.clean_source_date[4:6]}_{self.clean_source_date[6:8]}_{source.time}"
        self.container = source.container.replace(
            f"source/{source.date}/{source.time}",
            f"transcode/{self.date}"
        )
        self.path = os.path.join(self.container,self.filename)
        self.transcoded = self.check_transcoded()
    def check_transcoded(self):
        return os.path.exists(self.path)
    def ensure_container_exists(self):
        if not os.path.isdir(self.container):
            print(f"creating container for {self.path}")
            os.makedirs(self.container)

# this class describes a source to be transcoded
class Source:
    def __init__(self,path):
        self.path = path
        self.container = os.path.split(path)[-2]
        self.filename = self.path.split(os.path.sep)[-1]
        self.time = self.path.split(os.path.sep)[-2]
        self.date = self.path.split(os.path.sep)[-3]
        self.project = self.path.split(os.path.sep)[3]
        self.output = Transcode(self)
    def transcode(self):
        self.output.ensure_container_exists()
        (
            ffmpeg
                .input(self.path)
                .output(self.output.path,qmax=69,brand="mp42",vcodec="libx264")
                .run(overwrite_output=True)
        )

"""
encoding settings:
cabac=1
ref=3
deblock=1:0:0
analyse=0x3:0x113
me=hex
subme=7
psy=1
psy_rd=1.00:0.00
mixed_ref=1
me_range=16
chroma_me=1
trellis=1
8x8dct=1
cqm=0
deadzone=21,11
fast_pskip=1
chroma_qp_offset=-2
threads=6
lookahead_threads=1
sliced_threads=0
nr=0
decimate=1
interlaced=0
bluray_compat=0
constrained_intra=0
bframes=3
b_pyramid=2
b_adapt=1
b_bias=0
direct=1
weightb=1
open_gop=0
weightp=2
keyint=250
keyint_min=23
scenecut=40
intra_refresh=0
rc_lookahead=40
rc=crf
mbtree=1
crf=23.0
qcomp=0.60
qpmin=0
qpmax=69
qpstep=4
ip_ratio=1.40
aq=1:1.00
cabac=1
ref=3
deblock=1:0:0
analyse=0x3:0x113
me=hex
subme=7
psy=1
psy_rd=1.00:0.00
mixed_ref=1
me_range=16
chroma_me=1
trellis=1
8x8dct=1
cqm=0
deadzone=21,11
fast_pskip=1
chroma_qp_offset=-2
threads=6
lookahead_threads=1
sliced_threads=0
nr=0
decimate=1
interlaced=0
bluray_compat=0
constrained_intra=0
bframes=3
b_pyramid=2
b_adapt=1
b_bias=0
direct=1
weightb=1
open_gop=0
weightp=2
keyint=250
keyint_min=23
scenecut=40
intra_refresh=0
rc_lookahead=40
rc=crf
mbtree=1
crf=23.0
qcomp=0.60
qpmin=0
qpmax=69
qpstep=4
ip_ratio=1.40
aq=1:1.00
"""