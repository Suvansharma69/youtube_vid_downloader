from pytube import YouTube
import os

def download_video(url, path='.'):
    try:
        yt = YouTube(url)
        print(f"\nTitle: {yt.title}")
        print(f"Author: {yt.author}")
        print(f"Length: {yt.length} seconds")
        print(f"Views: {yt.views}")

        stream = yt.streams.get_highest_resolution()
        print(f"Downloading: {stream.resolution} - {stream.mime_type}")
        stream.download(output_path=path)
        print("\nDownload complete!")
    except Exception as e:
        print(f"Error: {e}")

if _name_ == "_main_":
    url = input("Enter the YouTube video URL: ")
    path = input("Enter the download path (leave blank for current directory): ").strip()
    if path == '':
        path = '.'
    download_video(url, path)