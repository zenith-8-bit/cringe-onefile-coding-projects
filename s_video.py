from pytube import YouTube
  
# Function to download a YouTube video
def download_video(url):
    try:
        # Create YouTube object
        video = YouTube(url)
        # Get the highest resolution stream
        stream = video.streams.get_highest_resolution()
        # Download the video
        stream.download()
        print("Download completed successfully!")
    except Exception as e:
        print(f"An error occurred: {e}")

# Provide the URL of the YouTube video
video_url = input("Enter the URL of the YouTube video: ")

# Call the function to download the video
download_video(video_url)
