import serial
import time
import os



class DigiSerial(  ):
 
	def __init__( self, ser_port, ser_packet_handler ,tim_out):
		self.serial = serial.Serial( port = ser_port, baudrate = 9600 , timeout = tim_out)
		self.ser_packet_handler = ser_packet_handler
		self.packet_data = [ None, None ]
  
	def send_command( self, packet_data ):
		packet_data = packet_data
		self.receive_data( size = 1, time_out = .1)
		for i in  range(0, len(packet_data )):
		   packet_data[i] = chr( packet_data[i] )
		serial_data = "".join(packet_data)
		self.serial.write( serial_data )
		time.sleep(.1) # delay is to fix interrupt problem that causes pyserial to drop characters -- internet post reported

	def receive_data( self, size = 256 , time_out = 1, change_time_out = True ):
		self.serial.setRTS(True)
		buffer = ""
		loop_flag = True
		self.serial.timeout = time_out
		while loop_flag == True:
		
			data = self.serial.read(size = size)
			#now that a serial stream is received
			#data will come very quickly now
			#time out is reduced to a low value
			if change_time_out == True:
				self.serial.timeout = .2
		        #print "data",data
			if len(data) ==  0:
				loop_flag = False
			else:
				buffer = buffer + data
		
		if len( buffer ) > 0:
			#print "serial data",buffer
			#break serial stream ( string)
			#into packets which are lists
			packets = self.parse_for_packets( buffer )
			#print "packets",packets
		else:
			packets = []
		return packets
		
		    
	def parse_for_packets( self, buffer ):
		self.packet_list = []
		list_buffer = list( buffer )
		for i in range( 0, len(list_buffer) ):
			list_buffer[i] = ord(list_buffer[i])
		#print "list buffer",list_buffer
		loop_flag = True
		list_index = 0
		while loop_flag == True:
			list_index = self.look_for_start( list_index, list_buffer )
			#print "list index ",list_index
			if list_index > 0:
				list_index = self.assemble_packet( list_index, list_buffer )
			if list_index < 0 :
				loop_flag = False
		return self.packet_list
		
	def look_for_start( self, loop_index, list_buffer ):
		if loop_index < 0:
			return loop_index
		for i in range( loop_index, len( list_buffer ) ):
			
			if list_buffer[i] == 0x7e:
				return loop_index + 1
		return -1
		
	def assemble_packet( self, list_index, list_buffer ):
		
		length = len(list_buffer)
		
		if list_index +3 >= length:
			return -1;
		packet_length = list_buffer[list_index]*256 + list_buffer[ list_index +1 ]
		#print "packet_length",packet_length
		
		list_index = list_index +2
		if packet_length + list_index + 1 > length:
		  return -1
		#compute check sum
		check_sum = 0
		packet_data = list_buffer[list_index:list_index+packet_length]
		for i in range( list_index, list_index + packet_length):
			check_sum = ( check_sum + list_buffer[ list_index ] )& 0xff
			list_index = list_index +1
	
		check_sum = ( check_sum + list_buffer[list_index] ) & 0xff
		#print "check_sum",check_sum
		list_index =list_index +1
		if check_sum == 0xff:
			self.packet_list.append( self.ser_packet_handler.parse_packet( packet_data ))
		        
		
		#print "packet_list",self.packet_list
		return list_index
				
				
      
      

