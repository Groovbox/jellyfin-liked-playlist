import requests

def get_headers(token:str=None) -> dict:
    headers = {
    'authorization': f'MediaBrowser Client="Octo", Device="Chrome", DeviceId="TW96aWxsYS81LjAgKFgxMTsgTGludXggeDg2XzY0KSBBcHBsZVdlYktpdC81MzcuMzYgKEtIVE1MLCBsaWtlIEdlY2tvKSBDaHJvbWUvMTMxLjAuMC4wIFNhZmFyaS81MzcuMzZ8MTczODE0NDMzNjc4NQ11", {'Token="'+token+'", ' if token else ''} Version="10.10.3"',
    }
    return headers



class JellyfinAccount:
    token:str = None
    userId:str = None
    def __init__(self, server:str, username:str, password:str):
        self.server = server
        self.username = username
        self.password = password

        self.authenticate()

    def authenticate(self) -> str:
        _authentication_url = f"{self.server}/Users/AuthenticateByName"
        payload = {
            "Username": self.username,
            "Pw": self.password
        }

        response = requests.post(_authentication_url, json=payload, headers=get_headers())
        response.raise_for_status()

        self.token = response.json()["AccessToken"]
        self.userId = response.json()['User']['Id']

        return 

    def __json__(self):
        return {
            'Server': self.server,
            'Username': self.username,
            'Pw': self.password
        }

def get_playlists(account:JellyfinAccount) -> dict:
    """
    Returns all playlists of a user
    """
    playlist_id_map = {}

    resp = requests.get(account.server+f"/Users/{account.userId}/Items?includeItemTypes=Playlist&Recursive=true", headers=get_headers(account.token))

    for item in resp.json()['Items']:
        playlist_id_map[item['Name']] = item['Id']

    return playlist_id_map

def create_playlist(account:JellyfinAccount, playlist_name:str, playlist_image=None) -> str:
    create_playlist_endpoint_url:str = account.server + "/Playlists"

    payload_data  = {
        "isPublic": False,
        "Name": playlist_name, 
        "UserId": account.userId
    }

    response = requests.post(create_playlist_endpoint_url, json=payload_data, headers=get_headers(account.token))

    return response.json()['Id']

def get_fav_tracks(account:JellyfinAccount) -> list[str]:
    fav_tracks_list = []
    fav_tracks_endpoint = account.server + f"/Items?includeItemTypes=Audio&filters=IsFavorite&Recursive=true"

    resp = requests.get(fav_tracks_endpoint, headers=get_headers(account.token))

    for item in resp.json()["Items"]:
        fav_tracks_list.append(item["Id"])

    return fav_tracks_list

def get_playlist_tracks(account:JellyfinAccount, playlist_id:str) -> list[str]:
    endpoint_url = account.server + f"/Playlists/{playlist_id}"

    resp = requests.get(endpoint_url, headers=get_headers(account.token))
    return resp.json()["ItemIds"]

def add_items_to_playlist(account:JellyfinAccount, playlist_id, items:list[str]):
    ids_str = ""
    for i,item in enumerate(items):
        ids_str+=item
        if i != len(items)-1:
            ids_str+=","
    
    endpoint_url = account.server + f"/Playlists/{playlist_id}/Items?ids={ids_str}&userId={account.userId}"
    print(endpoint_url)
    resp = requests.post(endpoint_url, headers=get_headers(account.token))

    print(resp.status_code)

