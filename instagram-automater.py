from instagrapi import Client
import os
import json
import tempfile
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
from functools import lru_cache
import time

SESSION_DIR = os.path.join(tempfile.gettempdir(), "InstagramUploader by @marpace1 on yt")
os.makedirs(SESSION_DIR, exist_ok=True)

@lru_cache(maxsize=128)
def get_session_file(username):
    return os.path.join(SESSION_DIR, f"{username}.json")

def save_session(cl, username):
    with open(get_session_file(username), "w") as f:
        json.dump(cl.get_settings(), f)

def load_session(cl, username):
    session_file = get_session_file(username)
    if os.path.exists(session_file):
        with open(session_file, "r") as f:
            cl.set_settings(json.load(f))
        return True
    return False

def prompt_for_password():
    dialog = tk.Toplevel(root)
    dialog.title("Enter Password")
    dialog.geometry("300x150")
    dialog.configure(bg="#f0f0f0")

    tk.Label(dialog, text=f"Enter password for '{username}':", bg="#f0f0f0").pack(pady=10)
    password_entry = tk.Entry(dialog, show="*", width=30)
    password_entry.pack(pady=5)

    password_var = tk.StringVar()
    def on_ok():
        password_var.set(password_entry.get().strip())
        dialog.destroy()

    tk.Button(dialog, text="OK", command=on_ok, bg="#4CAF50", fg="white").pack(pady=10)
    dialog.grab_set()
    dialog.wait_window()
    return password_var.get()

def animate_loading(canvas, stop_flag, operation_type, total_files=1, current_file=1):
    angle = 0
    while not stop_flag():
        canvas.delete("loading")
        canvas.create_arc(10, 10, 50, 50, start=angle, extent=270, fill="blue", outline="blue", tags="loading")
        canvas.create_text(30, 30, text=f"{operation_type.capitalize()} {current_file}/{total_files}...", fill="white", font=("Arial", 8))
        angle = (angle + 10) % 360
        root.update()
        time.sleep(0.05)
    canvas.delete("loading")
    if operation_type == "login":
        canvas.create_text(30, 30, text="Login Complete!", fill="green", font=("Arial", 10))
    elif operation_type == "upload":
        canvas.create_text(30, 30, text="Upload Complete!", fill="green", font=("Arial", 10))
    root.after(1000, lambda: canvas.delete("all"))

def check_existing_session(login_status_canvas, login_button):
    global cl, username
    session_files = [f for f in os.listdir(SESSION_DIR) if f.endswith(".json")]
    if not session_files:
        return False

    username = session_files[0].replace(".json", "")
    use_saved = messagebox.askyesno("Session Found", f"A saved session for '{username}' exists. Use it?")
    if not use_saved:
        return False

    cl = Client()
    try:
        load_session(cl, username)
        password = prompt_for_password()
        if not password:
            messagebox.showerror("Error", "Password is required to reuse the session.")
            return False

        login_status_canvas.pack(pady=5)
        login_button.config(state="disabled")
        stop_animation = False
        def stop_flag(): return stop_animation
        threading.Thread(target=animate_loading, args=(login_status_canvas, stop_flag, "login"), daemon=True).start()

        cl.login(username, password, relogin=True)
        stop_animation = True
        messagebox.showinfo("Success", "Logged in using saved session.")
        show_upload_frame()
        return True
    except Exception as e:
        stop_animation = True
        messagebox.showerror("Error", f"Failed to reuse session: {e}")
        os.remove(get_session_file(username))
        return False
    finally:
        login_button.config(state="normal")
        login_status_canvas.pack_forget()

def login():
    global cl, username
    username = username_entry.get().strip()
    password = password_entry.get().strip()
    
    if not username or not password:
        messagebox.showerror("Error", "Please enter both username and password.")
        return

    login_button.config(state="disabled")
    login_status_canvas.pack(pady=5)
    stop_animation = False
    def stop_flag(): return stop_animation
    threading.Thread(target=animate_loading, args=(login_status_canvas, stop_flag, "login"), daemon=True).start()

    def login_thread():
        global cl
        try:
            cl = Client()
            cl.login(username, password)
            save_session(cl, username)
            root.after(0, lambda: messagebox.showinfo("Success", "Logged in and session saved."))
            root.after(0, show_upload_frame)
        except Exception as e:
            root.after(0, lambda: messagebox.showerror("Login Failed", f"Login error: {e}"))
        finally:
            nonlocal stop_animation
            stop_animation = True
            root.after(0, lambda: login_status_canvas.pack_forget())
            root.after(0, lambda: login_button.config(state="normal"))

    threading.Thread(target=login_thread, daemon=True).start()

def logout():
    session_file = get_session_file(username)
    if os.path.exists(session_file):
        os.remove(session_file)
        messagebox.showinfo("Logout", "Logged out and session removed.")
        upload_frame.pack_forget()
        login_frame.pack(fill="both", expand=True)
    else:
        messagebox.showerror("Error", "No session found.")

def show_upload_frame():
    login_frame.pack_forget()
    upload_frame.pack(fill="both", expand=True)

media_files_list = []

def select_file(file_types, label):
    global media_files_list
    file_path = filedialog.askopenfilename(filetypes=file_types)
    if file_path:
        media_files_list = [os.path.abspath(file_path)]
        label.config(text=os.path.basename(file_path))

def select_multiple_files(file_types, label):
    global media_files_list
    file_paths = filedialog.askopenfilenames(filetypes=file_types)
    if file_paths:
        media_files_list = [os.path.abspath(f) for f in file_paths]
        label.config(text=f"{len(file_paths)} files selected")

def upload():
    global media_files_list
    current_tab = notebook.tab(notebook.select(), "text")
    media_files = media_files_list
    cover_file = cover_file_var.get() or None
    caption_widget = caption_widgets[current_tab]
    caption = caption_widget.get("1.0", tk.END).strip()

    if not media_files:
        messagebox.showerror("Error", "No media files selected.")
        return

    media_files = [os.path.abspath(f) for f in media_files]
    missing_files = [f for f in media_files if not os.path.exists(f)]
    if missing_files:
        messagebox.showerror("Error", f"One or more selected media files do not exist: {missing_files}")
        return

    if current_tab == "Reel":
        if not all(f.lower().endswith(".mp4") for f in media_files):
            messagebox.showerror("Error", "All files must be MP4 for Reels.")
            return
        if not caption:
            messagebox.showwarning("Warning", "No caption provided for Reel. Instagram may require a caption.")
    elif current_tab == "Story":
        if not all(f.lower().endswith((".jpg", ".png", ".mp4")) for f in media_files):
            messagebox.showerror("Error", "Files must be JPG, PNG, or MP4 for Stories.")
            return
    else:
        if not all(f.lower().endswith((".jpg", ".png", ".mp4")) for f in media_files):
            messagebox.showerror("Error", "Files must be JPG, PNG, or MP4 for Posts.")
            return
        if not caption:
            messagebox.showwarning("Warning", "No caption provided for Post. Instagram may require a caption.")

    status_canvas.pack(pady=5)
    upload_button.config(state="disabled")
    total_files = len(media_files)
    current_file = 0

    def upload_thread():
        nonlocal current_file
        stop_animation = False
        def stop_flag(): return stop_animation
        threading.Thread(target=animate_loading, args=(status_canvas, stop_flag, "upload", total_files, 1), daemon=True).start()

        def process_upload(file_list):
            nonlocal current_file
            for i, media_file in enumerate(file_list, 1):
                current_file = i
                root.after(0, lambda: status_canvas.delete("loading"))
                root.after(0, lambda: threading.Thread(target=animate_loading, args=(status_canvas, stop_flag, "upload", total_files, current_file), daemon=True).start())
                try:
                    if current_tab == "Reel":
                        cl.clip_upload(media_file, caption=caption if caption else None, thumbnail=cover_file)
                    elif current_tab == "Post":
                        if media_file.lower().endswith(".mp4"):
                            cl.clip_upload(media_file, caption=caption if caption else None, thumbnail=cover_file)
                        else:
                            cl.photo_upload(media_file, caption=caption if caption else None)
                    elif current_tab == "Story":
                        if media_file.lower().endswith(".mp4"):
                            cl.clip_upload_to_story(media_file)
                        else:
                            cl.photo_upload_to_story(media_file)

                    root.after(0, lambda: status_canvas.delete("loading"))
                except Exception as e:
                    root.after(0, lambda: messagebox.showerror("Upload Error", f"Error uploading {media_file}: {e}"))
                    break

        process_upload(media_files)
        root.after(0, lambda: messagebox.showinfo("Upload Complete", "Upload completed successfully!"))
        stop_animation = True
        root.after(0, lambda: upload_button.config(state="normal"))

    threading.Thread(target=upload_thread, daemon=True).start()

root = tk.Tk()
root.title("Instagram Media Uploader")
root.geometry("500x500")

login_frame = ttk.Frame(root)
login_frame.pack(fill="both", expand=True)

username_label = ttk.Label(login_frame, text="Username")
username_label.pack(pady=5)
username_entry = ttk.Entry(login_frame, width=30)
username_entry.pack(pady=5)

password_label = ttk.Label(login_frame, text="Password")
password_label.pack(pady=5)
password_entry = ttk.Entry(login_frame, show="*", width=30)
password_entry.pack(pady=5)

login_button = ttk.Button(login_frame, text="Login", command=login)
login_button.pack(pady=10)

login_status_canvas = tk.Canvas(login_frame, width=50, height=50, bg="#f0f0f0")
login_status_canvas.pack_forget()

upload_frame = ttk.Frame(root)

tabs = ttk.Notebook(upload_frame)
tabs.pack(fill="both", expand=True)

reel_tab = ttk.Frame(tabs)
tabs.add(reel_tab, text="Reel")

story_tab = ttk.Frame(tabs)
tabs.add(story_tab, text="Story")

post_tab = ttk.Frame(tabs)
tabs.add(post_tab, text="Post")

root.mainloop()
