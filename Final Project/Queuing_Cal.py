import tkinter as tk
from tkinter import ttk, messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import math
from tkinter import PhotoImage
from PIL import Image, ImageTk  # Import Image and ImageTk modules from PIL


# --- Queue Model Functions ---
def mm1_queue(lambda_rate, mu_rate):
    rho = lambda_rate / mu_rate
    if rho >= 1:
        return {"Error": "System is unstable (rho >= 1)."}
    Lq = rho**2 / (1 - rho)
    Wq = Lq / lambda_rate
    W = 1 / (mu_rate - lambda_rate)
    L = lambda_rate * W
    return {"Utilization (rho)": rho, "Lq": Lq, "Wq": Wq, "W": W, "L": L}


def mmc_queue(lambda_rate, mu_rate, servers):
    rho = lambda_rate / (servers * mu_rate)
    if rho >= 1:
        return {"Error": "System is unstable (rho >= 1)."}
    Po = 1 / (sum([(lambda_rate / mu_rate)**k / math.factorial(k) for k in range(servers)]) +
              ((lambda_rate / mu_rate)**servers / (math.factorial(servers) * (1 - rho))))
    Lq = (Po * (lambda_rate / mu_rate)**servers * rho) / \
        (math.factorial(servers) * (1 - rho)**2)
    Wq = Lq / lambda_rate
    W = Wq + 1 / mu_rate
    L = lambda_rate * W
    return {"Utilization (rho)": rho, "Lq": Lq, "Wq": Wq, "W": W, "L": L}


def mg1_queue(lambda_rate, mu_rate, sigma_service):
    rho = lambda_rate / mu_rate
    if rho >= 1:
        return {"Error": "System is unstable (rho >= 1)."}
    Lq = (lambda_rate**2 * sigma_service**2 + rho**2) / (2 * (1 - rho))
    Wq = Lq / lambda_rate
    W = Wq + 1 / mu_rate
    L = lambda_rate * W
    return {"Utilization (rho)": rho, "Lq": Lq, "Wq": Wq, "W": W, "L": L}


def mgc_queue(lambda_rate, mu_rate, servers, sigma_service):
    rho = lambda_rate / (servers * mu_rate)
    if rho >= 1:
        return {"Error": "System is unstable (rho >= 1)."}
    Po = 1 / (sum([(lambda_rate / mu_rate)**k / math.factorial(k) for k in range(servers)]) +
              ((lambda_rate / mu_rate)**servers / (math.factorial(servers) * (1 - rho))))
    Lq = (Po * (lambda_rate / mu_rate)**servers * rho) / \
        (math.factorial(servers) * (1 - rho)**2)
    Wq = Lq / lambda_rate
    W = Wq + 1 / mu_rate
    L = lambda_rate * W
    return {"Utilization (rho)": rho, "Lq": Lq, "Wq": Wq, "W": W, "L": L}


def gg1_queue(lambda_rate, mu_rate, sigma_arrival, sigma_service):
    rho = lambda_rate / mu_rate
    if rho >= 1:
        return {"Error": "System is unstable (rho >= 1)."}
    ca2 = (sigma_arrival / (1 / lambda_rate))**2
    cs2 = (sigma_service / (1 / mu_rate))**2
    Lq = (rho**2 * (ca2 + cs2)) / (2 * (1 - rho))
    Wq = Lq / lambda_rate
    W = Wq + 1 / mu_rate
    L = lambda_rate * W
    return {"Utilization (rho)": rho, "Lq": Lq, "Wq": Wq, "W": W, "L": L}


def ggc_queue(lambda_rate, mu_rate, servers, sigma_arrival, sigma_service):
    rho = lambda_rate / (servers * mu_rate)
    if rho >= 1:
        return {"Error": "System is unstable (rho >= 1)."}
    ca2 = (sigma_arrival / (1 / lambda_rate))**2
    cs2 = (sigma_service / (1 / mu_rate))**2
    Po = 1 / (sum([(lambda_rate / mu_rate)**k / math.factorial(k) for k in range(servers)]) +
              ((lambda_rate / mu_rate)**servers / (math.factorial(servers) * (1 - rho))))
    Lq = (Po * (lambda_rate / mu_rate)**servers * rho) / \
        (math.factorial(servers) * (1 - rho)**2)
    Wq = Lq / lambda_rate
    W = Wq + 1 / mu_rate
    L = lambda_rate * W
    return {"Utilization (rho)": rho, "Lq": Lq, "Wq": Wq, "W": W, "L": L}


# --- Helper Functions ---
def calculate_and_plot():
    try:
        lambda_rate = float(arrival_rate_entry.get())
        mu_rate = float(service_rate_entry.get())

        if mu_rate <= 0:
            raise ValueError("Service rate (mu) must be greater than 0.")

        choice = model_choice.get()
        if choice == "MM1":
            result = mm1_queue(lambda_rate, mu_rate)
        elif choice == "MMC":
            servers = int(servers_entry.get())
            result = mmc_queue(lambda_rate, mu_rate, servers)
        elif choice == "MG1":
            sigma_service = float(sigma_service_entry.get())
            result = mg1_queue(lambda_rate, mu_rate, sigma_service)
        elif choice == "MGC":
            servers = int(servers_entry.get())
            sigma_service = float(sigma_service_entry.get())
            result = mgc_queue(lambda_rate, mu_rate, servers, sigma_service)
        elif choice == "GG1":
            sigma_arrival = float(sigma_arrival_entry.get())
            sigma_service = float(sigma_service_entry.get())
            result = gg1_queue(lambda_rate, mu_rate,
                               sigma_arrival, sigma_service)
        elif choice == "GGC":
            servers = int(servers_entry.get())
            sigma_arrival = float(sigma_arrival_entry.get())
            sigma_service = float(sigma_service_entry.get())
            result = ggc_queue(lambda_rate, mu_rate, servers,
                               sigma_arrival, sigma_service)
        else:
            raise ValueError("Invalid queuing model selected.")

        if "Error" in result:
            messagebox.showerror("Error", result["Error"])
            return

        update_results(result)
        plot_graph(result)
    except Exception as e:
        messagebox.showerror("Error", str(e))


def update_results(result):
    for key, value in result.items():
        result_labels[key].config(text=f"{value:.2f}")


def plot_graph(result):
    graph_window = tk.Toplevel(root)
    graph_window.title("Queue Metrics Graph")

    fig, ax = plt.subplots()

    x = ["Utilization (rho)", "Lq", "Wq", "W", "L"]
    y = [result.get(k, 0) for k in x]

    colors = ["skyblue", "lightgreen", "salmon", "gold", "plum"]

    ax.bar(x, y, color=colors)
    ax.set_title("Queue Metrics")
    ax.set_ylabel("Values")
    ax.set_xlabel("Metrics")

    canvas = FigureCanvasTkAgg(fig, master=graph_window)
    canvas.draw()
    canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    tk.Button(graph_window, text="Close",
              command=graph_window.destroy).pack(pady=10)


# --- Main Application ---

def on_closing(event=None):
    root.destroy()


root = tk.Tk()
root.bind('<Escape>', on_closing)
root.title("Queuing Calculator")
root.protocol("WM_DELETE_WINDOW", on_closing)
# Get the screen width and height
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

# Maximize the window
root.state("zoomed")
    
top_box_height = 60

# Set the window to full screen
root.geometry(f"{screen_width}x{screen_height}+0+0")

# Create a canvas widget to draw the box
canvas = tk.Canvas(root, width=screen_width, height=top_box_height, bg="lightgray")
canvas.pack(fill=tk.X)

# Create a rectangle on the canvas
canvas.create_rectangle(
    0, 0,  # Top-left corner of the rectangle
    screen_width, top_box_height,  # Bottom-right corner of the rectangle
    fill="#008080", outline="#008080"  # Dark sea green color
)

# Add a logo to the box (optional, similar to previous code)
try:
    # Open the logo image file
    logo_image = Image.open("logo.png")  # Use the correct file path
    
    # Resize the image (make it smaller)
    logo_image = logo_image.resize((150, 100))  # Resize to 50x50 (adjust as needed)
    
    # Convert the image to a PhotoImage object for Tkinter
    logo_image_tk = ImageTk.PhotoImage(logo_image)
    
    # Place the resized logo on the canvas
    canvas.create_image(10, 30, image=logo_image_tk, anchor="w")  # Positioned in the left center
except Exception as e:
    canvas.create_text(10, top_box_height // 2, text="Logo Not Available", anchor="w", font=("Arial", 12, "bold"))

# Add title text next to the logo (aligned horizontally)
canvas.create_text(630, top_box_height // 2, text="Queuing Calculator", font=("Arial", 22, "bold"), anchor="w", fill='white')


# Input Frame
input_frame = tk.Frame(root)
input_frame.pack(pady=10)

tk.Label(input_frame, text="Arrival Rate (λ):").grid(
    row=0, column=0, padx=5, pady=5)
arrival_rate_entry = tk.Entry(input_frame)
arrival_rate_entry.grid(row=0, column=1, padx=5, pady=5)

tk.Label(input_frame, text="Service Rate (μ):").grid(
    row=1, column=0, padx=5, pady=5)
service_rate_entry = tk.Entry(input_frame)
service_rate_entry.grid(row=1, column=1, padx=5, pady=5)

model_choice = ttk.Combobox(input_frame, values=[
                            "MM1", "MMC", "MG1", "MGC", "GG1", "GGC"], state="readonly")
model_choice.grid(row=2, column=1, padx=5, pady=5)
model_choice.set("MM1")
tk.Label(input_frame, text="Model:").grid(row=2, column=0, padx=5, pady=5)

# Additional inputs
servers_label = tk.Label(input_frame, text="Servers (c):")
servers_label.grid(row=3, column=0, padx=5, pady=5)
servers_entry = tk.Entry(input_frame)
servers_entry.grid(row=3, column=1, padx=5, pady=5)

sigma_service_label = tk.Label(input_frame, text="σ Service:")
sigma_service_label.grid(row=4, column=0, padx=5, pady=5)
sigma_service_entry = tk.Entry(input_frame)
sigma_service_entry.grid(row=4, column=1, padx=5, pady=5)

sigma_arrival_label = tk.Label(input_frame, text="σ Arrival:")
sigma_arrival_label.grid(row=5, column=0, padx=5, pady=5)
sigma_arrival_entry = tk.Entry(input_frame)
sigma_arrival_entry.grid(row=5, column=1, padx=5, pady=5)

# Results Frame
results_frame = tk.Frame(root)
results_frame.pack(pady=10)

result_labels = {}
metrics = ["Utilization (rho)", "Lq", "Wq", "W", "L"]
for i, metric in enumerate(metrics):
    tk.Label(results_frame, text=f"{metric}:").grid(
        row=i, column=0, padx=5, pady=5)
    result_labels[metric] = tk.Label(results_frame, text="N/A")
    result_labels[metric].grid(row=i, column=1, padx=5, pady=5)

# Calculate Button
tk.Button(root, text="Calculate", command=calculate_and_plot).pack(pady=10)


root.mainloop()
