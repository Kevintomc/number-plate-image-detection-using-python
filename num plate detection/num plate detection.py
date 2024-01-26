import cv2
import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk

class NumberPlateApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Number Plate Detection and Cropping")

        self.file_path = None
        self.selected_photo = None  # Store PhotoImage for selected image
        self.processed_image = None  # Store processed image
        self.processed_photo = None  # Store PhotoImage for processed image preview
        self.crop_coordinates = None  # Store crop coordinates

        # Maximum size for the preview images
        self.max_preview_size = (400, 300)

        # Create labels
        self.label_selected = ttk.Label(root, text="Selected Image:")
        self.label_selected.pack(pady=5)

        self.label_selected_image = ttk.Label(root)
        self.label_selected_image.pack(pady=10)

        self.label_processed = ttk.Label(root, text="Processed Image:")
        self.label_processed.pack(pady=5)

        # Create buttons
        self.select_button = ttk.Button(root, text="Select File", command=self.select_file)
        self.select_button.pack(pady=5)

        self.process_button = ttk.Button(root, text="Process File", command=self.process_file)
        self.process_button.pack(pady=10)

        self.download_button = ttk.Button(root, text="Download Processed Image", command=self.download_processed_image, state="disabled")
        self.download_button.pack(pady=10)

        # Create image preview label for processed image
        self.image_label_processed = ttk.Label(root)
        self.image_label_processed.pack(pady=10)

        # Create progress bar
        self.progress_bar = ttk.Progressbar(root, mode="indeterminate", length=300)
        self.progress_bar.pack(pady=10)

    def select_file(self):
        self.file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png;*.jpg;*.jpeg")])
        if self.file_path:
            print(f"Selected file: {self.file_path}")
            self.show_selected_image()

    def show_selected_image(self):
        # Load and display the selected image in the Tkinter label
        selected_image = Image.open(self.file_path)
        selected_image.thumbnail(self.max_preview_size, Image.LANCZOS)
        self.selected_photo = ImageTk.PhotoImage(selected_image)

        self.label_selected_image.configure(image=self.selected_photo)
        self.label_selected_image.image = self.selected_photo

    def show_processed_image(self, processed_image, crop_coordinates):
        # Crop the processed image
        cropped_image = processed_image.crop(crop_coordinates)

        # Display the cropped processed image in the Tkinter label for preview
        cropped_image.thumbnail(self.max_preview_size, Image.LANCZOS)
        self.processed_photo = ImageTk.PhotoImage(cropped_image)

        self.image_label_processed.configure(image=self.processed_photo)
        self.image_label_processed.image = self.processed_photo

        # Enable the download button
        self.download_button["state"] = "normal"

    def process_file(self):
        if self.file_path:
            # Disable buttons during processing
            self.select_button["state"] = "disabled"
            self.process_button["state"] = "disabled"
            self.download_button["state"] = "disabled"

            # Show progress bar
            self.progress_bar.start()

            try:
                # Detect and crop number plates in the file
                self.processed_image, self.crop_coordinates = self.detect_and_crop_number_plate(self.file_path)

                # Display the processed image for preview
                self.show_processed_image(self.processed_image, self.crop_coordinates)

                messagebox.showinfo("Success", "Number plate detection and cropping completed!")

            except ValueError as e:
                messagebox.showerror("Error", str(e))

            finally:
                # Enable buttons after processing
                self.select_button["state"] = "normal"
                self.process_button["state"] = "normal"

                # Stop and hide progress bar
                self.progress_bar.stop()
                self.progress_bar.pack_forget()

    def detect_and_crop_number_plate(self, input_path):
        # Load the image
        img = cv2.imread(input_path)

        # Convert the image to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Apply GaussianBlur to reduce noise and help in contour detection
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)

        # Use edge detection (Canny) to find edges in the image
        edges = cv2.Canny(blurred, 50, 150)

        # Find contours in the edged image
        contours, _ = cv2.findContours(edges.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Filter out small contours based on area
        min_area = 1000
        valid_contours = [contour for contour in contours if cv2.contourArea(contour) > min_area]

        # Draw rectangles around the detected number plates on the original image
        for contour in valid_contours:
            x, y, w, h = cv2.boundingRect(contour)
            cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)

        # Return the processed image and crop coordinates
        return Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB)), (x, y, x + w, y + h)

    def download_processed_image(self):
        if self.processed_image and self.crop_coordinates:
            # Get the processed image filename
            processed_filename = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png")])

            if processed_filename:
                # Crop the processed image before saving
                cropped_image = self.processed_image.crop(self.crop_coordinates)
                cropped_image.save(processed_filename)
                messagebox.showinfo("Download Complete", "Cropped processed image downloaded successfully.")
            else:
                messagebox.showinfo("Download Canceled", "Download operation canceled.")

if __name__ == "__main__":
    root = tk.Tk()
    app = NumberPlateApp(root)
    root.mainloop()