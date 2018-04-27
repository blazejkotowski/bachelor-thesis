import numpy as np
import matplotlib.pyplot as plt

class Graph:
  def __init__(self, enabled, realtime, history = 0):
    self.realtime = realtime
    self.enabled = enabled
    self.history = history
    self.fig = plt.figure(figsize=(14, 10))
    self.ax1 = self.fig.add_subplot(331)
    self.ax1.set_ylim([-1.3 * np.pi, 1.3 * np.pi])
    self.__set_xlim(self.ax1)
    self.ax1.set_title('sync signal')
    self.sync_graph = self.ax1.plot([], color='b')[0]

    self.axes = [ self.fig.add_subplot(330 + i + 2) for i in range(0, 8) ]
    for idx, axis in enumerate(self.axes):
      axis.set_ylim([-1.3 * np.pi, 1.3 * np.pi])
      self.__set_xlim(axis)
      axis.set_title('carrier signal {0}'.format(idx))
    self.carrier_graphs = [ axis.plot([], color='g')[0] for axis in self.axes ]
    if self.enabled and self.realtime:
      plt.ion()
      self.redraw()
      plt.show()

  def redraw(self):
    if self.enabled and self.realtime:
      plt.draw()

  def show(self):
    if self.enabled:
      plt.draw()
      plt.show()

  def set_sync_signal(self, sync_signal):
    self.sync_graph.set_data(range(0, len(sync_signal)), sync_signal)
    self.__set_xlim(self.ax1, len(sync_signal))

  def set_carrier_signals(self, signals):
    for idx, signal in enumerate(signals):
      self.carrier_graphs[idx].set_data(range(0, len(signal)), signal)
      self.__set_xlim(self.axes[idx], len(signal))

  def set_sync_byte(self, idx, average, std_dev, carrier_averages, carrier_std_devs):
    if self.enabled:
      self.ax1.axvline(idx, color='#dddddd')
      self.ax1.errorbar([idx], [average], color='r', marker='.', yerr=[std_dev])
      for axisidx, axis in enumerate(self.axes):
        axis.axvline(idx, color='#dddddd')
        axis.errorbar([idx], [carrier_averages[axisidx]], color='r', marker='.', yerr=[carrier_std_devs[axisidx]])

  def set_sync_frame(self, idx):
    if self.enabled:
      self.ax1.axvline(idx, color='r')

  def __set_xlim(self, axis, length = 0):
    if self.history == 0:
      axis.set_xlim([0, length+1])
    else:
      axis.set_xlim([length-self.history, length])

