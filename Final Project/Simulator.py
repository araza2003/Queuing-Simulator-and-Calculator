import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk  # For handling images
import subprocess

# Function to open the queuing calculator


def open_queuing_calculator():
    try:
        subprocess.Popen(["python", "Queuing_Cal.py"])
    except FileNotFoundError:
        messagebox.showerror("Error", "Queuing_Cal.py file not found.")

# Function to handle the simulator


def open_simulator():
    def run_simulation():
        arrival_dist = arrival_choice.get()
        service_dist = service_choice.get()

        if not arrival_dist or not service_dist:
            messagebox.showerror(
                "Error", "Please select both arrival and service time distributions.")
            return

        try:
            if arrival_dist == "Poisson" and service_dist == "Exponential":
                subprocess.Popen(["python", "MMC.py"])
            elif arrival_dist in ["Poisson", "Exponential"] and service_dist in ["Normal", "Uniform", "Gamma"]:
                subprocess.Popen(["python", "MGC.py"])
            elif arrival_dist in ["Normal", "Uniform", "Gamma"] and service_dist in ["Normal", "Uniform", "Gamma"]:
                subprocess.Popen(["python", "GGC.py"])
            elif arrival_dist == service_dist in ["Normal", "Uniform", "Gamma"] and service_dist == "Exponential":
                messagebox.showerror(
                    "Error", "Invalid combination of distributions.")
            else:
                messagebox.showerror(
                    "Error", "Invalid combination of distributions.")
        except FileNotFoundError as e:
            messagebox.showerror(
                "Error", f"{str(e).split(' ')[-1]} file not found.")

    # Create a new window for distribution selection
    sim_window = tk.Toplevel(root)
    sim_window.title("Simulator")
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    sim_window.state("zoomed")
    sim_window.geometry(f"{screen_width}x{screen_height}+0+0")

    # Create a canvas for the header in the simulator window
    canvas = tk.Canvas(sim_window, width=screen_width, height=screen_height)
    canvas.pack(fill="both", expand=True)

    # Create the light gray box at the top of the simulator window
    top_box_height = 60  # Adjust the height as needed
    canvas.create_rectangle(
        0, 0,  # Top-left corner of the rectangle
        screen_width, top_box_height,  # Bottom-right corner of the rectangle
        fill="#008080", outline="#008080"  # Use a darker sea green color
    )

    # Add the logo to the top-left corner
    logo_image = Image.open("logo.png")  # Replace with your logo image path
    logo_image = logo_image.resize(
        (150, 100), Image.Resampling.LANCZOS)  # Resize logo as needed
    logo_photo = ImageTk.PhotoImage(logo_image)

    # Retain the reference by storing it as an attribute of the sim_window
    sim_window.logo_photo = logo_photo  # Keep a reference

    # Place the logo image on the canvas
    canvas.create_image(10, -20, image=logo_photo, anchor="nw")

    # Title Label for the simulator window
    canvas.create_text(screen_width // 2, 30, text="Simulator",
                       font=("Tahoma", 22, "bold"), fill="white")

    # Create the selection UI components for the simulator window using canvas.create_window()
    arrival_label = tk.Label(
        sim_window, text="Select Arrival Time Distribution:")
    arrival_choice = ttk.Combobox(sim_window, values=[
                                  "Poisson", "Exponential", "Normal", "Uniform", "Gamma"], state="readonly")
    service_label = tk.Label(
        sim_window, text="Select Service Time Distribution:")
    service_choice = ttk.Combobox(sim_window, values=[
                                  "Poisson", "Exponential", "Normal", "Uniform", "Gamma"], state="readonly")
    run_button = tk.Button(
        sim_window, text="Run Simulator", command=run_simulation)

    # Place the UI components using create_window() on the canvas
    canvas.create_window(screen_width // 2, 200, window=arrival_label)
    canvas.create_window(screen_width // 2, 250, window=arrival_choice)
    canvas.create_window(screen_width // 2, 300, window=service_label)
    canvas.create_window(screen_width // 2, 350, window=service_choice)
    canvas.create_window(screen_width // 2, 400, window=run_button)


# Main Application Window
root = tk.Tk()
root.title("Queueing and Simulation System")

# Get the screen width and height
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

# Maximize the window
root.state("zoomed")
root.geometry(f"{screen_width}x{screen_height}+0+0")

canvas = tk.Canvas(root, width=screen_width, height=screen_height)
canvas.pack(fill="both", expand=True)

# Create a light gray box spanning the top from left to right
top_box_height = 110  # Adjust the height as needed
canvas.create_rectangle(
    0, 0,  # Top-left corner of the rectangle
    screen_width, top_box_height,  # Bottom-right corner of the rectangle
    fill="#008080", outline="#008080"  # Use a darker sea green color
)

# Add the logo to the top-left corner
logo_image = Image.open("logo.png")  # Replace with your logo image path
logo_image = logo_image.resize(
    (270, 160), Image.Resampling.LANCZOS)  # Resize logo as needed
logo_photo = ImageTk.PhotoImage(logo_image)

canvas.create_image(-1, -25, image=logo_photo, anchor="nw")

# Title Label
text_id = canvas.create_text(
    screen_width // 2, 55, text="Queuing and Simulation System", font=("Tahoma", 36, "bold"), fill="white")

# Buttons for options
button_exit = tk.Button(
    root, text="Exit", command=root.destroy, font=("Arial", 12))

# Load and resize images to be square
image1 = Image.open("calculator.png")  # Replace with your image paths
image2 = Image.open("simulator.png")
image3 = Image.open("exit.png")
image_size = 200  # Size for the square images

image1 = image1.resize((image_size, image_size), Image.Resampling.LANCZOS)
image2 = image2.resize((image_size, image_size), Image.Resampling.LANCZOS)
image3 = image3.resize((image_size, image_size), Image.Resampling.LANCZOS)

# Convert images to PhotoImage objects
image1_photo = ImageTk.PhotoImage(image1)
image2_photo = ImageTk.PhotoImage(image2)
image3_photo = ImageTk.PhotoImage(image3)

# Place images side by side
canvas.create_image(screen_width // 4, 350, image=image1_photo)
canvas.create_image(screen_width // 2, 350, image=image2_photo)
canvas.create_image(3 * screen_width // 4, 350, image=image3_photo)

# Place buttons below each image
button1 = tk.Button(root, text="Queuing Calculator",
                    command=open_queuing_calculator, font=("Arial", 14), width=20)
button2 = tk.Button(root, text="Simulator",
                    command=open_simulator, font=("Arial", 14), width=20)

canvas.create_window(screen_width // 4, 500, window=button1)
canvas.create_window(screen_width // 2, 500, window=button2)
canvas.create_window(3 * screen_width // 4, 500, window=button_exit)

# Create a small box from bottom-left to bottom-right
bottom_box_height = 110  # Height of the bottom box
canvas.create_rectangle(
    # Top-left corner of the rectangle (start from the bottom left)
    0, screen_height - bottom_box_height,
    # Bottom-right corner of the rectangle (end at the bottom right)
    screen_width, screen_height,
    # Use the same sea green color or a different color if needed
    fill="#008080", outline="#008080"
)

# Developed By Text
canvas.create_text(750, 775, text="© Developed By: Ahmed Raza, Dinesh Kumar, Syed Muhammad Abbas Shah and Syed Zohaib Ahmed Qadri", font=(
    "Arial", 12, "bold"), fill="black")

root.mainloop()
