#
#
# File repeater.py
#
#

import os
import time
from mesh_control import *


class Base_Station():
	def __init__( 	self, com_port, 
				rx_callback_cb = None, 
				modem_status_cb = None ):
		self.com_port = com_port
		self.remote_modem_dict = {}
		self.digiCmds = DigiCmds( com_port )
		self.digiCmds.register_rx_callback(  rx_callback_cb )   #parameters (  success_flag, address, data )
		self. digiCmds.modem_status_callback( modem_status_cb ) # parameters( status )
		self.digiCmds.reset_modem()
		self.digiCmds.clear_diagnostics()
		self.address = self.digiCmds.get_serial_number()
		
	def get_modem_id( self ):
			return [ self.digiCmds.ni, self.digiCmds.serial_number ]
			
	def poll_modem( self,  time_delay = 1. ):
		self.digiCmds.receive_serial_data( timeout = time_delay)
	
	# Remote Node Maintaince 
	
	def clear_remote_modem_list( self ):
		self.remote_modem_dict = {}
		
	def add_remote_element( self, name, node_type= True ):
		temp  				= {}
		temp["name"] 			= name
		temp["node_type"] 	   	= node_type  # off and will be only active only at descresion of  remote nodes
		temp["address"]		= None
		temp["rfi"]			= None
		temp["online_status"]  	= None
		self.remote_modem_dict[ name ] = temp
		# add parameters as needed
	
	def get_remote_modem_list( self, remote_modem_list ):
		return self.remote_modem_list
	
	# return list of names which are offline and list of foriegn nodes
	def locate_remote_modems( self ):
		offline_elements = {}
		foriegn_elements = {}
		nodes_found = self.digiCmds.discover_nodes()
		print "nodes found",nodes_found
		for i in self.remote_modem_dict.keys():
			print "i",i
			self.remote_modem_dict[i]["online_status"] = False
		for name in nodes_found.keys():
			address  = nodes_found[name] 
			if self.remote_modem_dict.has_key(name):
				self.remote_modem_dict[ name]["address"] = address
				self.remote_modem_dict[name]["online_status"] = True
			else:
				foriegn_elements[ name] = address
		for i in self.remote_modem_dict.keys():
			if self.remote_modem_dict[i]["online_status"] == False:
				offline_elements[i] = self.remote_modem_dict[i]
				
		return  [ offline_elements, foriegn_elements ]
			
	def locate_single_modem( self, name ):
		status = self.digiCmds.discover_single_node( name )
		if (status != None ) and ( self.remote_modem_dict.has_key( name ) == True ):
			self.remote_modem_dict[name]["address"] = status
			self.remote_modem_dict[name]["online_status"] = True
		return status
	
	def change_tx_registers( self, name_list ):
		return_list = []
		for i in name_list:
			status1 = self.digiCmds.send_remote_at_message( i, "DH", self.address[0:4], frame_id= 1, retries = 3, up_date_flag = True)
			status2 = self.digiCmds.send_remote_at_message( i, "DH", self.address[4:], frame_id= 1, retries = 3, up_date_flag = True)
			if ( status1[0] == True ) and ( status2[0] == True ):
				return_list.append(True)
			else:
				return_list.append(False)
		return return_list

	def get_remote_diagnostics( self , name_list ):
		
		for i in name_list:
			x = self.digiCmds.diagnostics_remote( i )
			if (x[0] == True ) and ( self.remote_modem_dict.has_key(i) == True ):
				print i, x[1]
				self.remote_modem_dict[i]["diagnostics"] = x[1]
			self.digiCmds.clear_diagnostics_remote(i)
	
	#return list of of successful messages
	def transmit_messages( self, name_list, message ):
		success_list = {}
		for i in name_list:
			if (self.remote_modem_dict.has_key(i) == True) and ( self.remote_modem_dict[i]["online_status"] == True ):
				status = self.digiCmds.send_TX_name_msg(  i, message , retries = 3, frame_id = 1)
				success_list[i] = status[0]
			else:
				success_list[i] = False
		return success_list
			
if __name__== "__main__" :

	def rx_callback_cb( success_flag, address, data ):
		print "rx callback ----------->",success_flag, address, data
		

	# 0x00  Hardware Reset
	# 0x01  Watchdog Reset
	# 0x0B  Network Woke Up
	# 0x0C  Network Went to Sleep

	def modem_status_cb( status ): 
		print "modem status callback ------------------->", status

	x = Base_Station("com3", rx_callback_cb, modem_status_cb )
	print "modem id", x.get_modem_id()			
	x.clear_remote_modem_list()
	x.add_remote_element( "test_2", True )	
	x.add_remote_element( "test_3", True )	
	#print "locate remote names", x.locate_remote_modems( )
	print "locate node test_2", x.locate_single_modem("test_2")
	#print "locate node test_3", x.locate_single_modem("test_3")
	#print x.change_tx_registers( ["test_2"] )
	#print x.get_remote_diagnostics( ["test_2"] )
	print x.transmit_messages( ["test_2","test_3"] ,[0x10,0x20,0x30,0x40,0x50,0x60,0x70,0x80] )


					
