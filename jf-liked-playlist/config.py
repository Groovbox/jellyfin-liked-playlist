import json
from pathlib import Path

class Config:
    def __init__(self):
        data = json.load(open("config.json"))

        self.port:str = data['PORT']
        self.host:int = data['HOST']
        self.liked_songs_playlist_icon = Path(data['LIKED_SONGS_PLAYLIST_ICON'])