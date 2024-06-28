from dotenv import load_dotenv
import os
import base64
from requests import post, get
import json
import csv

load_dotenv()

client_id = os.getenv("CLIENT_ID")

client_secret = os.getenv("CLIENT_SECRET")


def get_token():
    auth_string = client_id + ":" + client_secret
    auth_bytes = auth_string.encode("utf-8")
    auth_base64 = str(base64.b64encode(auth_bytes), "utf-8")
    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": "Basic " + auth_base64,
        "Content-Type" : "application/x-www-form-urlencoded"
    }
    data = {"grant_type":"client_credentials"}
    result = post(url,headers = headers,data = data)
    json_result = json.loads(result.content)
    token = json_result["access_token"]
    return token

def get_auth_header(token):
    return {"Authorization": "Bearer " + token}

def search_for_tracks(token,track):
    url = "https://api.spotify.com/v1/search"
    headers = get_auth_header(token)
    query = f"?q={track}&type=track&limit=1"
    query_url = url+query
    result = get(query_url,headers = headers)
    json_result = json.loads(result.content)
    print(json_result)


def get_track(token,spotid):
    url = f"https://api.spotify.com/v1/tracks/{spotid}"
    headers = get_auth_header(token)
    result = get(url,headers = headers)
    json_result = json.loads(result.content)
    print(json_result)

def get_trackv2(token, spotid):
    url = f"https://api.spotify.com/v1/tracks/{spotid}"
    headers = get_auth_header(token)
    response = get(url, headers=headers)
    
    if response.status_code == 200:
        json_result = response.json()
        
        # Extract specific information
        track_info = {
            "track_name": json_result["name"],
            "album_name": json_result["album"]["name"],
            "artist_name": json_result["artists"][0]["name"],
            "release_date": json_result["album"]["release_date"],
            "duration_ms": json_result["duration_ms"],
            "popularity": json_result["popularity"],
            "external_url": json_result["external_urls"]["spotify"]
        }
        
        print(json.dumps(track_info, indent=4))
        return track_info
    else:
        print(f"Error: {response.status_code}")
        return None


def get_trackv3(token, spotid):
    url = f"https://api.spotify.com/v1/tracks/{spotid}"
    headers = get_auth_header(token)
    response = get(url, headers=headers)
    
    if response.status_code == 200:
        track_json = response.json()
        
        # Extract artist ID to get genre information
        artist_id = track_json["artists"][0]["id"]
        artist_url = f"https://api.spotify.com/v1/artists/{artist_id}"
        artist_response = get(artist_url, headers=headers)
        
        if artist_response.status_code == 200:
            artist_json = artist_response.json()
            genres = artist_json.get("genres", [])
            
            # Extract detailed track, album, and artist information
            track_info = {
                "track_name": track_json["name"],
                "track_id": track_json["id"],
                "track_number": track_json["track_number"],
                "disc_number": track_json["disc_number"],
                "duration_ms": track_json["duration_ms"],
                "explicit": track_json["explicit"],
                "popularity": track_json["popularity"],
                "preview_url": track_json["preview_url"],
                "isrc": track_json["external_ids"].get("isrc"),
                "album_name": track_json["album"]["name"],
                "album_id": track_json["album"]["id"],
                "album_type": track_json["album"]["album_type"],
                "album_total_tracks": track_json["album"]["total_tracks"],
                "album_release_date": track_json["album"]["release_date"],
                "album_release_date_precision": track_json["album"]["release_date_precision"],
                "album_images": track_json["album"]["images"],
                #"available_markets": track_json["available_markets"],
                "artist_name": track_json["artists"][0]["name"],
                "artist_id": track_json["artists"][0]["id"],
                "artist_genres": genres,
                "artist_popularity": artist_json["popularity"],
                "artist_followers": artist_json["followers"]["total"],
                "external_url": track_json["external_urls"]["spotify"]
            }
            
            # Print the extracted track information
            print(json.dumps(track_info, indent=4))
            
            return track_info
        else:
            print(f"Error fetching artist info: {artist_response.status_code}")
            return None
    else:
        print(f"Error fetching track info: {response.status_code}")
        return None



def fetch_lyrics_from_musixmatch(track_name, artist_name, musixmatch_api_key):
    base_url = "https://api.musixmatch.com/ws/1.1/matcher.lyrics.get"
    params = {
        "apikey": musixmatch_api_key,
        "q_track": track_name,
        "q_artist": artist_name
    }
    
    try:
        response = get(base_url, params=params)
        if response.status_code == 200:
            lyrics_data = response.json()
            if lyrics_data["message"]["body"]:
                lyrics = lyrics_data["message"]["body"]["lyrics"]["lyrics_body"]
                # Clean up the lyrics (Musixmatch includes identifier at the end)
                lyrics_clean = lyrics.split("...\n")[0]
                return lyrics_clean
            else:
                print(f"No lyrics found for {artist_name} - {track_name}")
                return None
        else:
            print(f"Failed to fetch lyrics, status code: {response.status_code}")
            return None
    except Exception as e:
        print(f"Exception occurred while fetching lyrics: {str(e)}")
        return None
    
#working for metadata at least    
'''
# Function to get track information including lyrics
def get_trackv4(token, spotid, musixmatch_api_key):
    url = f"https://api.spotify.com/v1/tracks/{spotid}"
    headers = get_auth_header(token)
    response = get(url, headers=headers)
    
    if response.status_code == 200:
        track_json = response.json()
        
        # Extract artist ID to get genre information
        artist_id = track_json["artists"][0]["id"]
        artist_url = f"https://api.spotify.com/v1/artists/{artist_id}"
        artist_response = get(artist_url, headers=headers)
        
        if artist_response.status_code == 200:
            artist_json = artist_response.json()
            genres = artist_json.get("genres", [])
            
            # Fetch lyrics from Musixmatch using track name from Spotify
            lyrics = fetch_lyrics_from_musixmatch(track_json["name"], track_json["artists"][0]["name"], musixmatch_api_key)
            
            # Extract detailed track, album, and artist information
            track_info = {
                "track_name": track_json["name"],
                "track_id": track_json["id"],
                "track_number": track_json["track_number"],
                "disc_number": track_json["disc_number"],
                "duration_ms": track_json["duration_ms"],
                "explicit": track_json["explicit"],
                "popularity": track_json["popularity"],
                "preview_url": track_json["preview_url"],
                "isrc": track_json["external_ids"].get("isrc"),
                "album_name": track_json["album"]["name"],
                "album_id": track_json["album"]["id"],
                "album_type": track_json["album"]["album_type"],
                "album_total_tracks": track_json["album"]["total_tracks"],
                "album_release_date": track_json["album"]["release_date"],
                "album_release_date_precision": track_json["album"]["release_date_precision"],
                "album_images": track_json["album"]["images"],
                "artist_name": track_json["artists"][0]["name"],
                "artist_id": track_json["artists"][0]["id"],
                "artist_genres": genres,
                "artist_popularity": artist_json["popularity"],
                "artist_followers": artist_json["followers"]["total"],
                "external_url": track_json["external_urls"]["spotify"],
                "lyrics": lyrics  # Add lyrics to track_info
            }
            
            # Print the extracted track information
            print(json.dumps(track_info, indent=4))
            
            return track_info
        else:
            print(f"Error fetching artist info: {artist_response.status_code}")
            return None
    else:
        print(f"Error fetching track info: {response.status_code}")
        return None


def fetch_and_save_track_data_to_csv(token, track_ids, musixmatch_api_key, output_file):
    headers = [
        "track_name", "track_id", "track_number", "disc_number", "duration_ms",
        "explicit", "popularity", "preview_url", "isrc", "album_name", "album_id",
        "album_type", "album_total_tracks", "album_release_date", "album_release_date_precision",
        "album_images", "artist_name", "artist_id", "artist_genres", "artist_popularity",
        "artist_followers", "external_url", "lyrics"
    ]
    
    with open(output_file, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=headers)
        writer.writeheader()
        
        for track_id in track_ids:
            track_info = get_trackv4(token, track_id, musixmatch_api_key)
            if track_info:
                writer.writerow(track_info)

'''

'''
#trying for acoustic features

def get_trackv4(token, spotid, musixmatch_api_key):
    track_url = f"https://api.spotify.com/v1/tracks/{spotid}"
    audio_features_url = f"https://api.spotify.com/v1/audio-features/{spotid}"
    #audio_analysis_url = f"https://api.spotify.com/v1/audio-analysis/{spotid}"
    
    headers = get_auth_header(token)
    
    track_response = get(track_url, headers=headers)
    audio_features_response = get(audio_features_url, headers=headers)
    #audio_analysis_response = get(audio_analysis_url, headers=headers)
    
    if track_response.status_code == 200 and audio_features_response.status_code == 200:
        track_json = track_response.json()
        audio_features_json = audio_features_response.json()
        #audio_analysis_json = audio_analysis_response.json()
        
        # Extract artist ID to get genre information
        artist_id = track_json["artists"][0]["id"]
        artist_url = f"https://api.spotify.com/v1/artists/{artist_id}"
        artist_response = get(artist_url, headers=headers)
        
        if artist_response.status_code == 200:
            artist_json = artist_response.json()
            genres = artist_json.get("genres", [])
            
            # Fetch lyrics from Musixmatch using track name from Spotify
            lyrics = fetch_lyrics_from_musixmatch(track_json["name"], track_json["artists"][0]["name"], musixmatch_api_key)
            
            # Extract detailed track, album, and artist information
            track_info = {
                "track_name": track_json["name"],
                "track_id": track_json["id"],
                "track_number": track_json["track_number"],
                "disc_number": track_json["disc_number"],
                "duration_ms": track_json["duration_ms"],
                "explicit": track_json["explicit"],
                "popularity": track_json["popularity"],
                "preview_url": track_json["preview_url"],
                "isrc": track_json["external_ids"].get("isrc"),
                "album_name": track_json["album"]["name"],
                "album_id": track_json["album"]["id"],
                "album_type": track_json["album"]["album_type"],
                "album_total_tracks": track_json["album"]["total_tracks"],
                "album_release_date": track_json["album"]["release_date"],
                "album_release_date_precision": track_json["album"]["release_date_precision"],
                "album_images": track_json["album"]["images"],
                "artist_name": track_json["artists"][0]["name"],
                "artist_id": track_json["artists"][0]["id"],
                "artist_genres": genres,
                "artist_popularity": artist_json["popularity"],
                "artist_followers": artist_json["followers"]["total"],
                "external_url": track_json["external_urls"]["spotify"],
                "acousticness": audio_features_json["acousticness"],
                #"analysis_url": audio_features_json["analysis_url"],
                "danceability": audio_features_json["danceability"],
                "energy": audio_features_json["energy"],
                "instrumentalness": audio_features_json["instrumentalness"],
                "key": audio_features_json["key"],
                "liveness": audio_features_json["liveness"],
                "loudness": audio_features_json["loudness"],
                "mode": audio_features_json["mode"],
                "speechiness": audio_features_json["speechiness"],
                "tempo": audio_features_json["tempo"],
                "time_signature": audio_features_json["time_signature"],
                "valence": audio_features_json["valence"],
                "lyrics": lyrics  # Add lyrics to track_info
            }
            
            # Print the extracted track information
            print(json.dumps(track_info, indent=4))
            
            return track_info
        else:
            print(f"Error fetching artist info: {artist_response.status_code}")
            return None
    else:
        print(f"Error fetching track info: {track_response.status_code}")
        print(f"Error fetching audio features: {audio_features_response.status_code}")
        #print(f"Error fetching audio analysis: {audio_analysis_response.status_code}")
        return None

# Function to fetch and save track data to CSV
def fetch_and_save_track_data_to_csv(token, track_ids, musixmatch_api_key, output_file):
    headers = [
        "track_name", "track_id", "track_number", "disc_number", "duration_ms",
        "explicit", "popularity", "preview_url", "isrc", "album_name", "album_id",
        "album_type", "album_total_tracks", "album_release_date", "album_release_date_precision",
        "album_images", "artist_name", "artist_id", "artist_genres", "artist_popularity",
        "artist_followers", "external_url", "acousticness", "analysis_url", "danceability",
        "energy", "instrumentalness", "key", "liveness", "loudness", "mode", "speechiness",
        "tempo", "time_signature", "valence", "lyrics"
    ]
    
    with open(output_file, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=headers)
        writer.writeheader()
        
        for track_id in track_ids:
            track_info = get_trackv4(token, track_id, musixmatch_api_key)
            if track_info:
                writer.writerow(track_info)


'''











def get_track_info(track_json, audio_features_json, musixmatch_api_key, token):
    artist_infos = []
    artist_genres = []
    artist_popularities = []
    artist_followers = []

    for artist in track_json["artists"]:
        artist_id = artist["id"]
        artist_url = f"https://api.spotify.com/v1/artists/{artist_id}"
        artist_response = get(artist_url, headers=get_auth_header(token))

        if artist_response.ok:
            artist_json = artist_response.json()
            artist_infos.append({
                "name": artist["name"],
                "id": artist["id"],
                "genres": artist_json.get("genres", []),
                "popularity": artist_json["popularity"],
                "followers": artist_json["followers"]["total"]
            })
            artist_genres.extend(artist_json.get("genres", []))
            artist_popularities.append(artist_json["popularity"])
            artist_followers.append(artist_json["followers"]["total"])

    # Find the most popular artist
    most_popular_artist = max(artist_infos, key=lambda x: x["popularity"])

    # Fetch lyrics from Musixmatch using track name and most popular artist's name
    lyrics = fetch_lyrics_from_musixmatch(track_json["name"], most_popular_artist["name"], musixmatch_api_key)

    # Extract detailed track, album, and artist information
    track_info = {
        "track_name": track_json["name"],
        "track_id": track_json["id"],
        "track_number": track_json["track_number"],
        "disc_number": track_json["disc_number"],
        "duration_ms": track_json["duration_ms"],
        "explicit": track_json["explicit"],
        "popularity": track_json["popularity"],
        "preview_url": track_json["preview_url"],
        "isrc": track_json["external_ids"].get("isrc"),
        "album_name": track_json["album"]["name"],
        "album_id": track_json["album"]["id"],
        "album_type": track_json["album"]["album_type"],
        "album_total_tracks": track_json["album"]["total_tracks"],
        "album_release_date": track_json["album"]["release_date"],
        "album_release_date_precision": track_json["album"]["release_date_precision"],
        "album_images": track_json["album"]["images"],
        "popular_artist": most_popular_artist["name"],
        "popular_artist_id": most_popular_artist["id"],
        "artist_names": [artist["name"] for artist in track_json["artists"]],
        "artist_ids": [artist["id"] for artist in track_json["artists"]],
        "combined_genres": list(set(artist_genres)),
        "artist_popularity": most_popular_artist["popularity"],
        "artist_followers": most_popular_artist["followers"],
        "external_url": track_json["external_urls"]["spotify"],
        "acousticness": audio_features_json["acousticness"],
        "danceability": audio_features_json["danceability"],
        "energy": audio_features_json["energy"],
        "instrumentalness": audio_features_json["instrumentalness"],
        "key": audio_features_json["key"],
        "liveness": audio_features_json["liveness"],
        "loudness": audio_features_json["loudness"],
        "mode": audio_features_json["mode"],
        "speechiness": audio_features_json["speechiness"],
        "tempo": audio_features_json["tempo"],
        "time_signature": audio_features_json["time_signature"],
        "valence": audio_features_json["valence"],
        "lyrics": lyrics  # Add lyrics to track_info
    }

    return track_info

def fetch_and_save_track_data_to_csv(token, track_ids, musixmatch_api_key, output_file):
    headers = [
        "track_name", "track_id", "track_number", "disc_number", "duration_ms",
        "explicit", "popularity", "preview_url", "isrc", "album_name", "album_id",
        "album_type", "album_total_tracks", "album_release_date", "album_release_date_precision",
        "album_images", "popular_artist", "popular_artist_id", "artist_names", "artist_ids", "combined_genres",
        "artist_popularity", "artist_followers", "external_url", "acousticness", "danceability",
        "energy", "instrumentalness", "key", "liveness", "loudness", "mode", "speechiness",
        "tempo", "time_signature", "valence", "lyrics"
    ]
    
    with open(output_file, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=headers)
        writer.writeheader()

        for i in range(0, len(track_ids), 50):
            batch_ids = track_ids[i:i+50]
            track_url = f"https://api.spotify.com/v1/tracks?ids={','.join(batch_ids)}"
            audio_features_url = f"https://api.spotify.com/v1/audio-features?ids={','.join(batch_ids)}"
            
            track_response = get(track_url, headers=get_auth_header(token))
            audio_features_response = get(audio_features_url, headers=get_auth_header(token))
            
            if track_response.ok and audio_features_response.ok:
                track_json = track_response.json()["tracks"]
                audio_features_json = {af["id"]: af for af in audio_features_response.json()["audio_features"]}
                
                for track in track_json:
                    track_info = get_track_info(track, audio_features_json[track["id"]], musixmatch_api_key, token)
                    if track_info:
                        writer.writerow(track_info)
            else:
                if not track_response.ok:
                    print(f"Error fetching track info: {track_response.status_code}")
                if not audio_features_response.ok:
                    print(f"Error fetching audio features: {audio_features_response.status_code}")










token = get_token()


#search_for_tracks(token, "Lady Killer")
#get_trackv3(token,"6REbwUNlppTfcnV4d4ZoZi")

# Example usage

musixmatch_api_key = "b2e75cde0b484648fb6fdc386bf38718"
track_id = "7qiZfU4dY1lWllzX7mPBI3"

#get_trackv4(token, track_id, musixmatch_api_key)

output_file = "spotify_tracks_data.csv"

track_ids = ["7qiZfU4dY1lWllzX7mPBI3","1xUddpWyEuYl5T3mduKnOJ","1u8c2t2Cy7UBoG4ArRcF5g","5cF0dROlMOK5uNZtivgu50","1XGmzt0PVuFgQYYnV2It7A"]

fetch_and_save_track_data_to_csv(token, track_ids, musixmatch_api_key, output_file)

print(f"Data saved to {output_file}")