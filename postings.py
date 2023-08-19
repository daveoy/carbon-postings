import ffmpeg
import os

# this class describes the transcoded output
class Transcode:
    def __init__(self,source):
        self.filename = source.filename.replace('.mov','.mp4')
        self.clean_source_date = source.date.replace('_','').replace('-','').replace(' ','')
        self.date = f"AUTO_{self.clean_source_date[0:4]}_{self.clean_source_date[4:6]}_{self.clean_source_date[6:8]}_{source.time}"
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
        ffmpeg.input(self.path).output(self.output.path,vcodec='h264').run()

