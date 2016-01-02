'''
   print "discover_node test_1",zz.discover_single_node("test_1")
   #print "aggregate tets_1",zz.aggregate_node( "test_1")
   print "sh register ", zz.send_remote_at_message(  "test_1","SH" )
   print "sl register ", zz.send_remote_at_message(  "test_1","SL" )
   print "dh register ", zz.send_remote_at_message(  "test_1","DH" )
   print "dl register ", zz.send_remote_at_message(  "test_1","DL" )

   print "discover_node test_2",zz.discover_single_node("test_2")
   #print "aggregate test_2",zz.aggregate_node( "test_2")
   #print "discover_node",zz.discover_nodes()
   #print "send tx data", zz.send_TX_name_msg( "test_1",[1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17],  frame_id = 1 )
   #print "send tx data", zz.send_TX_name_msg( "test_2",[1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17],  frame_id = 1 )
   
'''
'''
   print y.generate_AT_cmd( "BD",frame_id = 0x1 )
   print y.generate_ATQueue_cmd( "BD",[7],frame_id = 0x1 )
   print y.generate_TX_req(  [0,0x13,0xa2,0x00,0x40,0x0A,0x01,0x27 ] , [0x54,0x78,0x44,0x61,0x74,0x61,0x30,0x41], frame_id = 1 )
   x =  y.generate_Explicit_Tx_cmd(  [0,0x13,0xa2,0x00,0x01,0x23,0x84,0x00 ] , 0xA0, 0xA1,[0x15,0x54],[0xC1,0x05],
						  [0x54,0x78,0x44,0x61,0x74,0x61],  frame_id = 1)	
					
   print x
   x = y.generate_Remote_cmd(  [0,0x13,0xa2,0x00,0x40,0x40,0x11,0x22 ], ["B","H"], parameters = [0x1], frame_id = 1  )
   print x
   x = y.parse_packet([0x88,0x1,ord("B"),ord("D"),0])
   print x
   x = y.parse_packet([0x8a,0 ] )
   print x
   x = y.parse_packet([0x8B,0x47,0xff,0xfe,0,1,2 ] )
   print x
   x = y.parse_packet([0x8d, 0x12,0x2b,
                                  0x9c,0x93,0x81,0x7f,
				  0x00,0x00,0x00,
				  0x00,0x13,0xA2,0x00,0x40,0x52,0xaa,0xaa,
				  0x00,0x13,0xa2,0x00,0x40,0x52,0xdd,0xdd,
				  0x00,0x13,0xa2,0x00,0x40,0x52,0xbb,0xbb,
				  0x00,0x13,0xa2,0x00,0x40,0x52,0xcc,0xcc ] )

   print x
   x = y.parse_packet( [0x8E,0x00,1,2,3,4,5,6,7,8,11,12,13,14,15,16,17,18])
   print x
   x = y.parse_packet([0x90,
                                  1,2,3,4,5,6,7,8,
				  0xff,0xfe,
				  0x1,
				  0x1,2,3,4,5,6,7,8,9,10,11,12,13,14 ] )
   print x
   x = y.parse_packet([0x91,
                                   11,12,13,14,15,16,17,18,
				   0xff,0xf2,
				   0xE0,0xE0,0x22,0xC1,0x5,0x2,
				   1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19 ])
   print x

   x = y.parse_packet([0x97,0x55,
                                   11,12,13,14,15,16,17,18,
				   0xff,0xf2,
				   0x53,0x4c,0x00,
				   1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19 ])
   print x
'''