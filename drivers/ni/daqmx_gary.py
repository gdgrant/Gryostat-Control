from lantz.core import Feat, Action, Driver
import nidaqmx

#TO IMPROVE: INSTEAD OF ACTION, MAKE A SORT OF DYNAMIC FEAT. RIGHT NOW READ/WRITE WILL NOT SAVE DATA

class daqmx(Driver):
    """
    This is a simplified version of a daq drivers
    """

    def __init__(self, device_name):
        self._device_name = device_name
        self._tasks = dict()

    def finalize(self):
        for k in self._tasks:
            self.task_clear(k)

    @Action()
    def task_add(self, task_name, chtype, channels, **kwargs):
        """Add a task to the DAQ

        Args:
            task_name ([str]): A name for the task at hand, e.g. PL
            chtype ([str]): ao (analog output), ai (analog input), do (digital output), di (digital input)
            channels ([list]): List of channels name, e.g. ao1, ai1, pfi0,...
        """
        if task_name in self._tasks:
            self.task_clear(task_name)

        task = nidaqmx.Task()
        if chtype == 'ao':
            for ch in channels:
                task.ao_channels.add_ao_voltage_chan(self._device_name + '/' + ch)
        elif chtype == 'ai':
            for ch in channels:
                if 'range' in kwargs.keys():
                    Vrange = kwargs['range']
                else:
                    Vrange = [-10,10]
                task.ai_channels.add_ai_voltage_chan(self._device_name + '/' + ch, task_name, nidaqmx.constants.TerminalConfiguration.RSE,Vrange[0],Vrange[1])
        elif chtype == 'do':
            for ch in channels:
                task.do_channels.add_do_chan(self._device_name + '/' + ch)
        elif chtype == 'di':
            for ch in channels:
                task.di_channels.add_di_chan(self._device_name + '/' + ch)
        else:
            raise Exception('Cannot identify the type of channel.')

        self._tasks[task_name] = task

    @Action()
    def task_clear(self, task_name):
        task = self._tasks.pop(task_name)
        task.close()