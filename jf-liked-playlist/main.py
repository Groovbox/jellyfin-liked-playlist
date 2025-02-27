from fastapi import FastAPI
from pydantic import BaseModel
import json
from jellyfin import *

def sync_playlist():
    with open("accounts.json") as f:
        data = json.loads(f.read())
    
    accounts:list[JellyfinAccount] = []

    for account in data['accounts']:
        accounts.append(JellyfinAccount(account['Server'], account['Username'], account['Pw']))

    for account in accounts:
        print("Processing for ", account.username)
        all_playlists = get_playlists(account=account)

        if "Liked Songs" in all_playlists.keys():
            print("Playlist exists")
            lkd_pl_id = all_playlists['Liked Songs']
        
        else:
            lkd_pl_id = create_playlist(account, "Liked Songs")
            print("Liked Songs playlist created")
        
            # Update image
            update_playlist_icon(account, lkd_pl_id, Path("playlist_cover.png"))
        
        # Match songs up
        # get all favorite tracks first
        fav_tracks = get_fav_tracks(account)

        # Get all tracks in lkd_pl
        pl_tracks = get_playlist_tracks(account, lkd_pl_id)

        missing = []

        for track in fav_tracks:
            if track not in pl_tracks:
                missing.append(track)
            else:
                print("Yes")
        
        add_items_to_playlist(account, lkd_pl_id, missing)


app = FastAPI()

class Item(BaseModel):
    item_id: str
    name: str
    isLiked: str
    saveReason: str
    user_id: str

@app.post("/post")
async def post_request(item: Item):
    print(item)
    return {"message": "Data received", "data": item}



if __name__ == '__main__':
    sync_playlist()
    import uvicorn
    uvicorn.run(app, host="192.168.1.16", port=7079)
