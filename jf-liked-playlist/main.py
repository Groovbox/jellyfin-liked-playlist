from fastapi import FastAPI
from pydantic import BaseModel
import json
from jellyfin import *
import random
from config import Config

user_liked_playlist_map:dict = {}

def sync_playlist():
    global user_liked_playlist_map

    with open("accounts.json") as f:
        data = json.loads(f.read())
    
    accounts:list[JellyfinAccount] = []

    for account in data['accounts']:
        accounts.append(JellyfinAccount(account['Server'], account['Username'], account['Pw']))

    for account in accounts:
        print("Processing for ", account.username)
        all_playlists = get_playlists(account=account)

        playlist_name = f'Favourites: {account.username}'

        if playlist_name in all_playlists.keys():
            print("Playlist exists")
            lkd_pl_id = all_playlists[playlist_name]
        
        else:
            lkd_pl_id = create_playlist(account, playlist_name)
            print("Favourites playlist created")
        
            # Update image
            update_playlist_icon(account, lkd_pl_id, Config().liked_songs_playlist_icon)
        
        # Match songs up
        # get all favorite tracks first
        fav_tracks = get_fav_tracks(account)

        # Get all tracks in lkd_pl
        pl_tracks = get_playlist_tracks(account, lkd_pl_id)

        missing = []

        for track in fav_tracks:
            if track not in pl_tracks:
                missing.append(track)
        
        add_items_to_playlist(account, lkd_pl_id, missing)

        user_liked_playlist_map[account] = lkd_pl_id

app = FastAPI()

class Item(BaseModel):
    item_id: str|None
    name: str|None
    saveReason: str|None
    user_id: str|None

def update_playlist(user_id:str, item_id:str):
    user_id = user_id.replace("-", "")
    item_id = item_id.replace("-", "")
    account:JellyfinAccount = None
    for _account in user_liked_playlist_map.keys():
        if _account.userId == user_id:
            account = _account
            break
    
    if account is None:
        print("Could not find account")
        return
    
    liked_songs_playlist:str = user_liked_playlist_map[account]
    liked_tracks = get_playlist_tracks(account, liked_songs_playlist)

    if item_id in liked_tracks:
        # Remove that track from playlist
        remove_item_from_playlist(account, liked_songs_playlist, item_id)
        print("Removed", item_id, "from Liked Songs Playlist")
    else:
        # Add that track in playlist
        add_items_to_playlist(account, liked_songs_playlist, [item_id])
        print("Added", item_id, "to Liked Songs Playlist")


@app.post("/post")
async def post_request(item: Item):
    print(item)
    update_playlist(item.user_id, item.item_id)
    return {"message": "Data received", "data": item}



if __name__ == '__main__':
    sync_playlist()
    import uvicorn
    uvicorn.run(app, host=Config().host, port=Config().port)
