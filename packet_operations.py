class Packet_Ops():

	def __init__( self ):
		self.frame_id = 1
		self.rx_packet_table = {
			0x88: self.parse_command_resp,
			0x8a: self.parse_modem_status,
			0x8b: self.parse_tx_status,
			0x8d: self.parse_route_information,
			0x8e:  self.aggreate_address_update,
			0x90: self.parse_rx_indicator,
			0x91: self.parse_rx_explict_indicator,
			0x92: self.parse_sample_rx_indicator,
			0x95: self.parse_node_identifier,
			0x97: self.parse_remote_commad_resp  }
	
	
	def construct_packet( self, input_data ): #data is a length
		
		return_value = []
		return_value.append(0x7e)
		length = len(input_data)
		
		return_value.append( (length >>8 ) & 0xff )
		return_value.append( length & 0xff )
		
		sum = 0
		for i in input_data:
		  return_value.append(i)
		  sum = sum + i
	
	        return_value.append((0xff-sum)&0xff)
		
		return return_value
		
	def generate_AT_cmd( self, command, parameters = None, frame_id = None ):
		data = []
		if frame_id == None:
			frame_id = self.frame_id
		else:
			self.frame_id = frame_id
		data.append( 0x8)
		data.append( frame_id )
		data.append(ord(command[0] ))
		data.append(ord(command[1]))
		if parameters != None:
	           data.extend(parameters)
		self.frame_id = self.frame_id + 1
		return self.construct_packet(data) 
	
	def generate_ATQueue_cmd( self, command, parameters = None, frame_id = None ):
		data = []
		if frame_id == None:
			frame_id = self.frame_id
		else:
			self.frame_id = frame_id
		data.append( 0x9)
		data.append( frame_id )
		data.append(ord(command[0] ))
		data.append(ord(command[1]))
		if parameters != None:
	           data.extend(parameters)
		self.frame_id = self.frame_id + 1
		return self.construct_packet(data) 
	
	def generate_TX_req( self, destination_address, tx_data, broadcast_radius = 0, transmit_option = 0, frame_id = None ):
		data = []
		if frame_id == None:
			frame_id = self.frame_id
		else:
			self.frame_id = frame_id
		data.append( 0x10)
		data.append( frame_id )
		data.extend( destination_address )
		data.extend( [0xff, 0xfe] )
		data.append( broadcast_radius )
		data.append( transmit_option )
		data.extend(tx_data)
		self.frame_id = self.frame_id + 1
		return self.construct_packet(data) 

		
	def generate_Explicit_Tx_cmd( self, destination_address, source_endpoint, dest_endpoint, cluster_id, profile_id, tx_data, broadcast_radius = 0, transmit_option = 0, frame_id = None ):
		data = []
		if frame_id == None:
			frame_id = self.frame_id
		else:
			self.frame_id = frame_id
		data.append( 0x11)
		data.append( frame_id )
		data.extend( destination_address)
		data.extend( [ 0xff, 0xfe ] )
		data.append( source_endpoint)
		data.append( dest_endpoint )
		data.extend( cluster_id)
		data.extend( profile_id)
		data.append( broadcast_radius )
		data.append( transmit_option )
		data.extend(tx_data)
		self.frame_id = self.frame_id + 1
		return self.construct_packet(data) 

		
	def generate_Remote_cmd( self,destination_address, command, parameters = None, frame_id = None, update_flag = True ):
		data = []
		if frame_id == None:
			frame_id = self.frame_id
		else:
			self.frame_id = frame_id
		data.append( 0x17)
		data.append( frame_id )
		data.extend( destination_address)
		data.extend( [ 0xff , 0xfe ] )
		if update_flag == True:
			data.append(2)
		else:
			data.append(0)
		data.append(ord(command[0] ))
		data.append(ord(command[1]))
		if parameters != None:
	           data.extend(parameters)
		self.frame_id = self.frame_id + 1
		return  self.construct_packet(data) 

	def parse_command_resp( self, data ):
		return_value = {}
		return_value["frame_type"] = data[0]
		return_value["frame_id"] = data[1]
		return_value["at_command"] = [ chr(data[2]),chr(data[3]) ]
		return_value["command_status"] = data[4]
		if len(data) >= 5:
		  return_value["command_data"] = data[5:]
		else:
		  return_value["command_data"] = None
		return return_value
		
	def parse_modem_status( self, data ):
		return_value = {}
		return_value["frame_type"] = data[0]
		return_value["status"] = data[1]
		return return_value
		
	def parse_tx_status( self, data ):
		return_value = {}
		return_value["frame_type"] = data[0]
		return_value["frame_id"]   = data[1]
		return_value["retry_count"] = data[4]
		return_value["delivery_status"] = data[5]
		return_value["discovery_status"] = data[6]
		return return_value
		
		
	def parse_route_information( self, data ):
		return_value = {}
		
		return_value["frame_type"] = data[0]
		return_value["source_event"]   = data[1]
		return_value["length"] = data[2]
		return_value["time_stamp"] = data[3:7]
		return_value["ack_timeout_count"] = data[7]
		return_value["addresses"] = []
		number = data[2] -7
		address_number = number/8
		index_start = 10
		for i in range( 0,address_number): 
			return_value["addresses"].append( data[index_start : index_start+8 ] )
			index_start = index_start+8
		return return_value
		

		
	def aggreate_address_update( self, data ):
		return_value = {}
		return_value["frame_type"] = data[0]
		return_value["format_id"] = data[1]
		return_value["new_address"] = data[2:10]
		return_value["old_address"] = data[10:18]
		return return_value
		
	def parse_rx_indicator( self, data ):
		return_value = {}
		return_value["frame_type"] = data[0]
		return_value["address"] = data[1:9]
		return_value["receive_option"] = data[11]
		return_value["data"] = data[12:]
		return return_value

		
	def parse_rx_explict_indicator( self, data ):
		return_value = {}
		return_value["frame_type"] = data[0]
		return_value["address"] = data[1:9]
		return_value["source_endpoint"] = data[11]
		return_value["destination_endpoint"] = data[12]
		return_value["cluster_id"] = data[13]
		return_value["profile_id"] = data[14:16]
		return_value["receive_options"] = data[16]
		return_value["data"] = data[17:]
		return return_value

	#implemented later
	def parse_sample_rx_indicator( self, data ):
		pass
		
	### implinented later
	def parse_node_identifier( self,data ):
		pass
		
	def parse_remote_commad_resp( self, data ):
		return_value = {}
		return_value["frame_type"] = data[0]
		return_value["frame_id"] =    data[1]
		return_value["address"] = data[2:10]
		return_value["at_command"] = [ chr(data[12]), chr(data[13]) ]
		return_value["command_status"] = data[14]
		return_value["command_data"] = data[15:]
		return return_value




		
	def parse_packet( self,data ):
	   #print "parse_packet data",data
	   if self.rx_packet_table.has_key( data[0] ):
		
		return [ True, self.rx_packet_table[data[0] ](data) ]
	   else:
		return [ False] 