import cv2
import os
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk

class NumberPlateApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Number Plate Detection and Cropping")

        self.file_path = None
        self.selected_photo = None  # Store PhotoImage for selected image
        self.processed_photo = None  # Store PhotoImage for processed image

        # Create labels
        self.label_selected = tk.Label(root, text="Selected Image:")
        self.label_selected.pack(pady=5)

        self.label_selected_image = tk.Label(root)
        self.label_selected_image.pack(pady=10)

        self.label_processed = tk.Label(root, text="Processed Image:")
        self.label_processed.pack(pady=5)

        # Create buttons
        self.select_button = tk.Button(root, text="Select File", command=self.select_file)
        self.select_button.pack(pady=5)

        self.process_button = tk.Button(root, text="Process File", command=self.process_file)
        self.process_button.pack(pady=10)

        # Create image preview label for processed image
        self.image_label_processed = tk.Label(root)
        self.image_label_processed.pack(pady=10)

    def select_file(self):
        self.file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png;*.jpg;*.jpeg")])
        if self.file_path:
            print(f"Selected file: {self.file_path}")
            self.show_selected_image()

    def show_selected_image(self):
        # Load and display the selected image in the Tkinter label
        selected_image = Image.open(self.file_path)
        selected_image = selected_image.resize((400, 300), Image.LANCZOS)
        self.selected_photo = ImageTk.PhotoImage(selected_image)

        self.label_selected_image.configure(image=self.selected_photo)
        self.label_selected_image.image = self.selected_photo

    def show_processed_image(self, processed_file_path):
        # Load and display the processed image in the Tkinter label
        processed_image = Image.open(processed_file_path)
        processed_image = processed_image.resize((400, 300), Image.LANCZOS)
        self.processed_photo = ImageTk.PhotoImage(processed_image)

        self.image_label_processed.configure(image=self.processed_photo)
        self.image_label_processed.image = self.processed_photo

    def process_file(self):
        if self.file_path:
            # Specify the path to the directory for saving processed files
            output_directory_path = os.path.join('C:\\Users\\Geo Thomas\\OneDrive\\Desktop\\kevin\\New folder (2)', 'DETECTED_AND_CROPPED_FILES')
            print(f"Output directory: {output_directory_path}")

            # Ensure the output directory exists
            os.makedirs(output_directory_path, exist_ok=True)

            try:
                # Detect and crop number plates in the file
                processed_file_path = self.detect_and_crop_number_plate(self.file_path, output_directory_path)

                # Display the processed image
                self.show_processed_image(processed_file_path)

                messagebox.showinfo("Success", "Number plate detection and cropping completed!")
                print(f"Processed file saved at: {processed_file_path}")

            except ValueError as e:
                messagebox.showerror("Error", str(e))

    def detect_and_crop_number_plate(self, input_path, output_path):
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

        # Save the modified image with rectangles drawn around number plates
        output_filename = os.path.join(output_path, os.path.basename(input_path))
        cv2.imwrite(output_filename, img)

        return output_filename

if __name__ == "__main__":
    root = tk.Tk()
    app = NumberPlateApp(root)
    root.mainloop()
