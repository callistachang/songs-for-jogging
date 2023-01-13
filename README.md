# songs-for-jogging
Quick script that creates a Spotify playlist made from songs already in your other playlists, given some user condition (e.g. a desired BPM range) 

## Usage
Get your [Spotify client ID and client secret](https://developer.spotify.com/dashboard/login) and your [Spotify user id](https://www.bonjohh.com/how-to-get-my-spotify-user-id.html), create a new file `.env` based on `.env.example` and fill in values

## Motivation
I wanted a playlist of songs for jogging in the range of 82-85 BPM made of **songs I already knew**, i.e. songs I've included in other playlists I've made before. So here's an impulse script written at 5am by a very delirious and jetlagged individual, but it works! (hopefully)

TIL Spotify exposes every song's [audio features](https://developer.spotify.com/documentation/web-api/reference/#/operations/get-audio-features) via API, so for example one could set a threshold for how energetic they want their jogging playlist to be. The sky's the limit - you could make a playlist of just instrumental songs, or songs in the key of C, whatever tickles ur fancy

## Future Work
CLI interface and cleanup
