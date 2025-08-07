import os
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import face_recognition

class FaceSorterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Face Sorter App")
        self.reference_images = []
        self.reference_encodings = []
        self.reference_labels = []
        self.target_folder = ""

        self.setup_gui()

    def setup_gui(self):
        self.frame = tk.Frame(self.root)
        self.frame.pack(pady=20)

        self.load_buttons = []
        for i in range(3):
            btn = tk.Button(self.frame, text=f"Load Reference Image {i+1}", command=lambda i=i: self.load_reference_image(i))
            btn.grid(row=0, column=i, padx=10)
            self.load_buttons.append(btn)

        self.start_button = tk.Button(self.root, text="Select Target Folder and Start", command=self.process_target_folder)
        self.start_button.pack(pady=20)

        self.image_labels = [tk.Label(self.root) for _ in range(3)]
        for label in self.image_labels:
            label.pack(pady=5)

    def load_reference_image(self, index):
        path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png *.jpg *.jpeg")])
        if not path:
            return

        image = face_recognition.load_image_file(path)
        encodings = face_recognition.face_encodings(image)

        if not encodings:
            messagebox.showerror("Error", "No face detected in the selected image.")
            return

        self.reference_images.append(image)
        self.reference_encodings.append(encodings[0])
        label = os.path.splitext(os.path.basename(path))[0]
        self.reference_labels.append(label)

        # Display image in the GUI
        img = Image.open(path)
        img.thumbnail((200, 200))
        img_tk = ImageTk.PhotoImage(img)
        self.image_labels[index].configure(image=img_tk)
        self.image_labels[index].image = img_tk

    def process_target_folder(self):
        if len(self.reference_encodings) < 3:
            messagebox.showwarning("Warning", "Please load all 3 reference images first.")
            return

        self.target_folder = filedialog.askdirectory()
        if not self.target_folder:
            return

        # Create result folders
        for label in self.reference_labels:
            os.makedirs(os.path.join(self.target_folder, label), exist_ok=True)

        for filename in os.listdir(self.target_folder):
            path = os.path.join(self.target_folder, filename)
            if not os.path.isfile(path):
                continue
            if not filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                continue

            unknown_image = face_recognition.load_image_file(path)
            unknown_encodings = face_recognition.face_encodings(unknown_image)

            if not unknown_encodings:
                continue

            for face_encoding in unknown_encodings:
                matches = face_recognition.compare_faces(self.reference_encodings, face_encoding)
                for i, match in enumerate(matches):
                    if match:
                        dest = os.path.join(self.target_folder, self.reference_labels[i], filename)
                        shutil.move(path, dest)
                        break

        messagebox.showinfo("Done", "Photos sorted successfully!")

if __name__ == '__main__':
    root = tk.Tk()
    app = FaceSorterApp(root)
    root.mainloop()
