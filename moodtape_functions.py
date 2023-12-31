import spotipy
# import spotipy.util as util

import random




def authenticate_spotify(token):
	print('...connecting to Spotify')
	sp = spotipy.Spotify(auth=token)
	return sp

#Step 2. Creating a list of your favorite artists

def aggregate_top_artists(sp):
	print('...getting your top artists')
	top_artists_name = []
	top_artists_uri = []

	ranges = ['short_term', 'medium_term', 'long_term']
	for r in ranges:
		top_artists_all_data = sp.current_user_top_artists(limit=50, time_range= r)
		top_artists_data = top_artists_all_data['items']
		for artist_data in top_artists_data:
			if artist_data["name"] not in top_artists_name:		
				top_artists_name.append(artist_data['name'])
				top_artists_uri.append(artist_data['uri'])

	followed_artists_all_data = sp.current_user_followed_artists(limit=50)
	followed_artists_data = (followed_artists_all_data['artists'])
	for artist_data in followed_artists_data["items"]:
		if artist_data["name"] not in top_artists_name:
			top_artists_name.append(artist_data['name'])
			top_artists_uri.append(artist_data['uri'])
	return top_artists_uri


#Step 3. For each of the artists, get a set of tracks for each artist

def aggregate_top_tracks(sp, top_artists_uri):
	print("...getting top tracks")
	top_tracks_uri = []
	for artist in top_artists_uri:
		top_tracks_all_data = sp.artist_top_tracks(artist)
		top_tracks_data = top_tracks_all_data['tracks']
		for track_data in top_tracks_data:
			top_tracks_uri.append(track_data['uri'])
	return top_tracks_uri

# Step 4. From top tracks, select tracks that are within a certain mood1 range

def select_tracks(sp, top_tracks_uri, mood1):
	from app import mood1

	
	print("...selecting tracks")
	selected_tracks_uri = []

	def group(seq, size):
		return (seq[pos:pos + size] for pos in range(0, len(seq), size))

	random.shuffle(top_tracks_uri)
	for tracks in list(group(top_tracks_uri, 50)):
		tracks_all_data = sp.audio_features(tracks)
		for track_data in tracks_all_data:
			try:
				if mood1 < 0.10:
					if (0 <= track_data["valence"] <= (mood1 + 0.15)
					and track_data["danceability"] <= (mood1*8)
					and track_data["energy"] <= (mood1*10)):
						selected_tracks_uri.append(track_data["uri"])					
				elif 0.10 <= mood1 < 0.25:						
					if ((mood1 - 0.075) <= track_data["valence"] <= (mood1 + 0.075)
					and track_data["danceability"] <= (mood1*4)
					and track_data["energy"] <= (mood1*5)):
						selected_tracks_uri.append(track_data["uri"])
				elif 0.25 <= mood1 < 0.50:											
					if ((mood1 - 0.085) <= track_data["valence"] <= (mood1 + 0.085)
					and track_data["danceability"] <= (mood1*3)
					and track_data["energy"] <= (mood1*3.5)):
						selected_tracks_uri.append(track_data["uri"])
				elif 0.50 <= mood1 < 0.75:						
					if ((mood1 - 0.075) <= track_data["valence"] <= (mood1 + 0.075)
					and track_data["danceability"] >= (mood1/2.5)
					and track_data["energy"] >= (mood1/2)):
						selected_tracks_uri.append(track_data["uri"])
				elif 0.75 <= mood1 < 0.90:						
					if ((mood1 - 0.075) <= track_data["valence"] <= (mood1 + 0.075)
					and track_data["danceability"] >= (mood1/2)
					and track_data["energy"] >= (mood1/1.75)):
						selected_tracks_uri.append(track_data["uri"])
				elif mood1 >= 0.90:
					if ((mood1 - 0.15) <= track_data["valence"] <= 1
					and track_data["danceability"] >= (mood1/1.75)
					and track_data["energy"] >= (mood1/1.5)):
						selected_tracks_uri.append(track_data["uri"])
			except TypeError as te:
				continue
	return selected_tracks_uri			

# Step 5. From these tracks, create a playlist for user

def create_playlist(sp, selected_tracks_uri, mood1):
	from app import emotion,emoji


	print("...creating playlist")
	user_all_data = sp.current_user()
	user_id = user_all_data["id"]

	playlist_all_data = sp.user_playlist_create(user_id, "EmoTunes " + str(emotion).capitalize() + emoji)
	playlist_id = playlist_all_data["id"]
	playlist_uri = playlist_all_data["uri"]

	random.shuffle(selected_tracks_uri)
	# try:
	sp.user_playlist_add_tracks(user_id, playlist_id, selected_tracks_uri[0:30])
	# except spotipy.client.SpotifyException as s:
	# 	print("could not add tracks")

	return playlist_uri

# spotify_auth = authenticate_spotify()
# top_artists = aggregate_top_artists(spotify_auth)
# top_tracks = aggregate_top_tracks(spotify_auth, top_artists)
# selected_tracks = select_tracks(spotify_auth, top_tracks)
# create_playlist(spotify_auth, selected_tracks)