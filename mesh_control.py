
import time
import os
from packet_operations import *
from serial_operations import *


class DigiCmds():
	
	def __init__( self, com_port, serial_port_time_out = .25, at_time_default = .1 ):
		self.digi_packet   = Packet_Ops()
		self.digi_serial     = DigiSerial( com_port , self.digi_packet, .25 )
		self.node_list       = {}
		self.rx_callback_cb = None
		self.modem_status_cb = None
		self.initialize(at_time_default)
####################################################################################
#
#	Initialization and house keeping methods
#
####################################################################################

	def initialize( self, at_time_default ):
		self.at_time_default = at_time_default
		self.at_time = {}
		self.serial_number = self.get_serial_number()
		self.nt = self.get_nt()
		self.ni  = self.get_ni()
		self.at_time[ "DN"] = self.nt + 10
		self.at_time["ND"]  = self.nt + 10


	def get_timeout( self, cmd):
		if self.at_time.has_key(cmd ) == True:
			return self.at_time[ cmd ]
		else:
			return  self.at_time_default
			
	def get_node_table( self ):
		return self.node_list      
		
	def get_nt( self ):
		temp =  self.send_at_message( "NT")
		return (temp[1][0]*256+temp[1][1])*.1
		
	def reset_modem( self ):
		temp =  self.send_at_message( "FR")
		time.sleep(1)
		return temp[0]
	
	def set_ni( self, name):
		temp = list(name)
		for i in range(0, len(temp)):
			temp[i] = ord(temp[i])
		temp.append(0)
		temp = self.send_at_message("NI",parameters = temp )
		return temp[2]
	
	def get_ni( self ):
		temp = self.send_at_message("NI")
		#print "temp",temp
		for i in range(0,len(temp[1] )):
			temp[1][i] = chr(temp[1][i])
		#print "temp",temp
		self.ni = "".join(temp[1])
		return self.ni


		
	def get_serial_number( self ):
		return_value = None
		data = self.send_at_message( "SH")
		if data[ 0 ] == True:
			return_value = data[1]
			data = self.send_at_message("SL")
			if data[0] == True:
			   return_value.extend(data[1])
		return return_value
			   
		
	def diagnostics( self ):
		return_value = {}
		return_value["BC"] =  self.generate_number( self.send_at_message( "BC"))
		return_value["DB"] =  self.generate_number(self.send_at_message( "DB" ))
		return_value["ER"] =  self.generate_number(self.send_at_message( "ER"))
		return_value["GD"] =  self.generate_number(self.send_at_message( "GD"))
		return_value["EA"] =  self.generate_number(self.send_at_message("EA"))
		return_value["TR"] =  self.generate_number(self.send_at_message("TR"))
		return return_value
	
	def clear_diagnostics( self ):
		self.send_at_message( "BC",[0])
		self.send_at_message( "DB" ,[0])
		self.send_at_message( "ER",[0])
		self.send_at_message( "GD",[0])
		self.send_at_message("EA",[0])
		self.send_at_message("TR",[0])
		
	def generate_number( self, data ):
		#print "data",data
		if data[0] == False:
			return 0
		temp = data[1]
		temp.reverse()
		scale = 1
		sum  = 0
		for i in temp:
			sum = sum + i * scale
			scale =scale*256
		return sum
			
			
		
	def diagnostics_remote( self, name ):
		if self.node_list.has_key( name ) == True:
			return_value = {}
			return_value["BC"] =  self.generate_number(self.send_remote_at_message(name, "BC"))
			return_value["DB"] =  self.generate_number(self.send_remote_at_message(name, "DB" ))
			return_value["ER"] =  self.generate_number(self.send_remote_at_message( name,"ER"))
			return_value["GD"] =  self.generate_number(self.send_remote_at_message(name, "GD"))
			return_value["EA"] =  self.generate_number(self.send_remote_at_message(name,"EA"))
			return_value["TR"] =  self.generate_number(self.send_remote_at_message(name,"TR"))
			return [ True, return_value]
		else:
			return [ False, None ]
		
	
	def clear_diagnostics_remote( self, name):
		if self.node_list.has_key( name ) == True:
			self.send_remote_at_message( name,"BC",[0])
			self.send_remote_at_message(name, "DB" ,[0])
			self.send_remote_at_message( name,"ER",[0])
			self.send_remote_at_message( name, "GD",[0])
			self.send_remote_at_message(name,"EA",[0])
			self.send_remote_at_message(name,"TR",[0])

####################################################################################
#
#Receive Message Methods
#
###################################################################################
	
	#command is used to receive data  
	def receive_serial_data(self, timeout = 10, size = 10):
	    data = self.digi_serial.receive_data( time_out = timeout, size= size)
	    for i in data:
		if i[0] == True:
			self.process_async_messages( i[1] )
	       
	def modem_status_callback( self, modem_status_cb ): # parameters( status )
		self.modem_status_cb = modem_status_cb
	
	def register_rx_callback( self, rx_callback_cb ): #parameters (  success_flag, address, data )
		self.rx_callback_cb = rx_callback_cb
		
	def process_async_messages( self, data ):

		
		if data["frame_type"] == 0x8a:
			
    			if self.modem_status_cb != None:
					
					self.modem_status_cb( data["status" ] )
					
		elif (data["frame_type"] == 0x90) or ( data["frame_type"]  == 0x91 ):
			
			if (data["receive_option"] & 1) != 0:
				flag = True
			else:
				flag = False
			if self.rx_callback_cb != None:
				self.rx_callback_cb(  flag , data["address"], data["data"] )

		return [ False, None ]
	
####################################################################################
#
# Node Discovery Methods
# Note:  These commands donot return right away.  Instead they return in 10's of seconds as this is the search time of the modem
#
#####################################################################################
	def discover_single_node( self, node ):
		temp = list(node)
		for i in range(0, len( temp )):
			temp[i] = ord(temp[i])
		temp.append(0)
		temp =self.send_at_message("DN",parameters = temp )

		if (len(temp[1]) == 10  ) :
			
			address = temp[1][2:]
			self.node_list[node] = address
			
		else:
			if self.node_list.has_key(node) == True:
				del( self.node_list[node])
			address = None
		return address
		
	def parse_node_stream( self, packet_data ):
		return_value = []
		if( packet_data[ "frame_type" ] == 136 ) and ( packet_data["at_command"][0] == 'N') and ( packet_data["at_command"][1] == 'D' ):
			return_value.append(True)
			temp = packet_data["command_data"]
			return_value.append( temp[2:10] )
			name = ""
			for i in range( 10, len(temp)):
				if temp[i] != 0:
					name = name + chr(temp[i])
				else:
					return_value.append(name)
					return return_value
		else:
			return_value.append(False)
		return return_value
		
	def discover_nodes( self ):
		return_value = {}
		self.node_list       = {}
		timeout_temp = self.digi_serial.serial.timeout
	
		data = self.digi_packet.generate_AT_cmd( "ND" )
		
		self.digi_serial.send_command(data)	
		time_out = self.get_timeout( "ND")
		
		packets = self.digi_serial.receive_data( time_out = time_out, size = 10, change_time_out = False)
		
		for i in packets:
			if i[0] == True:
				status = self.parse_node_stream( i[1] )
				if status[0] == False:
					self.process_async_messages( i[1] )
				else:
					self.node_list[status[2]] = status[1]
					return_value[ status[2] ] = status[1]
				
		self.digi_serial.serial.timeout = timeout_temp
		return return_value
	
	# not sure how useful this command is
	def aggregate_node( self, node_name ):
		if self.node_list.has_key( node_name ) == True:
			address = self.node_list[ node_name ]
			timeout_temp = self.digi_serial.serial.timeout
			self.digi_serial.serial.timeout = self.nt +10
			temp =self.send_at_message("AG",parameters = address )
			self.digi_serial.serial.timeout = timeout_temp
			
			if temp[2] == 0:
				return True
			else:
				return False
		else:
			return False

####################################################################################
#
# Sending AT Commands
#
####################################################################################


	def send_at_message( self, cmd, parameters= None, frame_id= 1, retries = 3):
		for i in range( 0, retries ):
		        return_value = self.send_single_at_message( cmd, parameters, frame_id )
			if return_value[0] == True:
				return return_value
			frame_id = frame_id +1
		return [ False, None ]  #### This means no command response from modem
		
	def send_single_at_message( self, cmd, parameters, frame_id ):
		data = self.digi_packet.generate_AT_cmd( cmd, parameters, frame_id = frame_id )
		self.digi_serial.send_command(data)
		time_out = self.get_timeout( cmd)
		data = self.digi_serial.receive_data(time_out = time_out, size = 5)
		#print "data",data
		return_value = [ False, None ]
		for i in data:
			#print "i",i
			if ( i != None) and ( i[0] == True):
				j = i[1]
				if  ( j[ "frame_type" ] == 136 ) and ( j["frame_id"] == frame_id)  and ( j["at_command"][0] == cmd[0]) and ( j["at_command"][1] == cmd[1]  ) :
					
					return_value =  [ True, j["command_data"],j["command_status" ]]
				
				else:
					self.process_async_messages( i[1] )
					#print "return value",return_value
		return return_value		
	
		
	
####################################################################################
#
#Sending Remote AT Commands
#
#####################################################################################



		
	def send_remote_at_message( self, node_name, cmd, parameters= None, frame_id= 1, retries = 3, up_date_flag = True):

		if self.node_list.has_key(node_name) == False:
			return [ False, None ]
		
		address = self.node_list[ node_name ]
			
		for i in range( 0, retries ):
		        return_value = self.send_single_remote_message( address, cmd, parameters, frame_id , up_date_flag )
			if return_value[0] == True:
				return return_value
			frame_id = frame_id +1
		return [ False, None ]
		
	def send_single_remote_message( self, address, cmd, parameters, frame_id,update_flag ):
		data = self.digi_packet.generate_Remote_cmd( address, cmd, parameters =parameters, frame_id = frame_id, update_flag = update_flag)
		self.digi_serial.send_command(data)

		data = self.digi_serial.receive_data(time_out = 3.0, size = 5 )
		#print "data",data
		return_value = [ False, None ]
		for i in data:
			if i != None:
				j = i[1]
				if  ( j[ "frame_type" ] == 151 ) and ( j["frame_id"] == frame_id)  and ( j["at_command"][0] == cmd[0]) and ( j["at_command"][1] == cmd[1]  ) :
					return_value =  [ True, j["command_data"],j["command_status" ]]
				
			else:
			    self.process_async_messages( i[1] )
			#print "return value",return_value
		return return_value		

#####################################################################################
#
# Sending TX messages
# Time out for Serial Messages is default 3 seconds
#
#######################################################################################

	def send_TX_name_msg( self, name, tx_data, frame_id = 1 ,retries = 1, time_out = 3 ):
		#print "name",name,tx_data
		print self.node_list.has_key(name),  name, self.node_list
		if self.node_list.has_key( name ) == True:
			address = self.node_list[name]
			#print "made it here ",address
			return self.send_TX_msg( address,tx_data, frame_id = frame_id, retries = retries , time_out = time_out )
		else:
			return [False,None]		

		
	
		

	def send_TX_msg( self, address, tx_data, frame_id = 1 ,retries = 5 , time_out = 3):
		for i in range( 0, retries ):
		        return_value = self.send_tx_single_message( address, tx_data, frame_id ,time_out = time_out)
			if return_value[0] == True:
				return return_value
			frame_id = frame_id +1
		return [ False, None ]

	
	def send_tx_single_message( self, address, tx_data, frame_id , time_out):
		data = self.digi_packet.generate_TX_req( address, tx_data, broadcast_radius = 0,   frame_id = frame_id )
		#print "tx data",tx_data
		self.digi_serial.send_command(data)
		data = self.digi_serial.receive_data( time_out = time_out,size  = 10 )
		#print "rx_data",data
		return_value = [ False, None ]
		for i in data:
			if i != None:
				j = i[1]
				#print "j",j
				if  ( j[ "frame_type" ] == 0x8b ) and ( j["frame_id"] == frame_id)  :
					
					return_value =  [ True, j["delivery_status"], j ]
				
				else:
					self.process_async_messages( i[1] )
					#print "return value",return_value
		return return_value	
		

	

if __name__== "__main__" :
  
	def rx_callback( success_flag, address, data ):
		print "rx callback ----------->",success_flag, address, data
		

	# 0x00  Hardware Reset
	# 0x01  Watchdog Reset
	# 0x0B  Network Woke Up
	# 0x0C  Network Went to Sleep

	def modem_status_cb( status ): 
		print "modem status callback ------------------->", status


	
	zz = DigiCmds( "COM5" )
	zz.register_rx_callback(  rx_callback )   #parameters (  success_flag, address, data )
	zz.modem_status_call_back( modem_status_cb ) # parameters( status )
	zz.reset_modem()
	zz.clear_diagnostics()
	print zz.discover_single_node( "test_2" )

	print zz.discover_single_node("test_1")
	#print "discover_node test_2",zz.discover_nodes()

	print "waiting for time",time.sleep(5)
	
	print "dh register ",zz.send_remote_at_message(  "test_2","DH", zz.get_serial_number()[0:4] )
	print "dl register ",zz.send_remote_at_message(  "test_2","DL",zz.get_serial_number()[4:] )
	print "dh register ",zz.send_remote_at_message(  "test_1","DH",zz.get_serial_number()[0:4] )
	print "dl register ",zz.send_remote_at_message(  "test_1","DL", zz.get_serial_number()[4:] )

	
	for i in range( 0,100):
		print "sh register ", i,zz.send_remote_at_message(  "test_2","SH" )
		print "sl register ", i,zz.send_remote_at_message(  "test_2","SL" )
		print "dh register ", i,zz.send_remote_at_message(  "test_2","DH" )
		print "dl register ", i,zz.send_remote_at_message(  "test_2","DL" )

	for i in range( 0,100):
		print "sh register ", i,zz.send_remote_at_message(  "test_1","SH" )
		print "sl register ", i,zz.send_remote_at_message(  "test_1","SL" )
		print "dh register ", i,zz.send_remote_at_message(  "test_1","DH" )
		print "dl register ", i,zz.send_remote_at_message(  "test_1","DL" )

	for i in range( 0,100):
		print "send tx data", i,zz.send_TX_name_msg( "test_1",[1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17],  frame_id = 1 )
	
	for i in range(0,100):
		print "send tx data", i,zz.send_TX_name_msg( "test_2",[1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17],  frame_id = 1 )

	print "----------------------------------> start of read"
	for i in range( 0, 10):
		zz.receive_serial_data( .1, 10)
	print "--------------------------------------- end of read"
	print zz.diagnostics(  )
	print zz.diagnostics_remote( "test_2")
	
	print zz.diagnostics_remote( "test_1")
	print zz.clear_diagnostics_remote("test_1")
