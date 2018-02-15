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
            line=Line2D(self.time,self.cpu_usage[x],color=self.color(x),label=str(x) + 'thread')
            self.lines.append(line)
            self.chart.add_line(line)

    def update_data(self,data):
        self.chart.legend(bbox_to_anchor=(1, 1), loc=1, borderaxespad=0.)
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
        elif value==6:
            return 'brown'
        elif value==7:
            return 'orange'


class Memory_Data(object):

    def __init__(self,bar,ax):
        self.bar=bar
        self.ax=ax

    def update_data(self,data):
        self.bar.set_height(data[2])
        self.ax.text(0.85, 20, 'Current RAM usage: '+ str(data[2])+ '% ' , style='italic',
                bbox={'facecolor': 'red', 'alpha': 0.6, 'pad': 10})
        ram_used=data[3]
        ram_used=round(data[3]/1000000000,2)
        self.ax.text(0.85, 10, 'Current RAM usage: ' + str(ram_used) + 'GB', style='italic',
                     bbox={'facecolor': 'red', 'alpha': 0.6, 'pad': 10})
        return self.bar

    def get_data(self):
        while True:
            yield psutil.virtual_memory()

class Temperature_Data(object):

    def __init__(self,bar,ax):
        self.bar=bar
        self.ax=ax
        self.thread_num=psutil.cpu_count(logical=False)

    def update_data(self,data):
        for x in range (self.thread_num):
            tmp=data['coretemp'][x+1][1]
            self.ax.text(0.15+x, 10, 'Core: ' +str(x)+' temperature= '+ str(tmp) + ' C', style='italic',
                         bbox={'facecolor': 'red', 'alpha': 0.25, 'pad': 5})
            self.bar[x][0].set_height(tmp)
            if tmp >80:
                self.bar[x][0].set_color('y')
                if tmp> 90:
                    self.bar[x][0].set_color('r')
            else:
                self.bar[x][0].set_color('g')
        return self.bar

    def get_data(self):
        while True:
            yield psutil.sensors_temperatures()


class Manager(object):

    def __init__(self):
        self.fig, self.ax = plt.subplots()
        self.fig.set_size_inches(7.5, 7.5)
        self.ani = None
        m_button = plt.axes([0.35, 0.92, 0.1, 0.05])
        c_button = plt.axes([0.45, 0.92, 0.1, 0.05])
        t_button = plt.axes([0.55, 0.92, 0.1, 0.05])
        self.fig.canvas.set_window_title('Task Manager')
        memory_button = Button(m_button,'Memory')
        cpu_button = Button(c_button,'CPU')
        temp_button = Button(t_button,'t of CPU')
        cpu_button.on_clicked(self.cpu_clicked)
        memory_button.on_clicked(self.mem_clicked)
        temp_button.on_clicked(self.temp_clicked)
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
        self.ani = animation.FuncAnimation(self.fig, proc.update_data, proc.get_data, interval=10)
        plt.show()

    def mem_clicked(self,event):

        if self.ani != None:
            self.ani.event_source.stop()
        self.ax.cla()
        self.ax.set_title('MEMORY USAGE')
        self.ax.set_ylim(0,100)
        self.ax.set_xlim(0.5,1.5)
        self.ax.set_ylabel('Percent usage')
        rect, = self.ax.bar(1,0,color='blue')
        mem=Memory_Data(rect,self.ax)
        self.ani = animation.FuncAnimation(self.fig,mem.update_data, mem.get_data, interval=100)
        plt.show()

    def temp_clicked(self,event):

        if self.ani != None:
            self.ani.event_source.stop()
        self.ax.cla()
        self.ax.set_title('Temperature per core')
        self.ax.set_ylim(0, 100)
        x_size=psutil.cpu_count(logical=False)
        self.ax.set_xlim(0,x_size)
        self.ax.set_ylabel('Temperature in Celsius')
        bars =[]
        for x in range (psutil.cpu_count(logical=False)):
            bars.append(self.ax.bar(x+0.5,0,color='green'))

        temp=Temperature_Data(bars,self.ax)
        self.ani= animation.FuncAnimation(self.fig,temp.update_data, temp.get_data, interval=100)
        plt.show()

if __name__ == "__main__":
    manager = Manager()
