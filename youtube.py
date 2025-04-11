from pytube import Playlist

# Function to download a YouTube playlist
def download_playlist(url):
    try:
        # Create Playlist object
        playlist = Playlist(url)
        # Iterate through videos in the playlist
        for video in playlist.videos:
            # Download each video
            video.streams.first().download()
            print(f"Downloaded: {video.title}")
        print("Download completed successfully!")
    except Exception as e:
        print(f"An error occurred: {e}")

# Provide the URL of the YouTube playlist
playlist_url = input("Enter the URL of the YouTube playlist: ")

# Call the function to download the playlist
download_playlist(playlist_url)
