# -*- coding: utf-8 -*-
"""
Created on Mon Jan  9 14:59:52 2023

@author: weber
"""

import pyvisa
import numpy as np


class SerialBase(object):

    def __init__(self):
        super().__init__()
        self._controller = None
        self._VISA_rm = pyvisa.ResourceManager()
        self.com_ports = self.get_ressources()

    @property
    def timeout(self):
        return self._timeout

    @timeout.setter
    def timeout(self, to):
        self._timeout = to
        self._controller.timeout = to

    def get_ressources(self):
        infos=self._VISA_rm.list_resources_info()
        com_ports = [infos[key].alias for key in infos.keys()]
        return com_ports
    
    def init_communication(self, com_port, axis=1):
        raise NotImplementedError('This method should be implemented in your real class')
        

    def close_communication(self, axis=1):
        self._controller.close()
        self._VISA_rm.close() 
        
    def get_controller_infos(self, axis=1):
        self._write_command(f'{axis}ID?')
        return self._get_read()

    def _query(self, command):
        ret = self._controller.query(command)
        return ret

    def _write_command(self, command):
        self._controller.write(command)

    
    def _get_read(self):
        self._controller.timeout = 50
        info = ''
        try:
            while True:
                info += self._controller.read()+'\n'
        except pyvisa.errors.VisaIOError as e:
            pass
        self._controller.timeout = self._timeout
        return info
    
    def move_axis(self, move_type='ABS', axis=1, pos=0.):
        if move_type == 'ABS':
            ret = self._write_command(f'{axis}PA{pos}')

        elif move_type == 'REL':
            ret = self._write_command(f'{axis}PR{pos}')
        else:
            raise Exception('{:s} is not a valid displacement type'.format(move_type))
        return ret

    def get_position(self, axis=1):
        """ return the given axis position always in mm
        """
        self._write_command(f'{axis}TP')
        pos = self._controller.read_ascii_values()[0]
        return pos

    def get_velocity(self, axis=1):
        self._write_command(f'{axis}VA?')
        pos = self._controller.read_ascii_values()[0]
        return pos

    def get_velocity_max(self, axis=1):
        self._write_command(f'{axis}VU?')
        pos = self._controller.read_ascii_values()[0]
        return pos

    def set_velocity(self, velocity, axis=1):
        self._write_command(f'{axis}VA{velocity}')


    def move_home(self, axis=1):
        self._write_command(f'{axis}OR1')

    def stop_motion(self, axis=1):
        self._write_command(f'{axis}ST')