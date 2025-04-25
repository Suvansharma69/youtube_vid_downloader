import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from main import download_video
import threading
from pytube import YouTube
import json
import os
from datetime import datetime

class YouTubeDownloaderUI:
    def __init__(self, root):
        self.root = root
        self.root.title("YouTube Video Downloader")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        # Configure style
        self.style = ttk.Style()
        self.style.configure("TButton", padding=6, relief="flat", background="#2196F3")
        self.style.configure("TLabel", padding=6)
        self.style.configure("TEntry", padding=6)
        
        # Create main frame with scrollbar
        self.main_canvas = tk.Canvas(root)
        self.scrollbar = ttk.Scrollbar(root, orient="vertical", command=self.main_canvas.yview)
        self.main_frame = ttk.Frame(self.main_canvas, padding="20")
        
        self.main_canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.scrollbar.pack(side="right", fill="y")
        self.main_canvas.pack(side="left", fill="both", expand=True)
        
        self.canvas_frame = self.main_canvas.create_window((0, 0), window=self.main_frame, anchor="nw")
        
        # URL Entry with Preview Button
        self.url_frame = ttk.Frame(self.main_frame)
        self.url_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.url_label = ttk.Label(self.url_frame, text="YouTube URL:")
        self.url_label.pack(side=tk.LEFT, padx=(0, 10))
        
        self.url_entry = ttk.Entry(self.url_frame, width=50)
        self.url_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        self.preview_button = ttk.Button(self.url_frame, text="Preview", command=self.preview_video)
        self.preview_button.pack(side=tk.RIGHT)
        
        # Video Info Frame
        self.info_frame = ttk.LabelFrame(self.main_frame, text="Video Information", padding="10")
        self.info_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.info_text = tk.Text(self.info_frame, height=4, wrap=tk.WORD, state='disabled')
        self.info_text.pack(fill=tk.X)
        
        # Quality Selection
        self.quality_frame = ttk.LabelFrame(self.main_frame, text="Video Quality", padding="10")
        self.quality_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.quality_var = tk.StringVar(value="highest")
        self.quality_combo = ttk.Combobox(self.quality_frame, textvariable=self.quality_var, state="readonly")
        self.quality_combo['values'] = ('highest', '720p', '480p', '360p')
        self.quality_combo.pack(fill=tk.X)
        
        # Download Path
        self.path_frame = ttk.LabelFrame(self.main_frame, text="Download Location", padding="10")
        self.path_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.path_var = tk.StringVar(value="Current Directory")
        self.path_display = ttk.Label(self.path_frame, textvariable=self.path_var)
        self.path_display.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        self.browse_button = ttk.Button(self.path_frame, text="Browse", command=self.browse_directory)
        self.browse_button.pack(side=tk.RIGHT)
        
        # Progress Frame
        self.progress_frame = ttk.LabelFrame(self.main_frame, text="Download Progress", padding="10")
        self.progress_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.progress = ttk.Progressbar(self.progress_frame, orient=tk.HORIZONTAL, length=100, mode='determinate')
        self.progress.pack(fill=tk.X, pady=(0, 5))
        
        self.progress_label = ttk.Label(self.progress_frame, text="0%")
        self.progress_label.pack(fill=tk.X)
        
        # Status Label
        self.status_var = tk.StringVar(value="Ready to download")
        self.status_label = ttk.Label(self.main_frame, textvariable=self.status_var)
        self.status_label.pack(fill=tk.X, pady=(0, 10))
        
        # Buttons Frame
        self.buttons_frame = ttk.Frame(self.main_frame)
        self.buttons_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.download_button = ttk.Button(self.buttons_frame, text="Download", command=self.start_download)
        self.download_button.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        self.clear_button = ttk.Button(self.buttons_frame, text="Clear", command=self.clear_form)
        self.clear_button.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))
        
        # History Frame
        self.history_frame = ttk.LabelFrame(self.main_frame, text="Download History", padding="10")
        self.history_frame.pack(fill=tk.BOTH, expand=True)
        
        self.history_text = tk.Text(self.history_frame, height=6, wrap=tk.WORD, state='disabled')
        self.history_text.pack(fill=tk.BOTH, expand=True)
        
        # Set initial state
        self.download_path = "."
        self.current_video = None
        self.load_history()
        
        # Configure canvas scrolling
        self.main_frame.bind("<Configure>", self.on_frame_configure)
        self.main_canvas.bind("<Configure>", self.on_canvas_configure)
        
    def on_frame_configure(self, event=None):
        self.main_canvas.configure(scrollregion=self.main_canvas.bbox("all"))
        
    def on_canvas_configure(self, event):
        width = event.width
        self.main_canvas.itemconfig(self.canvas_frame, width=width)
        
    def load_history(self):
        try:
            if os.path.exists('download_history.json'):
                with open('download_history.json', 'r') as f:
                    history = json.load(f)
                    self.history_text.config(state='normal')
                    self.history_text.delete(1.0, tk.END)
                    for entry in history[-10:]:  # Show last 10 downloads
                        self.history_text.insert(tk.END, f"{entry['date']} - {entry['title']}\n")
                    self.history_text.config(state='disabled')
        except Exception as e:
            print(f"Error loading history: {e}")
            
    def save_to_history(self, title):
        try:
            history = []
            if os.path.exists('download_history.json'):
                with open('download_history.json', 'r') as f:
                    history = json.load(f)
            
            history.append({
                'date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'title': title
            })
            
            with open('download_history.json', 'w') as f:
                json.dump(history[-50:], f)  # Keep last 50 downloads
                
            self.load_history()
        except Exception as e:
            print(f"Error saving history: {e}")
            
    def preview_video(self):
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showerror("Error", "Please enter a YouTube URL")
            return
            
        try:
            self.current_video = YouTube(url)
            self.info_text.config(state='normal')
            self.info_text.delete(1.0, tk.END)
            self.info_text.insert(tk.END, f"Title: {self.current_video.title}\n")
            self.info_text.insert(tk.END, f"Author: {self.current_video.author}\n")
            self.info_text.insert(tk.END, f"Length: {self.current_video.length} seconds\n")
            self.info_text.insert(tk.END, f"Views: {self.current_video.views:,}")
            self.info_text.config(state='disabled')
            
            # Update quality options based on available streams
            streams = self.current_video.streams.filter(progressive=True)
            qualities = ['highest'] + [f"{s.resolution}" for s in streams if s.resolution]
            self.quality_combo['values'] = qualities
            
            self.status_var.set("Video information loaded successfully")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load video information: {str(e)}")
            self.status_var.set("Failed to load video information")
            
    def browse_directory(self):
        directory = filedialog.askdirectory()
        if directory:
            self.download_path = directory
            self.path_var.set(directory)
            
    def clear_form(self):
        self.url_entry.delete(0, tk.END)
        self.info_text.config(state='normal')
        self.info_text.delete(1.0, tk.END)
        self.info_text.config(state='disabled')
        self.quality_var.set('highest')
        self.path_var.set("Current Directory")
        self.download_path = "."
        self.progress['value'] = 0
        self.progress_label.config(text="0%")
        self.status_var.set("Ready to download")
        self.current_video = None
        
    def update_progress(self, stream, chunk, bytes_remaining):
        total_size = stream.filesize
        bytes_downloaded = total_size - bytes_remaining
        percentage = (bytes_downloaded / total_size) * 100
        self.progress['value'] = percentage
        self.progress_label.config(text=f"{percentage:.1f}%")
        self.root.update_idletasks()
        
    def start_download(self):
        if not self.current_video:
            messagebox.showerror("Error", "Please preview the video first")
            return
            
        self.download_button.config(state=tk.DISABLED)
        self.preview_button.config(state=tk.DISABLED)
        self.status_var.set("Downloading...")
        
        # Start download in a separate thread
        thread = threading.Thread(target=self.download_thread)
        thread.start()
        
    def download_thread(self):
        try:
            quality = self.quality_var.get()
            if quality == 'highest':
                stream = self.current_video.streams.get_highest_resolution()
            else:
                stream = self.current_video.streams.filter(res=quality).first()
                
            if not stream:
                raise Exception(f"No stream available for quality: {quality}")
                
            stream.download(output_path=self.download_path, on_progress_callback=self.update_progress)
            self.root.after(0, self.download_complete, True)
            self.save_to_history(self.current_video.title)
        except Exception as e:
            self.root.after(0, self.download_complete, False, str(e))
            
    def download_complete(self, success, error_message=None):
        self.download_button.config(state=tk.NORMAL)
        self.preview_button.config(state=tk.NORMAL)
        
        if success:
            self.status_var.set("Download completed successfully!")
            messagebox.showinfo("Success", "Video downloaded successfully!")
        else:
            self.status_var.set(f"Download failed: {error_message}")
            messagebox.showerror("Error", f"Download failed: {error_message}")

if __name__ == "__main__":
    root = tk.Tk()
    app = YouTubeDownloaderUI(root)
    root.mainloop() 