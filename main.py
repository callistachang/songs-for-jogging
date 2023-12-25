import spotipy
from dotenv import load_dotenv
from typing import List
import os
import random
import json

load_dotenv()

SPOTIPY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIPY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
USER_ID = os.getenv("SPOTIFY_USER_ID")

# quick and poorly designed script thing
class MySpotifyClient:
    def __init__(self, user_id):
        # use this if you only need read access
        # self.sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials())

        # use oauth if need to make write access (like creating a playlist)
        # authenticate once on the web, don't need to authenticate again for a while
        self.sp = spotipy.Spotify(
            auth_manager=spotipy.oauth2.SpotifyOAuth(
                client_id=SPOTIPY_CLIENT_ID,
                client_secret=SPOTIPY_CLIENT_SECRET,
                redirect_uri="http://localhost/",  # must add to whitelist on your dev dashboard
                scope="playlist-modify-public",
                open_browser=False
            )
        )
        self.user_id = user_id
        self.playlists_fp = "./playlists.json"
        self.songs_and_features_fp = "./songs_and_features.json"

    def retrieve_and_write_playlist_data(self, use_cache=True):
        playlists_dict = dict()
        if os.path.isfile(self.playlists_fp) and use_cache:
            with open(self.playlists_fp, "r") as f:
                playlists_dict = json.load(f)
        else:
            playlist_results = self.sp.user_playlists(
                self.user_id
            )  # max limit of 50 results per api call

            # make api calls until no more playlists to retrieve
            while playlist_results:
                for playlist in playlist_results["items"]:
                    playlists_dict[playlist["name"]] = playlist["id"]
                if playlist_results["next"]:
                    playlist_results = self.sp.next(playlist_results)
                else:
                    playlist_results = None
            # write playlists data to file, use as cache
            with open(self.playlists_fp, "w") as f:
                json.dump(playlists_dict, f)
        print(f"you have {len(playlists_dict)} playlists!")
        return playlists_dict

    # TODO: use multithreading make this async tho idk if it'll trigger rate limits
    # TODO: instead of taking from all user playlists, make it such that you can
    # specify a playlist or list of playlists
    def retrieve_and_write_playlist_songs_and_features(self, use_cache=True):
        if os.path.isfile(self.songs_and_features_fp) and use_cache:
            with open(self.songs_and_features_fp, "r") as f:
                songs_list = json.load(f)
        else:
            playlists_dict = self.retrieve_and_write_playlist_data(use_cache)
            songs_dict = dict()

            # this make take some time if you are like me and have 200 playlists
            for name, playlist_id in playlists_dict.items():
                print(f"writing songs for playlist '{name}'...")
                tracks = self.sp.user_playlist_tracks(self.user_id, playlist_id)
                track_chunks = self._split_into_data_chunks(
                    tracks["items"], chunk_size=100
                )
                for chunk in track_chunks:
                    # for some weird reason, select songs in spotify are corrupt and don't have an id
                    id_chunk = [x["track"]["id"] for x in chunk if x["track"]["id"]]
                    try:
                        # audio features of the song, such as tempo, energy, etc. cool stuff
                        # ref: https://developer.spotify.com/documentation/web-api/reference/#/operations/get-audio-features
                        features = self.sp.audio_features(id_chunk)
                        for i, feature in enumerate(features):
                            track = chunk[i]["track"]
                            data = {
                                "primary_song_artist": track["artists"][0]["name"],
                                "song_name": track["name"],
                                "song_id": track["id"],
                                "features": feature,
                            }
                            # ensure no duplicates
                            songs_dict[
                                (data["song_name"], data["primary_song_artist"])
                            ] = data
                    except spotipy.exceptions.SpotifyException as e:
                        # sometimes songs on spotify haven't got their audio features yet, don't let one song stop the show
                        print(e.reason)
            print(
                f"you have a combined total of {len(songs_dict)} songs in your playlists, noice"
            )
            songs_list = list(songs_dict.values())
            with open(self.songs_and_features_fp, "w") as f:
                json.dump(songs_list, f)
        return songs_list

    def _split_into_data_chunks(self, data: List, chunk_size: int):
        return [data[x : x + chunk_size] for x in range(0, len(data), chunk_size)]

    # default condition
    def jogging_songs(self, features):
        return (
            82 < features["tempo"] < 85 or 82 * 2 < features["tempo"] < 85 * 2
        ) and features["energy"] > 0.7 and features["valence"] > 0.4

    def create_playlist(
        self,
        condition,
        playlist_name="New Playlist",
        use_cache=True,
    ):
        if os.path.isfile(self.songs_and_features_fp) and use_cache:
            with open(self.songs_and_features_fp, "r") as f:
                songs = json.load(f)
        else:
            songs = self.retrieve_and_write_playlist_songs_and_features(use_cache)

        songs_to_add = []
        for song in songs:
            f = song["features"]
            if condition(f):
                preamble = f"added: '{song['song_name']}' by {song['primary_song_artist']}"
                print(
                    f"{preamble:<80} | bpm={f['tempo']} energy={f['energy']} valence={f['valence']}"
                )
                songs_to_add.append(song["song_id"])

        assert songs_to_add, "no songs to add into playlist"
        print(
            f"found {len(songs_to_add)} songs to add into your new {playlist_name} playlist!"
        )

        # who doesn't love a lil bit of randomness
        random.shuffle(songs_to_add)

        created_playlist_id = self.sp.user_playlist_create(
            self.user_id, playlist_name
        )["id"]
        chunks = self._split_into_data_chunks(songs_to_add, chunk_size=100)
        for chunk in chunks:
            try:
                self.sp.playlist_add_items(created_playlist_id, chunk)
            except Exception as e:
                print(e)

# TODO: make a cli interface for this
if __name__ == "__main__":
    client = MySpotifyClient(USER_ID)
    # TODO: stateful and messy, change this later
    client.retrieve_and_write_playlist_songs_and_features()

    # use https://developer.spotify.com/documentation/web-api/reference/#/operations/get-audio-features
    # to see which features you can play with

    # client.create_playlist(playlist_name="autogen_high_valence_high_energy", condition=lambda f: f["valence"] > 0.8 and f["energy"] > 0.8)
    # client.create_playlist(playlist_name="autogen_jogging_songs", condition=lambda f: client.jogging_songs(f))
    # client.create_playlist(playlist_name="autogen_live", condition=lambda features: features["liveness"] > 0.8)
    # client.create_playlist(playlist_name="apparently-happy", condition=lambda features: features["valence"] > 0.9)
    # client.create_playlist(playlist_name="apparently-sad", condition=lambda features: features["valence"] < 0.1)
    # client.create_playlist(playlist_name="apparently-danceable", condition=lambda features: features["danceability"] > 0.8 and features["energy"] > 0.8 and features["valence"] > 0.8)
    # client.create_playlist(playlist_name="apparently-acoustic", condition=lambda features: features["acousticness"] > 0.9)
    # client.create_playlist(playlist_name="in-the-key-of-c", condition=lambda features: features["key"] == 0)
    # client.create_playlist(playlist_name="in-the-key-of-g", condition=lambda features: features["key"] == 7)
    client.create_playlist(playlist_name="minor-songs", condition=lambda features: features["mode"] == 0)
