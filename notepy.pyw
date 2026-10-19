"""
i- GLOBAL HOTKEYS:
   - Num 9: Instantly show or hide the Slate window from anywhere on your PC.
   - Num 5: Open/close the live search bar to highlight matches and jump through text.
   - Esc: Hide the app window or close the search bar.
   - Ctrl + Shift + Q: Completely exit and close the application.

i- WINDOW MOVEMENT:
   - Right-Click & Drag: Click and hold the right mouse button anywhere inside the window and drag to move Slate smoothly across your screen.

i- COLLAPSIBLE CODE BLOCKS:
   - Type three backticks (```) before and after your text to create code blocks.
   - Double-click the code block header to fold/collapse the text into a clean single-line banner, and double-click again to expand it.

i- CLICKABLE WEB LINKS:
   - Any website URL (starting with http:// or https://) is automatically highlighted and opens in your default web browser when clicked.

i- RIGHT-CLICK CONTEXT MENU:
   - Right-clicking without dragging opens a drop-down menu allowing you to:
     * Copy selected text or code blocks.
     * Delete selected text.
     * Open a Color Wheel to apply custom highlights to text.
     * Exit the app.

i- AUTO-SAVE & STORAGE:
   - Slate saves your notes automatically in real-time. Everything is stored persistently in a local `.glass_scratchpad.md` file in your user folder.

python -m PyInstaller --noconsole --onefile --icon=icon.ico --name=Slate notepy.pyw
get icon from somewhere
"""

import sys
import os
import ctypes
from ctypes import wintypes
import winreg
import re
import webbrowser
import tkinter as tk
from tkinter import font, colorchooser

# ==============================================================================
# 1. WINDOWS API & GLASS/ROUNDED CORNERS SETUP (ctypes)
# ==============================================================================

class ACCENT_POLICY(ctypes.Structure):
    _fields_ = [
        ("AccentState", ctypes.c_int),
        ("AccentFlags", ctypes.c_int),
        ("GradientColor", ctypes.c_int),
        ("AnimationId", ctypes.c_int)
    ]

class WINDOWCOMPOSITIONATTRIBDATA(ctypes.Structure):
    _fields_ = [
        ("Attribute", ctypes.c_int),
        ("pData", ctypes.POINTER(ACCENT_POLICY)),
        ("SizeOfData", ctypes.c_size_t)
    ]

ACCENT_ENABLE_ACRYLICBLURBEHIND = 4

def apply_glass_and_corners(hwnd):
    """Applies Windows Acrylic blur with a warm orange tint and rounded corners."""
    try:
        user32 = ctypes.windll.user32
        policy = ACCENT_POLICY()
        policy.AccentState = ACCENT_ENABLE_ACRYLICBLURBEHIND
        policy.GradientColor = 0xD8150D0A  # Rich dark base with warm amber undertone
        policy.AccentFlags = 2
        policy.AnimationId = 0

        data = WINDOWCOMPOSITIONATTRIBDATA()
        data.Attribute = 19  # WCA_ACCENT_POLICY
        data.pData = ctypes.pointer(policy)
        data.SizeOfData = ctypes.sizeof(policy)
        
        set_window_composition = getattr(user32, 'SetWindowCompositionAttribute', None)
        if set_window_composition:
            set_window_composition(hwnd, ctypes.byref(data))

        DWMWA_WINDOW_CORNER_PREFERENCE = 33
        DWMWCP_ROUND = 2
        ctypes.windll.dwmapi.DwmSetWindowAttribute(
            hwnd, 
            DWMWA_WINDOW_CORNER_PREFERENCE, 
            ctypes.byref(ctypes.c_int(DWMWCP_ROUND)), 
            ctypes.sizeof(ctypes.c_int)
        )
    except Exception:
        pass


# ==============================================================================
# 2. STARTUP REGISTRY MANAGEMENT
# ==============================================================================

STARTUP_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"
APP_NAME = "GlassmorphismScratchpad"

def set_autostart(enable=True):
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, STARTUP_KEY, 0, winreg.KEY_ALL_ACCESS)
        if enable:
            script_path = os.path.abspath(sys.argv[0])
            pythonw = os.path.join(os.path.dirname(sys.executable), "pythonw.exe")
            cmd = f'"{pythonw}" "{script_path}"' if os.path.exists(pythonw) else f'"{sys.executable}" "{script_path}"'
            winreg.SetValueEx(key, APP_NAME, 0, winreg.REG_SZ, cmd)
        else:
            try:
                winreg.DeleteValue(key, APP_NAME)
            except FileNotFoundError:
                pass
        winreg.CloseKey(key)
    except Exception:
        pass


# ==============================================================================
# 3. GLOBAL HOTKEY LISTENER (Numpad 9 & Numpad 5)
# ==============================================================================

VK_NUMPAD9 = 0x69
VK_NUMPAD5 = 0x65
HOTKEY_ID_9 = 1001
HOTKEY_ID_5 = 1002

class GlobalHotkeyThread:
    def __init__(self, toggle_cb, search_cb):
        self.toggle_cb = toggle_cb
        self.search_cb = search_cb
        self.running = False

    def start(self):
        import threading
        self.running = True
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()

    def _run(self):
        user32 = ctypes.windll.user32
        user32.RegisterHotKey(None, HOTKEY_ID_9, 0, VK_NUMPAD9)
        user32.RegisterHotKey(None, HOTKEY_ID_5, 0, VK_NUMPAD5)

        msg = wintypes.MSG()
        while self.running:
            res = user32.GetMessageW(ctypes.byref(msg), None, 0, 0)
            if res <= 0:
                break
            if msg.message == 0x0312:
                if msg.wParam == HOTKEY_ID_9:
                    self.toggle_cb()
                elif msg.wParam == HOTKEY_ID_5:
                    self.search_cb()
            user32.TranslateMessage(ctypes.byref(msg))
            user32.DispatchMessageW(ctypes.byref(msg))

        user32.UnregisterHotKey(None, HOTKEY_ID_9)
        user32.UnregisterHotKey(None, HOTKEY_ID_5)


# ==============================================================================
# 4. SCRATCHPAD APPLICATION LOGIC
# ==============================================================================

NOTES_FILE = os.path.join(os.path.expanduser("~"), ".glass_scratchpad.md")

class GlassScratchpad:
    def __init__(self):
        set_autostart(True)

        self.root = tk.Tk()
        self.root.title("Glass Scratchpad")
        self.root.geometry("520x660+300+200")
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        self.root.attributes("-alpha", 0.95)
        
        self.bg_color = "#100B08"
        self.fg_color = "#FCE4EC"
        self.root.configure(bg=self.bg_color)

        self.container = tk.Frame(self.root, bg=self.bg_color)
        self.container.pack(fill=tk.BOTH, expand=True, padx=16, pady=16)

        self.collapsed_blocks = {}
        self._is_dragging = False

        self._setup_ui()
        self._setup_markdown_tags()
        self._setup_context_menu()
        self._load_notes()

        # Right-Click & Drag bindings across entire app window
        for widget in [self.root, self.container, self.text, self.line_numbers]:
            widget.bind("<Button-3>", self._start_drag)
            widget.bind("<B3-Motion>", self._on_drag)
            widget.bind("<ButtonRelease-3>", self._on_release)

        # Hotkeys
        self.root.bind("<Escape>", lambda e: self.hide())
        self.root.bind("<Control-Shift-Q>", lambda e: self.quit_app())
        self.root.bind("<Control-Shift-q>", lambda e: self.quit_app())

        self._save_job = None

        self.root.update_idletasks()
        hwnd = ctypes.windll.user32.GetParent(self.root.winfo_id())
        apply_glass_and_corners(hwnd)

        self.hotkey_thread = GlobalHotkeyThread(self._on_hotkey, self._on_search_hotkey)
        self.hotkey_thread.start()

        self.visible = True

    def _setup_ui(self):
        # Header Bar with Accent Dash
        self.header_bar = tk.Frame(self.container, bg=self.bg_color, height=14)
        self.header_bar.pack(side=tk.TOP, fill=tk.X, pady=(0, 6))

        accent_dash = tk.Frame(self.header_bar, bg="#FFB74D", height=3, width=28)
        accent_dash.pack(side=tk.LEFT)

        # Search Bar Frame (hidden by default)
        self.search_frame = tk.Frame(self.container, bg="#1E120A", bd=1)
        self.search_entry = tk.Entry(self.search_frame, bg="#1E120A", fg="#FFB74D", insertbackground="#FFB74D", bd=0, font=("Consolas", 10))
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=6, pady=4)
        self.search_entry.bind("<KeyRelease>", self._on_search_key)
        self.search_entry.bind("<Return>", self._search_next)
        self.search_entry.bind("<Escape>", lambda e: self.hide_search())

        # Editor layout container (Line numbers + Text Area)
        self.editor_frame = tk.Frame(self.container, bg=self.bg_color)
        self.editor_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.line_font = font.Font(family="Consolas", size=10)
        self.line_numbers = tk.Text(
            self.editor_frame,
            width=3,
            bg=self.bg_color,
            fg="#7A5238",
            font=self.line_font,
            bd=0,
            highlightthickness=0,
            state="disabled",
            takefocus=0
        )
        self.line_numbers.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 8))

        self.text_font = font.Font(family="Consolas", size=11)
        self.text = tk.Text(
            self.editor_frame,
            bg=self.bg_color,
            fg=self.fg_color,
            insertbackground="#FFA726",
            selectbackground="#5C3317",
            selectforeground="#FFF3E0",
            font=self.text_font,
            bd=0,
            highlightthickness=0,
            wrap=tk.WORD,
            undo=True
        )
        self.text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.text.focus_set()

        # Footer Badge with Hotkey Cheatsheet
        self.footer_frame = tk.Frame(self.container, bg=self.bg_color, bd=0)
        self.footer_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=(8, 0))

        self.status_dot = tk.Label(self.footer_frame, text="●", fg="#66BB6A", bg=self.bg_color, font=("Arial", 8))
        self.status_dot.pack(side=tk.LEFT, padx=(0, 3))

        self.status_label = tk.Label(self.footer_frame, text="Saved", fg="#7A5238", bg=self.bg_color, font=("Consolas", 8))
        self.status_label.pack(side=tk.LEFT)

        info_text = "[Num9: Toggle] [Num5: Search] [Esc: Hide] [R-Click: Drag/Menu]"
        self.info_label = tk.Label(self.footer_frame, text=info_text, fg="#5A3E2B", bg=self.bg_color, font=("Consolas", 7))
        self.info_label.pack(side=tk.LEFT, padx=10)

        self.stats_label = tk.Label(self.footer_frame, text="0 words", fg="#7A5238", bg=self.bg_color, font=("Consolas", 8))
        self.stats_label.pack(side=tk.RIGHT)

        # Bindings
        self.text.bind("<<Modified>>", self._on_text_modified)
        self.text.bind("<MouseWheel>", self._on_mousewheel)
        self.line_numbers.bind("<MouseWheel>", self._on_mousewheel)
        self.text.bind("<Double-1>", self._on_double_click)

    def _setup_markdown_tags(self):
        base_size = 11
        self.text.tag_configure("h1", font=font.Font(family="Consolas", size=base_size + 6, weight="bold"), foreground="#FFB74D")
        self.text.tag_configure("h2", font=font.Font(family="Consolas", size=base_size + 4, weight="bold"), foreground="#FFA726")
        self.text.tag_configure("h3", font=font.Font(family="Consolas", size=base_size + 2, weight="bold"), foreground="#FF9800")
        
        self.text.tag_configure("bold", font=font.Font(family="Consolas", size=base_size, weight="bold"), foreground="#FFF3E0")
        self.text.tag_configure("italic", font=font.Font(family="Consolas", size=base_size, slant="italic"), foreground="#FFCC80")
        self.text.tag_configure("code", font=font.Font(family="Consolas", size=base_size), background="#2E1A11", foreground="#FFB74D")
        self.text.tag_configure("code_fold", font=font.Font(family="Consolas", size=base_size, weight="bold"), background="#22130C", foreground="#FF9800")
        
        self.text.tag_configure("bullet", foreground="#FF8F00")
        self.text.tag_configure("checkbox_todo", foreground="#FF7043")
        self.text.tag_configure("checkbox_done", foreground="#6D4C41", overstrike=True)
        
        self.text.tag_configure("link", foreground="#4FC3F7", underline=True)
        self.text.tag_bind("link", "<Button-1>", self._open_link)
        
        # Search highlight tag
        self.text.tag_configure("search_hit", background="#FFB74D", foreground="#100B08")

    def _setup_context_menu(self):
        self.context_menu = tk.Menu(self.root, tearoff=0, bg="#1E120A", fg="#FCE4EC", activebackground="#FF8F00", activeforeground="#FFF")
        self.context_menu.add_command(label="📋 Copy Selected / Code", command=self._context_copy)
        self.context_menu.add_command(label="🗑️ Delete Selection", command=self._context_delete)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="🎨 Highlight with Color Wheel...", command=self._context_color_wheel)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="❌ Exit App", command=self.quit_app)

    def _show_context_menu(self, event):
        try:
            self.context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.context_menu.grab_release()

    def _context_copy(self):
        try:
            selected_text = self.text.get(tk.SEL_FIRST, tk.SEL_LAST)
        except tk.TclError:
            selected_text = self.text.get("1.0", tk.END)
        self.root.clipboard_clear()
        self.root.clipboard_append(selected_text)

    def _context_delete(self):
        try:
            self.text.delete(tk.SEL_FIRST, tk.SEL_LAST)
        except tk.TclError:
            pass

    def _context_color_wheel(self):
        try:
            color = colorchooser.askcolor(title="Choose Highlight Color")[1]
            if color:
                tag_name = f"custom_color_{color}"
                self.text.tag_configure(tag_name, background=color, foreground="#100B08" if color > "#888888" else "#FFF")
                self.text.tag_add(tag_name, tk.SEL_FIRST, tk.SEL_LAST)
        except tk.TclError:
            pass

    def _open_link(self, event):
        try:
            index = self.text.index(f"@{event.x},{event.y}")
            line_start = self.text.index(f"{index} linestart")
            line_end = self.text.index(f"{index} lineend")
            line_text = self.text.get(line_start, line_end)
            urls = re.findall(r'https?://[^\s]+', line_text)
            if urls:
                webbrowser.open(urls[0])
        except Exception:
            pass

    def _on_double_click(self, event):
        try:
            index = self.text.index(f"@{event.x},{event.y}")
            line_num = int(index.split(".")[0])
            for block_id, data in self.collapsed_blocks.items():
                if data['header_line'] == line_num:
                    data['collapsed'] = not data['collapsed']
                    self._apply_markdown_highlighting()
                    break
        except Exception:
            pass

    def _apply_markdown_highlighting(self):
        content = self.text.get("1.0", tk.END)
        lines = content.split("\n")

        for tag in ["h1", "h2", "h3", "bold", "italic", "code", "code_fold", "bullet", "checkbox_todo", "checkbox_done", "link"]:
            self.text.tag_remove(tag, "1.0", tk.END)

        in_code_block = False
        code_block_start = 0

        for line_idx, line in enumerate(lines, start=1):
            line_start = f"{line_idx}.0"
            line_end = f"{line_idx}.end"

            for m in re.finditer(r'https?://[^\s]+', line):
                self.text.tag_add("link", f"{line_idx}.{m.start()}", f"{line_idx}.{m.end()}")

            if line.strip().startswith("```"):
                if not in_code_block:
                    in_code_block = True
                    code_block_start = line_idx
                    self.text.tag_add("code_fold", line_start, line_end)
                else:
                    in_code_block = False
                    block_key = f"block_{code_block_start}"
                    is_collapsed = self.collapsed_blocks.get(block_key, {}).get('collapsed', False)
                    self.collapsed_blocks[block_key] = {'header_line': code_block_start, 'collapsed': is_collapsed}
                    
                    if is_collapsed:
                        self.text.tag_remove("code", f"{code_block_start}.0", line_end)
                        self.text.tag_add("code_fold", f"{code_block_start}.0", line_end)
                continue

            if in_code_block:
                block_key = f"block_{code_block_start}"
                is_collapsed = self.collapsed_blocks.get(block_key, {}).get('collapsed', False)
                if is_collapsed:
                    self.text.tag_add("code_fold", line_start, line_end)
                    self.text.tag_configure("elided", elide=True)
                    self.text.tag_add("elided", line_start, line_end)
                else:
                    self.text.tag_remove("elided", line_start, line_end)
                    self.text.tag_add("code", line_start, line_end)
                continue
            else:
                self.text.tag_remove("elided", line_start, line_end)

            if line.startswith("# "):
                self.text.tag_add("h1", line_start, line_end)
            elif line.startswith("## "):
                self.text.tag_add("h2", line_start, line_end)
            elif line.startswith("### "):
                self.text.tag_add("h3", line_start, line_end)
            elif line.lstrip().startswith(("- ", "* ", "+ ")):
                self.text.tag_add("bullet", line_start, line_end)
            elif re.search(r'^\s*[ ]', line):
                self.text.tag_add("checkbox_todo", line_start, line_end)
            elif re.search(r'^\s*[[xX]]', line):
                self.text.tag_add("checkbox_done", line_start, line_end)

            for m in re.finditer(r'\*\*(.*?)\*\*', line):
                self.text.tag_add("bold", f"{line_idx}.{m.start()}", f"{line_idx}.{m.end()}")
            for m in re.finditer(r'(?<!\*)\*(?!\*)(.*?)(?<!\*)\*(?!\*)', line):
                self.text.tag_add("italic", f"{line_idx}.{m.start()}", f"{line_idx}.{m.end()}")
            for m in re.finditer(r'`(.*?)`', line):
                self.text.tag_add("code", f"{line_idx}.{m.start()}", f"{line_idx}.{m.end()}")

        self._update_line_numbers(len(lines))
        self._update_stats(content)

    def _update_line_numbers(self, total_lines):
        line_strings = "\n".join(str(i) for i in range(1, total_lines + 1))
        self.line_numbers.config(state=tk.NORMAL)
        self.line_numbers.delete("1.0", tk.END)
        self.line_numbers.insert("1.0", line_strings)
        self.line_numbers.config(state=tk.DISABLED)

    def _update_stats(self, content):
        words = len(content.split())
        chars = len(content.strip())
        self.stats_label.config(text=f"{words} words | {chars} chars")

    def _on_mousewheel(self, event):
        delta = -1 if event.delta > 0 else 1
        self.text.yview_scroll(delta, "units")
        self.line_numbers.yview_scroll(delta, "units")
        return "break"

    def _on_text_modified(self, event=None):
        if self.text.edit_modified():
            self.text.edit_modified(False)
            self.status_dot.config(fg="#FFA726")
            self.status_label.config(text="Saving...")
            
            if self._save_job:
                self.root.after_cancel(self._save_job)
            self._save_job = self.root.after(300, self._sync_and_save)

    def _sync_and_save(self):
        self._apply_markdown_highlighting()
        self._save_notes()
        self.status_dot.config(fg="#66BB6A")
        self.status_label.config(text="Saved")

    def _save_notes(self):
        try:
            content = self.text.get("1.0", tk.END)
            with open(NOTES_FILE, "w", encoding="utf-8") as f:
                f.write(content)
        except Exception:
            pass

    def _load_notes(self):
        if os.path.exists(NOTES_FILE):
            try:
                with open(NOTES_FILE, "r", encoding="utf-8") as f:
                    content = f.read()
                self.text.delete("1.0", tk.END)
                self.text.insert("1.0", content)
                self._apply_markdown_highlighting()
            except Exception:
                pass

    # --- Search Engine ---
    def _on_search_hotkey(self):
        self.root.after(0, self.toggle_search_bar)

    def toggle_search_bar(self):
        if self.search_frame.winfo_ismapped():
            self.hide_search()
        else:
            self.search_frame.pack(side=tk.TOP, fill=tk.X, pady=(0, 6), before=self.editor_frame)
            self.search_entry.focus_set()

    def hide_search(self):
        self.search_frame.pack_forget()
        self.text.tag_remove("search_hit", "1.0", tk.END)
        self.text.focus_set()

    def _on_search_key(self, event=None):
        query = self.search_entry.get()
        self.text.tag_remove("search_hit", "1.0", tk.END)
        if not query:
            return
        pos = "1.0"
        while True:
            pos = self.text.search(query, pos, stopindex=tk.END, nocase=True)
            if not pos:
                break
            end_pos = f"{pos}+{len(query)}c"
            self.text.tag_add("search_hit", pos, end_pos)
            pos = end_pos

    def _search_next(self, event=None):
        query = self.search_entry.get()
        if not query:
            return
        current_idx = self.text.index(tk.INSERT)
        pos = self.text.search(query, current_idx, stopindex=tk.END, nocase=True)
        if not pos:
            pos = self.text.search(query, "1.0", stopindex=current_idx, nocase=True)
        if pos:
            end_pos = f"{pos}+{len(query)}c"
            self.text.mark_set(tk.INSERT, end_pos)
            self.text.see(pos)

    # --- Right-Click & Drag Window ---
    def _start_drag(self, event):
        self._drag_start_x = event.x_root
        self._drag_start_y = event.y_root
        self._win_start_x = self.root.winfo_x()
        self._win_start_y = self.root.winfo_y()
        self._is_dragging = False

    def _on_drag(self, event):
        dx = event.x_root - self._drag_start_x
        dy = event.y_root - self._drag_start_y
        if abs(dx) > 2 or abs(dy) > 2:
            self._is_dragging = True
            x = self._win_start_x + dx
            y = self._win_start_y + dy
            self.root.geometry(f"+{x}+{y}")

    def _on_release(self, event):
        if not self._is_dragging:
            self._show_context_menu(event)

    def _on_hotkey(self):
        self.root.after(0, self.toggle_visibility)

    def toggle_visibility(self):
        if self.visible:
            self.hide()
        else:
            self.show()

    def show(self):
        self.root.deiconify()
        self.root.lift()
        self.root.attributes("-topmost", True)
        self.text.focus_set()
        self.visible = True

    def hide(self):
        self.root.withdraw()
        self.visible = False

    def quit_app(self):
        self._save_notes()
        self.hotkey_thread.running = False
        self.root.destroy()
        sys.exit(0)

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    app = GlassScratchpad()
    app.run()
