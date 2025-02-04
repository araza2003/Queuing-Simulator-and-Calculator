import simpy
import tkinter as tk
from tkinter import ttk, messagebox
import random
import math
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class Process:
    def __init__(self, pid, arrival_time, service_time, server):
        self.pid = pid
        self.arrival_time = arrival_time
        self.service_time = service_time
        self.start_time = 0
        self.finish_time = 0
        self.turnaround_time = 0
        self.waiting_time = 0
        self.response_time = 0
        self.server = server

def simulate_mgc(lmbda, servers, arrivals, service_distribution, dist_params, result_frame, chart_frame):
    env = simpy.Environment()
    processes = []
    server_next_free_time = [0] * servers
    server_busy_time = [0] * servers

    arrival_times = [0]  # First arrival at time 0
    inter_arrival_times = []
    cumulative_prob = []

    for i in range(arrivals + 1):
        cp = 0
        for j in range(i):
            cp += ((math.exp(-lmbda) * lmbda**j) / math.factorial(j))
        cumulative_prob.append(cp)

    for i in range(1, arrivals):
        rn = random.random()
        for j in range(len(cumulative_prob)):
            if rn <= cumulative_prob[j]:
                inter_arrival_times.append(j - 1)
                arrival_times.append(arrival_times[-1] + inter_arrival_times[-1])
                break

    def generate_service_time():
        if service_distribution == "Normal":
            mu, sigma = dist_params
            return math.ceil(max(0, np.random.normal(mu, sigma)))
        elif service_distribution == "Uniform":
            a, b = dist_params
            return math.ceil(random.uniform(a, b))
        elif service_distribution == "Gamma":
            shape, scale = dist_params
            return math.ceil(np.random.gamma(shape, scale))

    def customer(env, pid, arrival_time):
        yield env.timeout(arrival_time - env.now)
        service_time = generate_service_time()

        server_idx = -1
        for idx in range(servers):
            if server_next_free_time[idx] <= env.now:
                server_idx = idx
                break

        if server_idx == -1:
            server_idx = min(range(servers), key=lambda i: server_next_free_time[i])

        start_time = max(env.now, server_next_free_time[server_idx])
        finish_time = start_time + service_time

        server_next_free_time[server_idx] = finish_time
        server_busy_time[server_idx] += service_time

        turnaround_time = finish_time - arrival_time
        waiting_time = start_time - arrival_time
        response_time = start_time - arrival_time

        process = Process(pid, arrival_time, service_time, f"Server {server_idx + 1}")
        process.start_time = start_time
        process.finish_time = finish_time
        process.turnaround_time = turnaround_time
        process.waiting_time = waiting_time
        process.response_time = response_time
        processes.append(process)

        yield env.timeout(service_time)

    for i, arrival_time in enumerate(arrival_times):
        env.process(customer(env, f"Customer {i + 1}", arrival_time))

    env.run()

    for row in result_frame.get_children():
        result_frame.delete(row)

    table_data = [
        [
            process.pid,
            process.server,
            f"{process.arrival_time:.2f}",
            f"{process.service_time:.2f}",
            f"{process.start_time:.2f}",
            f"{process.finish_time:.2f}",
            f"{process.turnaround_time:.2f}",
            f"{process.waiting_time:.2f}",
            f"{process.response_time:.2f}"
        ] for process in processes
    ]

    for row in table_data:
        result_frame.insert("", "end", values=row)

    service_sum = sum([float(row[3]) for row in table_data])
    turnaround_sum = sum([float(row[6]) for row in table_data])
    waiting_sum = sum([float(row[7]) for row in table_data])
    response_sum = sum([float(row[8]) for row in table_data])

    service_avg = service_sum / len(table_data)
    turnaround_avg = turnaround_sum / len(table_data)
    waiting_avg = waiting_sum / len(table_data)
    response_avg = response_sum / len(table_data)

    result_frame.insert("", "end", values=["Total", "-", "-", f"{service_sum:.2f}", "-", "-", f"{turnaround_sum:.2f}", f"{waiting_sum:.2f}", f"{response_sum:.2f}"])
    result_frame.insert("", "end", values=["Average", "-", "-", f"{service_avg:.2f}", "-", "-", f"{turnaround_avg:.2f}", f"{waiting_avg:.2f}", f"{response_avg:.2f}"])

    total_time = max([process.finish_time for process in processes])
    idle_times = [total_time - busy_time for busy_time in server_busy_time]
    utilizations = [(busy_time / total_time) * 100 for busy_time in server_busy_time]

    messagebox.showinfo(
        "Simulation Complete",
        f"Average Server Utilization: {np.mean(utilizations):.2f}%\nIdle Times: {idle_times}"
    )

    def create_gantt_chart(server_idx):
        fig, ax = plt.subplots(figsize=(10, 6))
        server_processes = [process for process in processes if f"Server {server_idx + 1}" in process.server]

        prev_end_time = 0
        for i, process in enumerate(server_processes):
            if process.start_time > prev_end_time:
                ax.barh(process.pid, process.start_time - prev_end_time, left=prev_end_time, color='white', edgecolor='black', hatch='//')

            ax.barh(process.pid, process.service_time, left=process.start_time, label=process.server)
            ax.text(process.start_time + process.service_time / 2, i, f"{process.service_time:.2f}",
                    ha='center', va='center', color='black')

            prev_end_time = process.finish_time

        ax.set_xlabel('Time')
        ax.set_ylabel('Processes')
        ax.set_title(f'Gantt Chart for Server {server_idx + 1}')
        plt.tight_layout()

        return fig

    def show_gantt_chart(server_idx):
        fig = create_gantt_chart(server_idx)
        gantt_window = tk.Toplevel()
        gantt_window.title(f"Gantt Chart for Server {server_idx + 1}")
        canvas = FigureCanvasTkAgg(fig, gantt_window)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def create_utilization_chart():
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.barh([f"Server {i + 1}" for i in range(servers)], utilizations, color="red", edgecolor="black")
        for i, utilization in enumerate(utilizations):
            ax.text(utilization + 2, i, f"{utilization:.2f}%", va="center", color="black")
        ax.set_title("Server Utilizations")
        ax.set_xlabel("Utilization (%)")
        ax.set_xlim(0, 100)
        return fig

    def show_utilization_chart():
        fig = create_utilization_chart()
        utilization_window = tk.Toplevel()
        utilization_window.title("Server Utilizations")
        canvas = FigureCanvasTkAgg(fig, utilization_window)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def create_turnaround_chart():
        fig, ax = plt.subplots(figsize=(10, 6))
        turnaround_times = [process.turnaround_time for process in processes]
        ax.plot(range(1, len(turnaround_times) + 1), turnaround_times, marker='o', linestyle='-', color='r')
        ax.set_title("Turnaround Times")
        ax.set_xlabel("Customer Index")
        ax.set_ylabel("Turnaround Time")
        ax.grid(True)
        for i, value in enumerate([p.turnaround_time for p in processes], start=1):
            ax.text(i, value + 0.1, f"{value:.2f}", ha="center", va="bottom", color='black', fontsize=8)
        return fig

    def show_turnaround_chart():
        fig = create_turnaround_chart()
        turnaround_window = tk.Toplevel()
        turnaround_window.title("Turnaround Times")
        canvas = FigureCanvasTkAgg(fig, turnaround_window)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def create_waiting_chart():
        fig, ax = plt.subplots(figsize=(10, 6))
        waiting_times = [process.waiting_time for process in processes]
        ax.plot(range(1, len(waiting_times) + 1), waiting_times, marker='o', linestyle='-', color='g')
        ax.set_title("Waiting Times")
        ax.set_xlabel("Customer Index")
        ax.set_ylabel("Waiting Time")
        ax.grid(True)
        for i, value in enumerate([p.waiting_time for p in processes], start=1):
            ax.text(i, value + 0.1, f"{value:.2f}", ha="center", va="bottom", color='black', fontsize=8)
        return fig

    def show_waiting_chart():
        fig = create_waiting_chart()
        waiting_window = tk.Toplevel()
        waiting_window.title("Waiting Times")
        canvas = FigureCanvasTkAgg(fig, waiting_window)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def create_response_chart():
        fig, ax = plt.subplots(figsize=(10, 6))
        response_times = [process.response_time for process in processes]
        ax.plot(range(1, len(response_times) + 1), response_times, marker='o', linestyle='-', color='b')
        ax.set_title("Response Times")
        ax.set_xlabel("Customer Index")
        ax.set_ylabel("Response Time")
        ax.grid(True)
        for i, value in enumerate([p.response_time for p in processes], start=1):
            ax.text(i, value + 0.1, f"{value:.2f}", ha="center", va="bottom", color='black', fontsize=8)
        return fig

    def show_response_chart():
        fig = create_response_chart()
        response_window = tk.Toplevel()
        response_window.title("Response Times")
        canvas = FigureCanvasTkAgg(fig, response_window)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
        # Create Inter-Arrival Times chart
    def create_inter_arrival_chart():
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.plot(range(1, len(inter_arrival_times) + 1), inter_arrival_times, marker='o', linestyle='-', color='b')
        ax.set_title("Inter-Arrival Times")
        ax.set_xlabel("Customer Index")
        ax.set_ylabel("Inter-Arrival Time")
        ax.grid(True)

        # Add values over each point
        for i, value in enumerate(inter_arrival_times, start=1):
            ax.text(i, value + 0.1, f"{value:.2f}", ha="center", va="bottom", color='black', fontsize = 8)

        return fig

    def show_inter_arrival_chart():
        fig = create_inter_arrival_chart()
        inter_arrival_window = tk.Toplevel()
        inter_arrival_window.title("Inter-Arrival Times")
        canvas = FigureCanvasTkAgg(fig, inter_arrival_window)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    # Create a dotted plot for customer vs. time
    def create_dotted_plot():
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.plot(range(1, len(arrival_times) + 1), arrival_times, marker='o', linestyle=':', color='g')
        ax.set_title("Customer Arrival Times")
        ax.set_xlabel("Customer Index")
        ax.set_ylabel("Arrival Time")
        ax.grid(True)

        # Add values over each point
        for i, value in enumerate(arrival_times, start=1):
            ax.text(i, value + 0.1, f"{value:.2f}", ha="center", va="bottom", color='black', fontsize = 8)

        return fig

    def show_dotted_plot():
        fig = create_dotted_plot()
        dotted_plot_window = tk.Toplevel()
        dotted_plot_window.title("Customer Arrival Times")
        canvas = FigureCanvasTkAgg(fig, dotted_plot_window)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    # Create frames for different rows of buttons
    gantt_frame = tk.Frame(chart_frame)
    gantt_frame.pack(side=tk.TOP, fill=tk.X)

    utilization_frame = tk.Frame(chart_frame)
    utilization_frame.pack(side=tk.TOP, fill=tk.X)

    time_frame = tk.Frame(chart_frame)
    time_frame.pack(side=tk.TOP, fill=tk.X)

    for server_idx in range(servers):
        gantt_button = tk.Button(chart_frame, text=f"Show Gantt Chart for Server {server_idx + 1}",
                                command=lambda idx=server_idx: show_gantt_chart(idx))
        gantt_button.pack(side=tk.TOP, padx=5, pady=5)

    inter_arrival_button = tk.Button(time_frame, text="Show Inter-Arrival Times", command=show_inter_arrival_chart)
    inter_arrival_button.pack(side=tk.TOP, padx=5, pady=5)  # Changed to side=tk.TOP

    dotted_plot_button = tk.Button(time_frame, text="Show Customer Arrival Times", command=show_dotted_plot)
    dotted_plot_button.pack(side=tk.TOP, padx=5, pady=5)  # Changed to side=tk.TOP
    
    utilization_button = tk.Button(chart_frame, text="Show Server Utilization", command=show_utilization_chart)
    utilization_button.pack(side=tk.TOP, padx=5, pady=5)

    turnaround_button = tk.Button(chart_frame, text="Show Turnaround Times", command=show_turnaround_chart)
    turnaround_button.pack(side=tk.TOP, padx=5, pady=5)

    waiting_button = tk.Button(chart_frame, text="Show Waiting Times", command=show_waiting_chart)
    waiting_button.pack(side=tk.TOP, padx=5, pady=5)

    response_button = tk.Button(chart_frame, text="Show Response Times", command=show_response_chart)
    response_button.pack(side=tk.TOP, padx=5, pady=5)
    

def main():
    root = tk.Tk()
    root.title("M/G/c Queue Simulator")
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    root.state("zoomed")
    root.geometry(f"{screen_width}x{screen_height}+0+0")

    input_frame = tk.Frame(root)
    input_frame.pack(side=tk.TOP, fill=tk.X)

    tk.Label(input_frame, text="Arrival Rate (λ):").grid(row=0, column=0, padx=5, pady=5)
    entry_lmbda = tk.Entry(input_frame)
    entry_lmbda.grid(row=0, column=1, padx=5, pady=5)

    tk.Label(input_frame, text="Number of Servers:").grid(row=0, column=2, padx=5, pady=5)
    entry_servers = tk.Entry(input_frame)
    entry_servers.grid(row=0, column=3, padx=5, pady=5)

    tk.Label(input_frame, text="Number of Customers:").grid(row=0, column=4, padx=5, pady=5)
    entry_arrivals = tk.Entry(input_frame)
    entry_arrivals.grid(row=0, column=5, padx=5, pady=5)

    tk.Label(input_frame, text="Service Distribution:").grid(row=0, column=6, padx=5, pady=5)
    dist_var = tk.StringVar(value="Normal")
    dist_menu = ttk.Combobox(input_frame, textvariable=dist_var, values=["Normal", "Uniform", "Gamma"])
    dist_menu.grid(row=0, column=7, padx=5, pady=5)

    tk.Label(input_frame, text="Dist. Parameters:").grid(row=0, column=8, padx=5, pady=5)
    entry_dist_params = tk.Entry(input_frame)
    entry_dist_params.grid(row=0, column=9, padx=5, pady=5)

    result_frame = ttk.Treeview(root, columns=("Customer", "Server", "Arrival Time", "Service Time", "Start Time", "End Time", "Turnaround Time", "Wait Time", "Response Time"), show="headings")
    for col in result_frame["columns"]:
        result_frame.heading(col, text=col)
        result_frame.column(col, width=100, anchor=tk.CENTER)
    result_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    vsb = tk.Scrollbar(root, orient="vertical", command=result_frame.yview)
    result_frame.configure(yscrollcommand=vsb.set)
    vsb.pack(side=tk.RIGHT, fill="y")

    chart_frame = tk.Frame(root)
    chart_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    def on_submit():
        if not entry_lmbda.get() or not entry_arrivals.get() or not entry_dist_params.get() or not entry_servers.get():
            messagebox.showerror("Input Error", "Please fill in all the fields before starting the simulation.")
            return
        for widget in chart_frame.winfo_children():
            widget.destroy()
        try:
            lmbda = float(entry_lmbda.get())
            servers = int(entry_servers.get())
            arrivals = int(entry_arrivals.get())
            dist_params = tuple(map(float, entry_dist_params.get().split()))

            simulate_mgc(
                lmbda,
                servers,
                arrivals,
                dist_var.get(),
                dist_params,
                result_frame,
                chart_frame
            )
        except ValueError:
            messagebox.showerror("Input Error", "Please enter valid numeric values.")

    submit_button = tk.Button(input_frame, text="Start Simulation", command=on_submit)
    submit_button.grid(row=0, column=10, columnspan=10, pady=10)

    root.mainloop()

if __name__ == "__main__":
    main()
