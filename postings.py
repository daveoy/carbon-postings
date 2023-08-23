import ffmpeg
import os
import json
import requests

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
        self.webhookURL = "https://whitehousepost.webhook.office.com/webhookb2/dd6f12b1-92cd-42b8-bf21-fae1b5055581@f2cc8bed-6791-456d-833e-0a8d2c1ee8f6/IncomingWebhook/fb9729e5b6cd42a0b3d3534d645485b1/e7d508af-cd60-4109-a3a8-251f6085c3df"

    def post_to_teams(self,msg_json):
        headers = {
            "content-type":"application/json"
        }
        body = {
            "webhookUrl":self.webhookURL,
            "title":f"posting {self.project}",
            "message":json.dumps(msg_json),
            "color":"green"
        }
        requests.post('https://engineering.carbonvfx.com/postToTeamsJSON',headers=headers,data=json.dumps(body))

    def transcode(self):
        self.output.ensure_container_exists()
        (
            ffmpeg
                .input(self.path)
                .output(
                    self.output.path,
                    qmax=69,
                    brand="mp42",
                    vcodec="libx264",
                    pix_fmt="yuv420p",
                    )
                .run(overwrite_output=True)
        )

