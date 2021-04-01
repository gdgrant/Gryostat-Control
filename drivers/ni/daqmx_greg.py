# Implementation of a simple Lantz driver for an NI DAQ, based on Gary's implementation
# Gregory Grant
# April 1, 2021

from lantz.core import Feat, Action, Driver
import nidaqmx

class daqmx(Driver):
    """ A simplified DAQ driver """

    def __init__(self, device_name):
        self._device_name = device_name # Something like 'Dev1'
        self._tasks = dict()

        self._analog_input_limits = [-10, 10] # volts
        self._analog_output_limtis = [-10, 10] # volts

    def finalize(self):
        """ Clears all tasks within the DAQ when Lantz unloads the driver """
        for k in self._tasks:
            self.task_clear(k)

    @Action()
    def clear_task(self, task_name):
        """ Given a task by name, remove it from the active tasks """
        task = self._tasks.pop(task_name)
        task.close()

    @Action()
    def add_task(self, task_name, ch_type, channels, vlimits=None, **kwargs):
        """ Adds a task to the DAQ, given the following:
                Task name : (string) the name of the described task, e.g. PL, light, freq_detector
                Channel type : (string) the type of channel - analog or digital, input or output,
                    as one of the four options (ai, ao, di, do)
                Channels : (list of strings) a list of the names of the channels associated with
                    this task, e.g. ao0, ai1, pfi0, etc.
                Voltage limits (optional) : (list of length 2 holding ints or floats) the limits
                    of the suggested task's channel(s), in volts -- first lower limit, then upper limit
        """

        # Clear this task if it has previously existed
        if task_name in self._tasks:
            self.task_clear(task_name)

        # Check what type of channel this is
        ch_types = ['ai', 'ao', 'di', 'do']
        if not ch_type in ch_types:
            raise Exception('Suggested task {} has invalid channel type {}.'.foormat(task_name, ch_type))

        # Create the interfacing task object
        task = nidaqmx.Task(task_name)

        # Iterate over provided channel names and associate
        # channels with the suggested task
        for ch in channels:

            ch_name = self._device_name + '/' + ch

            # Analog input channel type
            if chtype == 'ai':

                if vlimits is None:
                    vlimits = self._analog_input_limits

                task.ai_channels.add_ai_voltage_chan(ch_name, terminal_config=nidaqmx.constants.TerminalConfiguration.RSE, min_val=vlimits[0], max_val=vlimits[1])

            # Analog output channel type
            elif chtype == 'ao':

                if vlimits is None:
                    vlimits = self._analog_output_limtis

                task.ao_channels.add_ao_voltage_chan(ch_name, min_val=vlimits[0], max_val=vlimits[1])

            # Digital input channel type
            elif chtype == 'di':
                task.di_channels.add_di_chan(ch_name)

            # Digital output channel type
            elif chtype == 'do':
                task.do_channels.add_do_chan(ch_name)

        # Save the task to the internal task dictionary
        self._tasks[task_name] = task