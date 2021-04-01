# -*- coding: utf-8 -*-
"""
    lantz.drivers.newport.xpsq8
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Implementation of XPS Q8 controller for Lantz
    NOTE: Assumes that XPS_Q8_drivers.py is be placed within the same directory as this script

    Author: Manish Singh
    Date: 03/23/2021
"""

from lantz.core import Action, DictFeat, Driver
import XPS_Q8_drivers
# use the following if importing this class directly
# from . import XPS_Q8_drivers

class XPSQ8(Driver):
    channels = ['X', 'Focus', 'Z']
    # actual names of the channels for newport is ['X.pos', 'Focus.pos', 'Z.pos']

    def __init__(self, address='192.168.0.254', port=5001, timeout=20.0):
        super(XPSQ8, self).__init__()
        self._xps = XPS_Q8_drivers.XPS()
        self._socket_id = self._xps.TCP_ConnectToServer(address, port, timeout)
        if self._socket_id == -1:
            self.log_error("Failed to establish XPS connection at {0}:{1}", address, port)

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

    @DictFeat(keys=channels, units='mm')
    def travel_limits(self, key):
        # retval, travelMin, travelMax = self._xps.PositionerUserTravelLimitsGet(self._socket_id, key+'.Pos')
        # return retval
        retval,minV,maxV = self._xps.PositionerUserTravelLimitsGet(self._socket_id, key+'.Pos')
        return float(maxV)
        
    @DictFeat(keys=channels, units='mm')
    def abs_position(self, key):
        retval = self._xps.GroupPositionCurrentGet(self._socket_id, key+'.Pos', 1)
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
