import tkinter as tk
from tkinter import messagebox, ttk, filedialog
from PIL import Image, ImageTk
import requests
from io import BytesIO
import yt_dlp
import os
import threading

ASSETS_DIR = "assets"
ICON_PATH = os.path.join(ASSETS_DIR, "youtube_icon.ico")
LOGO_PATH = os.path.join(ASSETS_DIR, "youtube_logo.png")
BG_PATH = os.path.join(ASSETS_DIR, "background.png")

download_format = "mp4"
download_folder = os.getcwd()

def fetch_video_info():
    url = url_entry.get()
    if not url:
        messagebox.showerror("Erreur", "Veuillez entrer une URL YouTube.")
        return

    try:
        with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
            info = ydl.extract_info(url, download=False)

        title_label.config(text=info['title'])
        author_label.config(text=f"Chaîne : {info['uploader']}")

        response = requests.get(info['thumbnail'])
        img_data = Image.open(BytesIO(response.content)).resize((320, 180))
        img = ImageTk.PhotoImage(img_data)
        thumbnail_label.config(image=img)
        thumbnail_label.image = img

        download_btn.config(state=tk.NORMAL)
        root.video_url = url

    except Exception as e:
        messagebox.showerror("Erreur", f"Impossible de récupérer les infos : {e}")


def start_download():
    threading.Thread(target=download_video).start()


def progress_hook(d):
    if d['status'] == 'downloading':
        total = d.get('total_bytes') or d.get('total_bytes_estimate')
        downloaded = d.get('downloaded_bytes', 0)
        if total:
            percent = downloaded / total * 100
            progress['value'] = percent
            progress.update_idletasks()


def download_video():
    url = root.video_url

    ydl_opts = {
        'outtmpl': os.path.join(download_folder, '%(title)s.%(ext)s'),
        'progress_hooks': [progress_hook],
        'quiet': True
    }

    if format_var.get() == "mp4":
        ydl_opts.update({
            'format': 'bestvideo+bestaudio/best',
            'merge_output_format': 'mp4'
        })
    else:
        ydl_opts.update({
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }]
        })

    try:
        download_btn.config(state=tk.DISABLED)
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        progress['value'] = 100
        messagebox.showinfo("Succès", "Téléchargement terminé !")
    except Exception as e:
        messagebox.showerror("Erreur", f"Erreur : {e}")
    finally:
        download_btn.config(state=tk.NORMAL)


def select_folder():
    global download_folder
    folder = filedialog.askdirectory()
    if folder:
        download_folder = folder
        folder_label.config(text=download_folder)

root = tk.Tk()
root.title("YouTube Downloader")
root.geometry("440x600")
root.resizable(False, False)

if os.path.exists(ICON_PATH):
    root.iconbitmap(ICON_PATH)

canvas = tk.Canvas(root, width=440, height=600, highlightthickness=0)
canvas.pack(fill="both", expand=True)

if os.path.exists(BG_PATH):
    bg_img = Image.open(BG_PATH).resize((440, 600))
    bg_tk = ImageTk.PhotoImage(bg_img)
    canvas.create_image(0, 0, image=bg_tk, anchor="nw")
else:
    canvas.create_rectangle(0, 0, 440, 600, fill="#f4f4f4")

if os.path.exists(LOGO_PATH):
    logo_img = Image.open(LOGO_PATH).resize((160, 55))
    logo_tk = ImageTk.PhotoImage(logo_img)
    canvas.create_image(220, 35, image=logo_tk, anchor="center")

url_entry = tk.Entry(root, font=("Segoe UI", 11), width=45)
canvas.create_window(220, 100, window=url_entry)

analyse_btn = tk.Button(
    root,
    text="Analyser la vidéo",
    font=("Segoe UI", 10, "bold"),
    bg="#ff0000", fg="white",
    activebackground="#cc0000",
    relief=tk.FLAT,
    cursor="hand2",
    command=fetch_video_info
)
canvas.create_window(220, 140, window=analyse_btn, width=180, height=35)

format_var = tk.StringVar(value="mp4")
format_frame = tk.Frame(root, bg="#f4f4f4")
tk.Radiobutton(format_frame, text="MP4", variable=format_var, value="mp4", bg="#f4f4f4").pack(side="left", padx=10)
tk.Radiobutton(format_frame, text="MP3", variable=format_var, value="mp3", bg="#f4f4f4").pack(side="left", padx=10)
canvas.create_window(220, 180, window=format_frame)

folder_btn = tk.Button(root, text="Choisir un dossier", command=select_folder, font=("Segoe UI", 9), cursor="hand2")
canvas.create_window(220, 215, window=folder_btn)

folder_label = tk.Label(root, text=download_folder, font=("Segoe UI", 8), wraplength=380, bg="#f4f4f4", fg="#666")
canvas.create_window(220, 245, window=folder_label)

thumbnail_label = tk.Label(root, bg="#f4f4f4")
canvas.create_window(220, 320, window=thumbnail_label)

title_label = tk.Label(root, text="", font=("Segoe UI", 10, "bold"), wraplength=360, bg="#f4f4f4")
canvas.create_window(220, 390, window=title_label)

author_label = tk.Label(root, text="", font=("Segoe UI", 9), bg="#f4f4f4")
canvas.create_window(220, 420, window=author_label)

progress = ttk.Progressbar(root, length=300, mode='determinate')
canvas.create_window(220, 460, window=progress)

download_btn = tk.Button(
    root,
    text="Télécharger la vidéo",
    state=tk.DISABLED,
    font=("Segoe UI", 10, "bold"),
    bg="#28a745", fg="white",
    activebackground="#218838",
    relief=tk.FLAT,
    cursor="hand2",
    command=start_download
)
canvas.create_window(220, 500, window=download_btn, width=200, height=40)

signature = tk.Label(
    root,
    text="YouTube Downloader - By Stylobow",
    font=("Segoe UI", 8),
    bg="#f4f4f4", fg="#777"
)
canvas.create_window(435, 590, anchor="se", window=signature)

root.mainloop()
