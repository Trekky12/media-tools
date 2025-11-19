from tkinter import Tk, ttk, filedialog, messagebox, PhotoImage, Button, Frame
import threading
import logging
import traceback
import os
from pathlib import Path

from PIL import Image
import pillow_heif
import piexif

import sys
import json
import locale

# Logging
log_folder = os.path.join(os.getcwd(), "logs")
if not os.path.exists(log_folder):
   os.makedirs(log_folder)

logger = logging.getLogger("erix")
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(log_folder + '/heic-convert.log')
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

VERSION = "1.0.0"

class HeicConvertApp(Tk):
    def __init__(self):
        super().__init__(className="HEIC Convert")
        self.title("HEIC Convert - Version: "+ VERSION)
        self.geometry("800x600")
        self.minsize(800, 300)
        
        if sys.platform.startswith("win"):
            self.iconbitmap(self.get_base_path() / "images-regular-full.ico")
        else:
            img = PhotoImage(file=self.get_base_path() / "images-regular-full.png")
            self.iconphoto(True, img)

        self.converting = False
        self.translations = self.load_translations()
        
        self.lang = self.detect_lang()
        if self.lang not in self.translations:
            self.lang = "en"
            
        logger.info(f"Using language {self.lang}")
        
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=0)
        self.grid_rowconfigure(2, weight=1)
        self.grid_rowconfigure(3, weight=0)

        self.grid_columnconfigure(0, weight=1)

        self.select_button = Button(self, text=self._("select_heic_files"), command=self.select_files)
        self.select_button.grid(row=0, column=0, sticky="w", padx=10, pady=10)

        self.progress = ttk.Progressbar(self, orient="horizontal", length=200, mode="determinate", maximum=100)
        self.progress.grid(row=1, column=0, padx=10, pady=10, sticky="ew")

        self.table = ttk.Treeview(self, columns=("file", "state"), show="headings")
        self.table.heading("file", text=self._("file"))
        self.table.heading("state", text=self._("state"))
        self.table.grid(row=2, column=0, sticky="nsew", padx=10, pady=5)
        self.table.bind("<<TreeviewSelect>>", self.on_select)
        
        #self.table.column("file", width=120)
        self.table.column("state", width=10)
        
        self.table.tag_configure("ok", foreground="green")
        self.table.tag_configure("error", foreground="white", background="red")
        self.table.tag_configure("warning", foreground="orange")

        bottom_frame = Frame(self)
        bottom_frame.grid(row=3, column=0, sticky="ew", padx=10, pady=10)
        bottom_frame.grid_columnconfigure(0, weight=1)

        self.remove_button = Button(bottom_frame, text=self._("remove_selected_file"), state="disabled", command=self.remove_selected)
        self.remove_button.pack(side="left")

        self.convert_button = Button(bottom_frame, text=self._("convert"), command=self.start_convert)
        self.convert_button.pack(side="right")

    def select_files(self):
        files = filedialog.askopenfilenames(title=self._("select_heic_files"),filetypes=[("HEIC files",".heic .heif")])
        for file in files:
            self.table.insert("", "end", values=(file, ""))

    def on_select(self, event):
        if not self.converting:
            selected = self.table.selection()            
            if selected:
                self.remove_button.config(state="normal")
            else:
                self.remove_button.config(state="disabled")
                
    def remove_selected(self):
        selected = self.table.selection()
        for item in selected:
            self.table.delete(item)
        self.remove_button.config(state="disabled")
        
    def disable_ui(self):
        self.select_button.config(state="disabled")
        self.convert_button.config(state="disabled")
        self.remove_button.config(state="disabled")
        self.progress.config(mode="indeterminate")
        self.progress.start()

    def enable_ui(self):
        self.select_button.config(state="normal")
        self.convert_button.config(state="normal")
        if self.table.selection():
            self.remove_button.config(state="normal")
        else:
            self.remove_button.config(state="disabled")
        self.progress.stop()
        self.progress.config(mode="determinate")
        
    def start_convert(self):
        threading.Thread(target=self.convert).start()
        
    def convert(self):
        self.converting = True
        self.disable_ui()
        logger.info("Starting convert")

        destination_folder = filedialog.askdirectory(title=self._("select_destination_folder"))
        if destination_folder:
            error = False
            
            delete_originals = messagebox.askyesno(self._("delete_originals_title"), self._("delete_originals_content"))
            
            pillow_heif.register_heif_opener()

            for item in self.table.get_children():
                file, *_ = self.table.item(item, "values")

                self.table.item(item, values=(file, self._("converting")))

                try:
                    if not pillow_heif.is_supported(file):
                        self.table.item(item, values=(file, self._("not_supported")), tags=("warning",))
                    else:
                        res = self.convert_heic_to_jpg(file, destination_folder, delete_originals)
                        if res:
                            self.table.item(item, values=(file, self._("done")), tags=("ok",))
                        else:
                            self.table.item(item, values=(file, self._("skipped")), tags=("warning",))

                except Exception as e:
                    error = True
                    print(f"Error converting {file}: {e}")
                    print(traceback.format_exc())

                    self.table.item(item, values=(file, self._("ERROR")), tags=("error",))
                    
                    logger.error(f"Error converting {file}: {e}")
                    logger.error(traceback.format_exc())

            if error:
                messagebox.showinfo(self._("convert_failed_title"), self._("convert_failed_content"))
                logger.error("Convert Failed")
            else:
                messagebox.showinfo(self._("convert_complete_title"), self._("convert_complete_content"))
                logger.info("Convert Complete")
        
        self.enable_ui()
        self.converting = False

    def get_base_path(self):
        if getattr(sys, 'frozen', False):
            return Path(sys._MEIPASS)
        else:
            return Path(__file__).parent
        
    def detect_lang(self):
        lang = locale.getlocale()[0]

        if not lang:
            lang = locale.getdefaultlocale()[0]

        if not lang:
            lang = "en_US"

        return lang.split("_")[0]

    def load_translations(self):
        file_path = self.get_base_path() / "translations.json"
        if file_path.exists():
            return json.loads(file_path.read_text(encoding="utf-8"))

        return {}
    
    def _(self, key):
        return self.translations[self.lang].get(key, self.translations["en"].get(key, key))
        
    def convert_heic_to_jpg(self, heic_file, destination_folder, remove = False):
        heic_path = Path(heic_file)
        jpg_name = f"{heic_path.stem}_converted.jpg"
        destination_folder = Path(destination_folder)
        jpg_path = destination_folder / jpg_name
        
        if not os.path.exists(jpg_path):
            im = Image.open(heic_path)
            icc_profile = im.info.get('icc_profile')

            # copy exif
            exif_bytes = im.info.get('exif')
            if exif_bytes:
                try:
                    exif_dict = piexif.load(exif_bytes)
                    exif_bytes = piexif.dump(exif_dict)
                    print(f"Copied EXIF from {heic_path}")
                except Exception as e:
                    print(f"Could not parse EXIF from HEIC: {e}")
                    exif_bytes = b''
            else:
                exif_bytes = b''
                print(f"No EXIF found in {heic_path}")

            # increase gamma
            im = self.apply_gamma(im, gamma=1.1)

            im.save(jpg_path, "JPEG", quality=90, icc_profile=icc_profile, exif=exif_bytes)
            print(f"Converted {heic_path} to {jpg_path}")
            if remove:
                os.remove(heic_path)
                print(f"Deleted {heic_path}")

            return True

        return False

    def apply_gamma(self, image, gamma=1.1):
        if image.mode not in ("RGB", "L"):
            image = image.convert("RGB")

        inv_gamma = 1.0 / gamma
        table = [int((i / 255.0) ** inv_gamma * 255) for i in range(256)]

        if image.mode == "RGB":
            return image.point(table * 3)
        else:
            return image.point(table)
                
if __name__ == "__main__":
    app = HeicConvertApp()
    app.mainloop()