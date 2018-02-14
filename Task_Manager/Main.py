import numpy as np
from matplotlib.lines import Line2D
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.widgets import Button
import psutil

class Processor_Data(object):

    def __init__(self,chart,threads_number,maxtime=10,dt=0.75):
        self.maxtime = maxtime
        self.dt=dt
        self.time=[0]
        self.threads_number=threads_number
        self.cpu_usage=[[0]for y in range(threads_number)]
        self.chart=chart
        self.lines=[]
        for x in range(threads_number):
            line=Line2D(self.time,self.cpu_usage[x],color=self.color(x))
            self.lines.append(line)
            self.chart.add_line(line)

    def update_data(self,data):
        last_time=self.time[-1]
        if last_time>self.time[0]+self.maxtime or len(self.time)>10 and last_time>self.time[-11]+self.maxtime:
            self.chart.set_xlim([self.time[-11],self.time[-1]+1])

        t = self.time[-1] + self.dt
        self.time.append(t)
        for x in range(self.threads_number):
            self.cpu_usage[x].append(data[x])
            self.lines[x].set_data(self.time, self.cpu_usage[x])
        return self.chart,

    def get_data(self):
        while True:
            yield psutil.cpu_percent(interval=0.75,percpu=True)

    def color(self,value):
        if value == 0:
            return 'blue'
        elif value == 1:
            return 'green'
        elif value == 2:
            return 'purple'
        elif value == 3:
            return 'yellow'
        elif value == 4:
            return 'red'
        elif value == 5:
            return 'grey'

    def reset(self):
        self.lines=[]
        self.time=[]
        self.cpu_usage=[]

class Memory_Data(object):
    def __init__(self,bar):
        self.bar=bar

    def update_data(self,data):
        self.bar.set_height(data)
        return self.bar

    def get_data(self):
        while True:
            yield psutil.virtual_memory()[2]

class Manager(object):

    def __init__(self):
        self.fig, self.ax = plt.subplots()
        self.fig.set_size_inches(7.5, 7.5)
        self.ani = None
        m_button = plt.axes([0.4, 0.92, 0.1, 0.05])
        c_button = plt.axes([0.5, 0.92, 0.1, 0.05])
        n_button = plt.axes([0.6, 0.92, 0.1, 0.05])
        memory_button = Button(m_button,'Memory')
        cpu_button = Button(c_button,'CPU')
        network_button=Button(n_button,'Network')
        cpu_button.on_clicked(self.cpu_clicked)
        memory_button.on_clicked(self.mem_clicked)
        network_button.on_clicked(self.net_clicked)
        plt.show()

    def cpu_clicked(self,event):

        if self.ani != None:
            self.ani.event_source.stop()
        self.ax.cla()
        threads_number = psutil.cpu_count()
        self.ax.set_title('CPU USAGE')
        self.ax.set_ylim(0, 100)
        self.ax.set_xlim(0, 10)
        self.ax.set_xlabel('Time')
        self.ax.set_ylabel('Percent usage')
        proc = Processor_Data(self.ax, threads_number)
        self.ani = animation.FuncAnimation(self.fig, proc.update_data, proc.get_data, interval=10,
                                      blit=False)
        plt.show()

    def mem_clicked(self,event):

        if self.ani != None:
            self.ani.event_source.stop()
        self.ax.cla()
        self.ax.set_title('MEMORY USAGE')
        self.ax.set_ylim(0,100)
        self.ax.set_ylabel('Percent usage')
        rect, = self.ax.bar(1,0,color='blue')
        mem=Memory_Data(rect)
        self.ani = animation.FuncAnimation(self.fig,mem.update_data, mem.get_data, interval=100)
        plt.show()

    def net_clicked(self,event):
        plt.clf()


manager = Manager()
