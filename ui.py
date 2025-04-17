import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from main import download_video
import threading

class YouTubeDownloaderUI:
    def __init__(self, root):
        self.root = root
        self.root.title("YouTube Video Downloader")
        self.root.geometry("600x400")
        self.root.resizable(False, False)
        
        # Configure style
        self.style = ttk.Style()
        self.style.configure("TButton", padding=6, relief="flat", background="#2196F3")
        self.style.configure("TLabel", padding=6)
        self.style.configure("TEntry", padding=6)
        
        # Create main frame
        self.main_frame = ttk.Frame(root, padding="20")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # URL Entry
        self.url_label = ttk.Label(self.main_frame, text="YouTube URL:")
        self.url_label.pack(fill=tk.X, pady=(0, 5))
        
        self.url_entry = ttk.Entry(self.main_frame, width=50)
        self.url_entry.pack(fill=tk.X, pady=(0, 10))
        
        # Download Path
        self.path_frame = ttk.Frame(self.main_frame)
        self.path_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.path_label = ttk.Label(self.path_frame, text="Download Path:")
        self.path_label.pack(side=tk.LEFT, padx=(0, 10))
        
        self.path_var = tk.StringVar(value="Current Directory")
        self.path_display = ttk.Label(self.path_frame, textvariable=self.path_var)
        self.path_display.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.browse_button = ttk.Button(self.path_frame, text="Browse", command=self.browse_directory)
        self.browse_button.pack(side=tk.RIGHT)
        
        # Progress Bar
        self.progress = ttk.Progressbar(self.main_frame, orient=tk.HORIZONTAL, length=100, mode='determinate')
        self.progress.pack(fill=tk.X, pady=(0, 10))
        
        # Status Label
        self.status_var = tk.StringVar(value="Ready to download")
        self.status_label = ttk.Label(self.main_frame, textvariable=self.status_var)
        self.status_label.pack(fill=tk.X, pady=(0, 10))
        
        # Download Button
        self.download_button = ttk.Button(self.main_frame, text="Download", command=self.start_download)
        self.download_button.pack(fill=tk.X)
        
        # Set initial state
        self.download_path = "."
        
    def browse_directory(self):
        directory = filedialog.askdirectory()
        if directory:
            self.download_path = directory
            self.path_var.set(directory)
    
    def start_download(self):
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showerror("Error", "Please enter a YouTube URL")
            return
            
        self.download_button.config(state=tk.DISABLED)
        self.status_var.set("Downloading...")
        self.progress.start()
        
        # Start download in a separate thread
        thread = threading.Thread(target=self.download_thread, args=(url,))
        thread.start()
    
    def download_thread(self, url):
        try:
            download_video(url, self.download_path)
            self.root.after(0, self.download_complete, True)
        except Exception as e:
            self.root.after(0, self.download_complete, False, str(e))
    
    def download_complete(self, success, error_message=None):
        self.progress.stop()
        self.download_button.config(state=tk.NORMAL)
        
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