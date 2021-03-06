# -*- coding: utf-8 -*-
"""
    lantz.drivers.newport.xpsq8
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Implementation of XPS Q8 controller
    NOTE: XPS_Q8_drivers.py must be placed within the same directory
    as this script

    Author: Kevin Miao
    Date: 12/16/2015
"""

from lantz.core import Action, DictFeat, Driver

# try:
#     from . import XPS_Q8_drivers
# except SystemError:
#     import XPS_Q8_drivers
import XPS_Q8_drivers


class XPSQ8(Driver):
    channels = ['X', 'Focus', 'Z']

    def __init__(self, address='192.168.0.254', port=5001, timeout=20.0):
        super(XPSQ8, self).__init__()
        self._xps = XPS_Q8_drivers.XPS()
        self._socket_id = self._xps.TCP_ConnectToServer(address, port, timeout)
        if self._socket_id == 1:
            self.log_error("Failed to establish XPS connection at {0}:{1}", address, port)
            # how do we proceed gracefully after this?

    @Action()
    def reboot(self):
        self._xps.Reboot(self._socket_id)
        return

    @Action()
    def rel_position(self, channel, dposition):
        retval = self._xps.GroupMoveRelative(self._socket_id, channel, [dposition])

    @Action()
    def jog(self, channel, velocity, acceleration):
        retval = self._xps.GroupJogParametersSet(self._socket_id, channel, [velocity], [acceleration])

    @Action()
    def home(self, channel):
        retval = self._xps.GroupHomeSearch(self._socket_id, channel)
        return retval

    @DictFeat(keys = channels, units = 'mm')
    def travel_limits(self, key):
        retval = self._xps.PositionerUserTravelLimitsGet(self._socket_id, key)
        
        #import traceback
        #fff = open('C:/Users/cmegroup/Desktop/errout.txt', 'w')
        #print(retval, file=fff)
        #print('\n', file=fff)
        #traceback.print_stack(file=fff)
        #fff.close()
        
        #return retval

    @DictFeat()
    def abs_position(self, channel):
        retval = self._xps.GroupPositionCurrentGet(self._socket_id, channel, 1)
        error, curpos = retval
        if error:
            raise ValueError
        return float(curpos)

    @abs_position.setter
    def abs_position(self, channel, position):
        retval = self._xps.GroupMoveAbsolute(self._socket_id, channel, [position])


def main():
    import logging
    import sys
    from lantz.log import log_to_screen
    import numpy as np
    log_to_screen(logging.CRITICAL)
    res_name = sys.argv[1]
   
    with XPSQ8(res_name) as inst:
        
        inst._xps.GroupJogModeEnable(inst._socket_id, 'X.Pos')
        value = inst._xps.GroupPositionCurrentGet(inst._socket_id, 'X.Pos', 1)
        print(value)
        value = inst._xps.GroupJogParametersGet(inst._socket_id, 'X.Pos', 1)
        # print(value)
        # ret = inst._xps.GroupJogParametersSet(inst._socket_id, 'X.Pos', [-0.0, ], [1.0, ])
        # print(ret)
        # value = inst._xps.GroupJogParametersGet(inst._socket_id, 'Focus.Pos', 1)
        # print(value)S
        # return
        # positions = np.linspace(-12.5, 12.5, 20)
        # for val in positions:
        #     print(val)
        #     inst.abs_position['X.Pos'] = val
        #     inst.abs_position['Focus.Pos'] = val
        #     inst.abs_position['Z.Pos'] = val
        #     print(inst.abs_position['X.Pos'])


if __name__ == '__main__':
    main()
