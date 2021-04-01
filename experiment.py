import time
import numpy as np

from nspyre.definitions import Q_
from nspyre.inserv.gateway import InservGateway
from nspyre.spyrelet.spyrelet import load_all_spyrelets, unload_all_spyrelets

### Setting up NSpyre environment ###

def get_instrument_manager():
	gateway = InservGateway()
	devices = gateway.hostcomp	# hostcomp = host name from client-config.yaml
	return gateway, devices
	

def refresh_spyrelets(gateway):
	
	try:
		unload_all_spyrelets()
		print('Spyrelets unloaded.')
	except:
		print('Spyrelet unloading failed.')
	
	all_spyrelets = load_all_spyrelets(gateway)
	print('Available spyrelets:', list(all_spyrelets.keys()))
	
	return all_spyrelets

gateway, devices = get_instrument_manager()
spyrelets = refresh_spyrelets(gateway)

print('\nReady\n')


### Describing manipulation of the XPS stage ###


def get_XPS_pos(field):
    
    # Check if valid dimension name
    if not field in ['X', 'Focus', 'Z']:
        raise Exception('{} not a valid position dimension name'.format(field))
    
    # Obtain absolute position and return
    return devices.XPS.abs_position[field]


def set_XPS_pos(field, val):

    # Check if valid dimension name
    if not field in ['X', 'Focus', 'Z']:
        raise Exception('{} not a valid position dimension name'.format(field))
    
    # Check if suggested position is within travel limits
    if np.abs(val) > 12.0:
        raise Exception('Travel limits of XPS are +/- 12 in any direction.  Movement to {}={} failed.'.format(field, val))
    
    # Send the new target position to the XPS
    devices.XPS.abs_position[field] = Q_(val, 'mm')
    
    # Allow some time for the movement to occur
    time.sleep(2)
    
def zero_XPS():
    
    print('Zeroing XPS location.')
    for field in ['X', 'Focus', 'Z']:
        set_XPS_pos(field, 0)
    print('Zeroing complete.\n')

def show_XPS_pos():

    print('Current XPS location:')
    for field in ['X', 'Focus', 'Z']:
        print('{} = {}'.format(field, get_XPS_pos(field)))
    print()


def discover_XPS():
    """ The XPS needs to be recognized before manipulations can start.
        This can be as simple as reading the position, and that's a good
        diagnostic anyway, so we do that here.  Run this function first. """
        
    print('Discovering XPS.  Current location:')
    show_XPS_pos()
    print('\n')
    time.sleep(0.1)


def abs_move_XPS(x=None, y=None, z=None):
    
    if x is not None:
        print('Moving X to {}'.format(x))
        set_XPS_pos('X', x)
    
    if y is not None:
        print('Moving Y to {}'.format(y))
        set_XPS_pos('Focus', y)
    
    if z is not None:
        print('Moving Z to {}'.format(z))
        set_XPS_pos('Z', z)


def rel_move_XPS(x=None, y=None, z=None):
    
    if x is not None:
        print('Moving X by {}'.format(x))
        pos = get_XPS_pos('X')._magnitude
        set_XPS_pos('X', x + pos)
    
    if y is not None:
        print('Moving Y by {}'.format(y))
        pos = get_XPS_pos('Focus')._magnitude
        set_XPS_pos('Focus', y + pos)
    
    if z is not None:
        print('Moving Z by {}'.format(z))
        pos = get_XPS_pos('Z')._magnitude
        set_XPS_pos('Z', z + pos)



discover_XPS()

zero_XPS()
show_XPS_pos()

abs_move_XPS(x=12.0)
show_XPS_pos()
rel_move_XPS(y=0.5)
show_XPS_pos()