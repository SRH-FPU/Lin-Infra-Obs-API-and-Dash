# Designed with https://visualtkinter.com - paste this file into File > Import there to edit it visually
import time
import paramiko, json, asyncio
import tkinter as tk
from async_tkinter_loop import async_handler, async_mainloop
from tkinter import ttk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from numpy.f2py.crackfortran import endifs
from sqlalchemy import false

# Setup
vmUser = "obsAPI"
privatekey_path = "C:\\Users\\srhsi\\.ssh\\obsAPI-ssh-key"
remotejson_path = "/var/lib/observationAPI/observationAPI.json"

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ticksA = [10,20,30,40,50,60,70,80,90,100]
ticksB = ["10%","20%","30%","40%","50%","60%","70%","80%","90%","100%"]


class Application:
    def __init__(self, root):
        self.root = root
        root.title("Remote Dashboard")
        root.geometry("1000x470")
        self.cpuX = []
        self.cpuY = []

        self.ramX = []
        self.ramY = []

        self.diskX = []
        self.diskY = []

        self.netUpX = []
        self.netUpY = []

        self.netDownX = []
        self.netDownY = []

        self.serverIP_var = tk.StringVar()
        self.doJsonParsing = False

        self.serverIP = tk.Entry(root, textvariable=self.serverIP_var, show="*")
        self.serverIP.place(x=20, y=420, width=90, height=40)

        self.cpu_chart = FigureCanvasTkAgg(Figure(figsize=(3.20, 2.20), dpi=100, layout="constrained"), master=root)
        self.cpu_chart_axes = self.cpu_chart.figure.add_subplot(111)
        self.cpu_chart_axes.set_title("CPU Usage")
        self.cpu_chart.draw()
        self.cpu_chart.get_tk_widget().place(x=10, y=10, width=320, height=220)

        self.ram_chart = FigureCanvasTkAgg(Figure(figsize=(3.20, 2.20), dpi=100, layout="constrained"), master=root)
        self.ram_chart_axes = self.ram_chart.figure.add_subplot(111)
        self.ram_chart_axes.set_title("Memory Usage")
        self.ram_chart.draw()
        self.ram_chart.get_tk_widget().place(x=340, y=10, width=320, height=220)

        self.disk_chart = FigureCanvasTkAgg(Figure(figsize=(3.20, 2.20), dpi=100, layout="constrained"), master=root)
        self.disk_chart_axes = self.disk_chart.figure.add_subplot(111)
        self.disk_chart_axes.set_title("Disk Usage")
        self.disk_chart.draw()
        self.disk_chart.get_tk_widget().place(x=670, y=10, width=320, height=220)
        self.disk_chart_axes.set_ylim(0, 220)

        self.upload_chart = FigureCanvasTkAgg(Figure(figsize=(3.20, 2.20), dpi=100, layout="constrained"), master=root)
        self.upload_chart_axes = self.upload_chart.figure.add_subplot(111)
        self.upload_chart_axes.set_title("Upload")
        self.upload_chart.draw()
        self.upload_chart.get_tk_widget().place(x=670, y=240, width=320, height=220)

        self.download_chart = FigureCanvasTkAgg(Figure(figsize=(3.20, 2.20), dpi=100, layout="constrained"), master=root)
        self.download_chart_axes = self.download_chart.figure.add_subplot(111)
        self.download_chart_axes.set_title("Download")
        self.download_chart.draw()
        self.download_chart.get_tk_widget().place(x=340, y=240, width=320, height=220)

        self.cpuButton = tk.Button(root, text="Stress CPU", command=async_handler(self.on_cpuButton))
        self.cpuButton.place(x=20, y=240, width=150, height=50)

        self.ramButton = tk.Button(root, text="Stress Memory", command=async_handler(self.on_ramButton))
        self.ramButton.place(x=180, y=240, width=140, height=50)

        self.networkButton = tk.Button(root, text="Stress Network", command=async_handler(self.on_networkButton))
        self.networkButton.place(x=180, y=300, width=140, height=50)

        self.diskButton = tk.Button(root, text="Stress Disk", command=async_handler(self.on_diskButton))
        self.diskButton.place(x=20, y=300, width=150, height=50)

        self.Maximum_Overdrive = tk.Button(root, text="Stress All", command=async_handler(self.on_Maximum_Overdrive))
        self.Maximum_Overdrive.place(x=20, y=360, width=300, height=50)

        self.connectionButton = tk.Button(root, text="Connect", command=async_handler(self.on_connectionButton))
        self.connectionButton.place(x=120, y=420, width=100, height=40)

        self.disconnect = tk.Button(root, text="Disconnect", command=async_handler(self.on_disconnect))
        self.disconnect.place(x=230, y=420, width=90, height=40)

    async def on_cpuButton(self):
        client.exec_command("sudo stress --quiet --cpu 2 --timeout 10")

    async def on_ramButton(self):
        client.exec_command("sudo stress --vm 2 --timeout 10")

    async def on_networkButton(self):
        pass

    async def on_diskButton(self):
        pass

    async def on_Maximum_Overdrive(self):
        await self.on_cpuButton()
        await self.on_ramButton()
        await self.on_networkButton()
        await self.on_diskButton()

    async def plot_cpu_chart(self, x, y):
        """Redraw the chart from two equal-length sequences."""
        self.cpuX.append(x)
        self.cpuY.append(y)
        self.cpu_chart_axes.clear()
        self.cpu_chart_axes.plot(self.cpuX, self.cpuY, 'o', '-', 'blue')
        self.cpu_chart_axes.set_ylim(0.0,100.0)
        self.cpu_chart_axes.set_ybound(0.0, 100.0)
        self.cpu_chart_axes.set_yticks(ticksA, ticksB)
        self.cpu_chart_axes.set_title("CPU Usage")
        self.cpu_chart.draw()

    async def plot_ram_chart(self, x, y):
        """Redraw the chart from two equal-length sequences."""
        self.ramX.append(x)
        self.ramY.append(y)
        self.ram_chart_axes.clear()
        self.ram_chart_axes.plot(self.ramX, self.ramY, 'o', '-', 'blue')
        self.ram_chart_axes.set_ylim(0.0, 100.0)
        self.ram_chart_axes.set_ybound(0.0, 100.0)
        self.ram_chart_axes.set_yticks(ticksA,ticksB)
        self.ram_chart_axes.set_title("Memory Usage")
        self.ram_chart.draw()

    async def plot_disk_chart(self, x, y):
        """Redraw the chart from two equal-length sequences."""
        self.diskX.append(x)
        self.diskY.append(y)
        self.disk_chart_axes.clear()
        self.disk_chart_axes.plot(self.diskX, self.diskY, 'o', '-', 'blue')
        self.disk_chart_axes.set_title("Storage Usage")
        self.disk_chart.draw()

    async def plot_upload_chart(self, x, y):
        """Redraw the chart from two equal-length sequences."""
        self.netUpX.append(x)
        self.netUpY.append(y)
        self.upload_chart_axes.clear()
        self.upload_chart_axes.plot(self.netUpX, self.netUpY, 'o', '-', 'blue')
        self.upload_chart_axes.set_title("Upload")
        self.upload_chart.draw()

    async def plot_download_chart(self, x, y):
        """Redraw the chart from two equal-length sequences."""
        self.netDownX.append(x)
        self.netDownY.append(y)
        self.download_chart_axes.clear()
        self.download_chart_axes.plot(self.netDownX, self.netDownY, 'o', '-', 'blue')
        self.download_chart_axes.set_title("Download")
        self.download_chart.draw()

    async def gatherTelemetry(self):
        startTime = time.time()
        while self.doJsonParsing:
            remoteFileSys = client.open_sftp()

            file_path = "observationAPI.json"
            try:
                with remoteFileSys.open(remotejson_path, "r") as file:
                    data = json.load(file)

                # Extract and print each key and its corresponding value
                cpu = data.get("cpu")
                mem = data.get("mem")
                disk = data.get("disk")
                net_down = data.get("netDown")
                net_up = data.get("netUp")

                await self.plot_cpu_chart(time.time()-startTime,int(cpu))
                await self.plot_ram_chart(time.time() - startTime, int(mem))
                await self.plot_disk_chart(time.time() - startTime, int(disk))
                await self.plot_upload_chart(time.time() - startTime, int(net_down))
                await self.plot_download_chart(time.time() - startTime, int(net_up))

            finally:
                pass
            await asyncio.sleep(1)

    async def on_connectionButton(self):
        self.cpuX.clear()
        self.cpuY.clear()
        self.ramX.clear()
        self.ramY.clear()
        self.diskX.clear()
        self.diskY.clear()
        self.netUpX.clear()
        self.netUpY.clear()
        self.netDownX.clear()
        self.netDownY.clear()
        try:
            client.connect(
                hostname=self.serverIP_var.get(),
                username=vmUser,
                key_filename=privatekey_path,
                passphrase="tbabs",
                timeout=10
            )
            self.doJsonParsing = True
            await self.gatherTelemetry()
        finally:
            pass

    async def on_disconnect(self):
        self.doJsonParsing = False
        client.close()


if __name__ == "__main__":
    root = tk.Tk()
    app = Application(root)
    async_mainloop(root)
    client.close()
