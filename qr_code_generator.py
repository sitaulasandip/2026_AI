import logging
import tkinter as tk
from tkinter import messagebox
from urllib.parse import urlparse

import qrcode
from qrcode.constants import ERROR_CORRECT_L
from PIL import Image, ImageTk


 
# All the configurable value
 
CONFIG = {
    "url":          "https://www.bioxsystems.com/",  # URL to encode
    "output_file":  "biox_systems_qr.png",           # PNG save path
    "box_size":     10,                              # Pixels per QR module
    "border":       4,                               # Quiet-zone width (modules)
    "window_title": "img",                           # Title bar label
    "padding":      20,                              # Inner frame padding (px)
    "border_color": "#D4A017",                       # Outer frame colour
}

 
# logging instead of print
 
logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
log = logging.getLogger(__name__)


 
# Data Validation
 
def validate_url(url: str) -> None:
    if not isinstance(url, str) or not url.strip():
        raise ValueError("URL must be a non-empty string.")

    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        raise ValueError(f"URL must begin with http:// or https://. Got: '{url}'")

    if not parsed.netloc:
        raise ValueError(f"URL does not contain a valid domain. Got: '{url}'")



def build_qr_object(url: str, box_size: int, border: int) -> qrcode.QRCode:
    """
    Construct and return a configured QRCode object for *url*.
    """
    qr = qrcode.QRCode(
        version=None,                 
        error_correction=ERROR_CORRECT_L,  
        box_size=box_size,
        border=border,
    )
    qr.add_data(url)
    qr.make(fit=True)  
    return qr


def render_qr_image(qr: qrcode.QRCode) -> Image.Image:
    """
    Render *qr* into a black-on-white PIL Image and return it.
    """
    return qr.make_image(fill_color="black", back_color="white")


def save_image(image: Image.Image, output_path: str) -> None:
    """
    Persist *image* to *output_path* on disk and log the result.

    """
    image.save(output_path)
    log.info("QR code saved -> %s  (%dx%d px)", output_path, *image.size)


def generate_qr_code(
    url: str,
    output_path: str,
    box_size: int,
    border: int,
) -> Image.Image:
    """
    Orchestrate validation, building, rendering, and saving of a QR code.

    """
    validate_url(url)                           
    qr     = build_qr_object(url, box_size, border)
    image  = render_qr_image(qr)
    save_image(image, output_path)
    return image


 
# Best Practice #5 — Avoid mixing technologies
# All GUI code is isolated here; QR logic above has zero tkinter imports.
 
def build_gui_window(title: str) -> tk.Tk:
    """
    Create and configure the root tkinter window.
    """
    root = tk.Tk()
    root.title(title)
    root.resizable(False, False)
    return root


def build_image_frame(
    parent: tk.Widget,
    border_color: str,
    padding: int,
) -> tk.Frame:
    """
    Build a two-layer frame: coloured outer border + white inner area.
    """
    outer = tk.Frame(parent, bg=border_color, padx=6, pady=6)
    outer.pack(fill="both", expand=True)

    inner = tk.Frame(outer, bg="white", padx=padding, pady=padding)
    inner.pack(fill="both", expand=True)

    return inner


def attach_image_label(frame: tk.Frame, image: Image.Image) -> None:
    """
    Convert *image* to a tkinter-compatible PhotoImage and attach it to
    *frame* via a Label widget.  Stores a reference on the label to
    prevent the image being garbage-collected while the window is open.
    """
    tk_image = ImageTk.PhotoImage(image)

    label = tk.Label(frame, image=tk_image, bg="white")
    label.image = tk_image  # Retain reference — tkinter drops it without this
    label.pack()


def display_qr_in_gui(
    image: Image.Image,
    title: str,
    border_color: str,
    padding: int,
) -> None:
    """
    Display *image* in a decorated tkinter window and start the event loop.

    """
    root  = build_gui_window(title)
    frame = build_image_frame(root, border_color, padding)
    attach_image_label(frame, image)
    root.mainloop()


 
# Entry point — Best Practice #2 (no globals) and #6 (one task: orchestrate)
 
def main() -> None:
    """
    Read configuration, generate the QR code, and launch the GUI.

    """
    try:
        qr_image = generate_qr_code(
            url         = CONFIG["url"],
            output_path = CONFIG["output_file"],
            box_size    = CONFIG["box_size"],
            border      = CONFIG["border"],
        )

        display_qr_in_gui(
            image        = qr_image,
            title        = CONFIG["window_title"],
            border_color = CONFIG["border_color"],
            padding      = CONFIG["padding"],
        )

    except ValueError as validation_error:
        # Bad URL supplied — show a clear message and do not crash
        messagebox.showerror("Input Error", str(validation_error))
        log.error("Validation failed: %s", validation_error)

    except IOError as file_error:
        # Disk write failed — surface the OS reason to the user
        messagebox.showerror("File Error", str(file_error))
        log.error("File save failed: %s", file_error)


if __name__ == "__main__":
    main()
