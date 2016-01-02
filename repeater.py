#
#
# File repeater.py
#
#

import os
import time
from mesh_control import *


class Repeater():
	def __init__( self, com_port, 
				rx_callback_cb = None, 
				modem_status_cb = None ):
		self.com_port = com_port
		self.digiCmds = DigiCmds( com_port )
		self.digiCmds.register_rx_callback(  rx_callback_cb )   #parameters (  success_flag, address, data )
		self. digiCmds.modem_status_callback( modem_status_cb ) # parameters( status )
		self.digiCmds.reset_modem()
		self.digiCmds.clear_diagnostics()
		

	def get_modem_id( self ):
			return [ self.digiCmds.ni, self.digiCmds.serial_number ]
			
	def poll_modem( self,  time_delay = 1. ):
		self.digiCmds.receive_serial_data( timeout = time_delay)
		
if __name__== "__main__" :
	
	def rx_callback_cb( success_flag, address, data ):
		print "rx callback ----------->",success_flag, address, data
		

	# 0x00  Hardware Reset
	# 0x01  Watchdog Reset
	# 0x0B  Network Woke Up
	# 0x0C  Network Went to Sleep

	def modem_status_cb( status ): 
		print "modem status callback ------------------->", status

	x = Repeater( "COM12", 
				rx_callback_cb       = rx_callback_cb,
				modem_status_cb  = modem_status_cb )
	
	print "modem id", x.get_modem_id()			
	
	
	while( True ):
		x.poll_modem()