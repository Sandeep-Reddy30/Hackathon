import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import pytesseract
import cv2
import numpy as np
import re
from datetime import datetime, timedelta
import webbrowser
import random

# Set up pytesseract path (change if needed)
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# OTP generation and verification (For simplicity, using random numbers and storing in memory)
otp_storage = {}
otp_expiry = 300  # OTP validity in seconds

# Token counter and history
token_count = {'tokens': 20}
token_history = []

# Define the main application class
class OCRApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Pristine-Access")
        self.root.attributes('-fullscreen', True)  # Make the window fullscreen
        self.root.configure(bg="#e0f7fa")  # Light cyan background color
        
        self.current_frame = None
        self.show_start_page()

    def show_start_page(self):
        if self.current_frame:
            self.current_frame.destroy()
        
        self.current_frame = tk.Frame(self.root, bg="#e0f7fa")
        self.current_frame.pack(fill=tk.BOTH, expand=True)

        title_label = tk.Label(self.current_frame, text="Welcome to Pristine-Access", font=("Helvetica", 36, "bold"), fg="#004d40", bg="#e0f7fa")
        title_label.pack(pady=30)

        start_button = tk.Button(self.current_frame, text="Start", command=self.show_phone_number_page, font=("Helvetica", 16), bg="#00796b", fg="white")
        start_button.pack(pady=20)

    def show_phone_number_page(self):
        if self.current_frame:
            self.current_frame.destroy()
        
        self.current_frame = tk.Frame(self.root, bg="#e0f7fa")
        self.current_frame.pack(fill=tk.BOTH, expand=True)

        title_label = tk.Label(self.current_frame, text="Enter Phone Number", font=("Helvetica", 36, "bold"), fg="#004d40", bg="#e0f7fa")
        title_label.pack(pady=30)

        self.phone_number_entry = tk.Entry(self.current_frame, font=("Helvetica", 16), width=20)
        self.phone_number_entry.pack(pady=20)

        submit_button = tk.Button(self.current_frame, text="Submit", command=self.send_otp, font=("Helvetica", 16), bg="#00796b", fg="white")
        submit_button.pack(pady=10)

        self.otp_entry = tk.Entry(self.current_frame, font=("Helvetica", 16), width=20)
        self.otp_entry.pack(pady=10)

        verify_button = tk.Button(self.current_frame, text="Verify OTP", command=self.verify_otp, font=("Helvetica", 16), bg="#004d40", fg="white")
        verify_button.pack(pady=10)

    def send_otp(self):
        phone_number = self.phone_number_entry.get().strip()
        if len(phone_number) != 10 or not phone_number.isdigit():
            messagebox.showerror("Error", "Please enter a valid 10-digit phone number.")
            return
        
        otp = random.randint(100000, 999999)
        otp_storage[phone_number] = (otp, datetime.now())
        
        # Here you would send the OTP to the user's phone number using an SMS API
        # For this example, we just print it to the console
        print(f"OTP for {phone_number}: {otp}")
        
        messagebox.showinfo("Info", "OTP sent!")

    def verify_otp(self):
        phone_number = self.phone_number_entry.get().strip()
        entered_otp = self.otp_entry.get().strip()

        if len(phone_number) != 10 or not phone_number.isdigit():
            messagebox.showerror("Error", "Please enter a valid 10-digit phone number.")
            return

        if phone_number in otp_storage:
            stored_otp, timestamp = otp_storage[phone_number]
            if datetime.now() > timestamp + timedelta(seconds=otp_expiry):
                del otp_storage[phone_number]
                messagebox.showerror("Error", "OTP has expired. Please request a new one.")
                return

            if int(entered_otp) == stored_otp:
                messagebox.showinfo("Success", "OTP verified successfully.")
                self.show_upload_page()
            else:
                messagebox.showerror("Error", "Invalid OTP. Please try again.")
        else:
            messagebox.showerror("Error", "Phone number not found. Please request a new OTP.")
            
    def show_upload_page(self):
        if self.current_frame:
            self.current_frame.destroy()
        
        self.current_frame = tk.Frame(self.root, bg="#e0f7fa")
        self.current_frame.pack(fill=tk.BOTH, expand=True)

        title_label = tk.Label(self.current_frame, text="Pristine-Access", font=("Helvetica", 36, "bold"), fg="#004d40", bg="#e0f7fa")
        title_label.pack(pady=30)

        label = tk.Label(self.current_frame, text="Upload Aadhaar Card Image:", font=("Helvetica", 18), bg="#e0f7fa", fg="#00796b")
        label.pack(pady=20)

        self.upload_button = tk.Button(self.current_frame, text="Upload Image", command=self.upload_image, font=("Helvetica", 16), bg="#00796b", fg="white")
        self.upload_button.pack(pady=10)

        self.process_button = tk.Button(self.current_frame, text="Process Image", command=self.process_image, font=("Helvetica", 16), bg="#004d40", fg="white")
        self.process_button.pack(pady=10)

        self.result_text = tk.Text(self.current_frame, height=5, width=60, font=("Helvetica", 14), bg="#ffffff", wrap=tk.WORD)
        self.result_text.pack(pady=20)

        self.right_image = Image.open('xx.jpg')
        self.right_image = self.right_image.resize((200, 200), Image.Resampling.LANCZOS)
        self.right_image_tk = ImageTk.PhotoImage(self.right_image)
        self.image_label = tk.Label(self.current_frame, image=self.right_image_tk, bg="#e0f7fa")
        self.image_label.pack(side=tk.RIGHT, padx=40, pady=10)

        self.image_path = None
        self.image = None

    def upload_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")])
        if file_path:
            self.image_path = file_path
            img = Image.open(file_path)
            img.thumbnail((200, 200))
            img = ImageTk.PhotoImage(img)
            if hasattr(self, 'img_label'):
                self.img_label.destroy()
            self.img_label = tk.Label(self.current_frame, image=img, bg="#e0f7fa")
            self.img_label.image = img
            self.img_label.pack(pady=10)
            self.image = cv2.imread(file_path)
        else:
            messagebox.showerror("Error", "No image selected!")

    def preprocess_image(self, image):
        if image is None:
            raise ValueError("No image to process")

        gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        blurred_image = cv2.GaussianBlur(gray_image, (3, 3), 0)
        thresh_image = cv2.adaptiveThreshold(blurred_image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
        return thresh_image

    def extract_text_from_image(self, image):
        processed_image = self.preprocess_image(image)
        text = pytesseract.image_to_string(processed_image)
        return text

    def extract_year_of_birth(self, text):
        year_pattern = r'\b(19[0-9]{2}|20[0-2][0-9]|202[0-4])\b'
        year_match = re.search(year_pattern, text)
        if year_match:
            year_str = year_match.group(0)
            year = int(year_str)
            return year
        return None

    def calculate_age(self, year_of_birth):
        if year_of_birth:
            current_year = datetime.today().year
            age = current_year - year_of_birth
            return age
        return None

    def grant_tokens(self, age):
        if age >= 18:
            return "User is 18 or older. Granting 20 tokens for 6 months."
        else:
            return "User is under 18. No tokens granted."

    def process_image(self):
        if self.image_path and self.image is not None:
            text = self.extract_text_from_image(self.image)
            if text:
                year_of_birth = self.extract_year_of_birth(text)
                if year_of_birth:
                    age = self.calculate_age(year_of_birth)
                    result = f"Your Age: {age}\n{self.grant_tokens(age)}"
                    self.result_text.delete(1.0, tk.END)
                    self.result_text.insert(tk.END, result)
                    
                    if age >= 18:
                        self.root.after(3000, self.show_token_page)
                else:
                    messagebox.showerror("Error", "Year of birth not found in the image.")
            else:
                messagebox.showerror("Error", "Unable to extract text from the image.")
        else:
            messagebox.showerror("Error", "No image uploaded!")

    def show_token_page(self):
        if self.current_frame:
            self.current_frame.destroy()
        
        self.current_frame = tk.Frame(self.root, bg="#e0f7fa")
        self.current_frame.pack(fill=tk.BOTH, expand=True)

        title_label = tk.Label(self.current_frame, text="Token Management", font=("Helvetica", 36, "bold"), fg="#004d40", bg="#e0f7fa")
        title_label.pack(pady=30)

        token_label = tk.Label(self.current_frame, text=f"Available Tokens: {token_count['tokens']}", font=("Helvetica", 24), fg="#00796b", bg="#e0f7fa")
        token_label.pack(pady=20)

        use_token_button = tk.Button(self.current_frame, text="Use Token", command=self.use_token, font=("Helvetica", 16), bg="#00796b", fg="white")
        use_token_button.pack(pady=10)

        history_button = tk.Button(self.current_frame, text="Token History", command=self.show_token_history, font=("Helvetica", 16), bg="#004d40", fg="white")
        history_button.pack(pady=10)

    def use_token(self):
        if token_count['tokens'] > 0:
            token_count['tokens'] -= 1
            token_usage_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            token_history.append(f"Token used at {token_usage_time}")
            webbrowser.open('http://www.nofap.com')  # Replace this with the actual website
            self.show_token_page()
        else:
            messagebox.showinfo("Info", "No tokens available.")

    def show_token_history(self):
        if self.current_frame:
            self.current_frame.destroy()

        self.current_frame = tk.Frame(self.root, bg="#e0f7fa")
        self.current_frame.pack(fill=tk.BOTH, expand=True)

        title_label = tk.Label(self.current_frame, text="Token History", font=("Helvetica", 36, "bold"), fg="#004d40", bg="#e0f7fa")
        title_label.pack(pady=30)
        

        history_text = tk.Text(self.current_frame, height=10, width=60, font=("Helvetica", 14), bg="#ffffff", wrap=tk.WORD)
        history_text.pack(pady=20)

        if token_history:
            for entry in token_history:
                history_text.insert(tk.END, f"{entry}\n")
        else:
            history_text.insert(tk.END, "No tokens used yet.")

        back_button = tk.Button(self.current_frame, text="Back", command=self.show_token_page, font=("Helvetica", 16), bg="#00796b", fg="white")
        back_button.pack(pady=10)

# Initialize the app
if __name__ == "__main__":
    root = tk.Tk()
    app = OCRApp(root)
    root.mainloop()
