# songs-for-running
quick and dirty script that creates a Spotify playlist made from songs already in your other playlists, given some user condition (e.g. a desired BPM range)

## Motivation
I wanted a playlist of songs for jogging in the range of 82-85 BPM made of **songs I already knew**, i.e. songs I've included in other playlists I've made. So here it is - impulsive, horrible code written at 5am by a very jetlagged individual, but it works! (hopefully)

TIL Spotify exposes every song's [audio features](https://developer.spotify.com/documentation/web-api/reference/#/operations/get-audio-features) via API, E.g. It's possible to set a condition for how energetic you want your playlist to be, I could set a threshold of energy > 0.5 for my jogging playlist. The sky's the limit! You could make a playlist of just instrumental songs, or songs in the key of C, whatever tickles ur fancy

## Future Work

probably an actual CLI interface
