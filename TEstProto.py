import cv2
import pytesseract
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import os

# Path to the Tesseract executable
pytesseract.pytesseract.tesseract_cmd = "/usr/bin/tesseract"

displayed_image = None

def process_image(image):
    global displayed_image
    if image is not None and len(image.shape) == 2:  
        extracted_text = pytesseract.image_to_string(image)

        h, w = image.shape

        for b in pytesseract.image_to_boxes(image).splitlines():
            b = b.split()
            x, y, x2, y2 = int(b[1]), h - int(b[2]), int(b[3]), h - int(b[4])
            cv2.rectangle(image, (x, y), (x2, y2), (0, 0, 255), 1)

        processed_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(processed_image)
        displayed_image = pil_image  

        pil_image = pil_image.resize((400, 400), resample=Image.LANCZOS)
        img_tk = ImageTk.PhotoImage(image=pil_image)

        panel.config(image=img_tk)
        panel.image = img_tk

        # Display the extracted text in the GUI
        text_output.config(state=tk.NORMAL)
        text_output.delete("1.0", tk.END)
        text_output.insert(tk.END, extracted_text)
        text_output.config(state=tk.DISABLED)
    else:
        messagebox.showerror("Error", "Invalid input image.")

def copy_to_clipboard():
    text = text_output.get("1.0", tk.END)
    root.clipboard_clear()
    root.clipboard_append(text)
    messagebox.showinfo("Copy Successful", "Text copied to clipboard.")

def save_as_file():
    text = text_output.get("1.0", tk.END)
    try:
        file_path = filedialog.asksaveasfilename(initialdir=os.path.join(os.path.expanduser('~'), 'Desktop'), title="Save As", filetypes=(("Text files", "*.txt"), ("All files", "*.*")))
        if file_path:
            with open(file_path, "w") as file:
                file.write(text)
            messagebox.showinfo("Save Successful", f"Text saved to {file_path} successfully.")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred while saving the file: {e}")

def load_and_convert_image():
    file_path = filedialog.askopenfilename()
    if file_path:
        image = cv2.imread(file_path)
        if image is not None:
            gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            process_image(gray_image)
        else:
            messagebox.showerror("Error", "Failed to load image.")
    else:
        messagebox.showerror("Error", "No image selected.")

def capture_image():
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
    ret, frame = cap.read()
    cap.release()
    if ret:
        gray_image = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        process_image(gray_image)
    else:
        messagebox.showerror("Error", "Failed to capture image from camera.")

def save_image():
    global displayed_image
    if displayed_image:
        try:
            file_path = filedialog.asksaveasfilename(initialdir=os.path.join(os.path.expanduser('~'), 'Desktop'), title="Save Image", filetypes=(("PNG files", "*.png"), ("JPEG files", "*.jpg"), ("All files", "*.*")), defaultextension=".png")
            if file_path:
                displayed_image.save(file_path)
                messagebox.showinfo("Save Successful", f"Image saved to {file_path} successfully.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while saving the image: {e}")
    else:
        messagebox.showerror("Error", "No image to save.")

root = tk.Tk()
root.title("OCR Image Processing")

load_button = tk.Button(root, text="Load Image", command=load_and_convert_image)
load_button.pack(pady=10)

capture_button = tk.Button(root, text="Capture Image from Camera", command=capture_image)
capture_button.pack(pady=5)

panel = tk.Label(root)
panel.pack()

text_output = tk.Text(root, height=10, width=50)
text_output.config(state=tk.DISABLED)
text_output.pack(pady=10)

copy_button = tk.Button(root, text="Copy to Clipboard", command=copy_to_clipboard)
copy_button.pack(pady=5)

save_text_button = tk.Button(root, text="Save As Text", command=save_as_file)
save_text_button.pack(side=tk.LEFT, padx=5, pady=5)

save_image_button = tk.Button(root, text="Save Image", command=save_image)
save_image_button.pack(side=tk.LEFT, padx=5, pady=5)

root.mainloop()
