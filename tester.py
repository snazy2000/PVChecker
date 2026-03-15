import serial
import time

def bin2hex(data):
	"""
	Converts binary data to hex
	"""
	return data.encode('hex_codec')

class Device:
	"""
	Device is a base class that provides physical and link layer operations
	"""
	STATUS = {
			# Field		Code			Divisor
			'Temp-inv':	('\x00',		10.0),		# Inverter internal temperature (deg C)
			'Vpv1':		('\x01',		10.0),		# PV1 Voltage (V)
			'Vpv2':		('\x02',		10.0),		# PV2 Voltage (V)
			'Vpv3':		('\x03',		10.0),		# PV3 Voltage (V)
			'Ipv1':		('\x04',		10.0),		# PV1 Current (A)
			'Ipv2':		('\x05',		10.0),		# PV2 Current (A)
			'Ipv3':		('\x06',		10.0),		# PV3 Current (A)
			'Vpv':		('\x40',		10.0),		# PV Voltage (V)
			'Iac':		('\x41',		10.0),		# Current to grid (A)
			'Vac':		('\x42',		10.0),		# Grid voltage (V)
			'Fac':		('\x43',		100.0),		# Grid frequency (Hz)
			'Pac':		('\x44',		1),			# Power to grid (W)
			'Zac':		('\x45',		1),			# Grid impedance (mOhm)
			'E-Total':	('\x47\x48',	10.0),		# Total energy to grid (kWh)
			'h-Total':	('\x49\x4a',	1),			# Total Operation hours (Hr)
			'Mode':		('\x4c',		1),			# Operation mode
			'Error':	('\x7e\x7f',	1)			# Error
			}
	PARAM = {
			'Vpc-start':	('\x40',	10.0),	# PV Start-up voltage (V)
			'T-start':		('\x41',	1),		# Time to connect grid (Sec)
			'Vac-Min':		('\x44',	10.0),	# Minimum operational grid voltage
			'Vac-Max':		('\x45',	10.0),	# Maximum operational grid voltage
			'Fac-Min':		('\x46',	100.0),	# Minimum operational frequency
			'Fac-Max':		('\x47',	100.0),	# Maximum operational frequency
			'Zac-Max':		('\x48',	1),		# Maximum operational grid impedance
			'DZac':			('\x49',	1),		# Allowable Delta Zac of operation
			}
	MODE = {0:'Wait', 1:'Normal', 2:'Fault', 3:'Permenant Fault'}
	ERROR = {		# The 2 error bytes are bit fields, e.g. ERROR[16] = 0x0100
			 0: ('The GFCI detection circucit is abnormal', 'GFCI ckt fails'),
			 1: ('The DC output sensor is abnormal', 'DC sensor fails'),
			 2: ('The 2.5V reference inside is abnormal', 'Ref 2.5V fails'),
			 3: ('Different measurements between Master and Slave for output DC current', 'DC inj. differs for M-S'),
			 4: ('Different measurements between Master and Slave for GFCI', 'Ground I differs for M-S'),
			 5: ('DC Bus voltage is too low', 'Bus-Low-Fail'),
			 6: ('DC Bus voltage is too High', 'Bus-High-Fail'),
			 7: ('Device Fault', 'Device-Fault'),
			 8: ('Delta GridZ is too high', 'Delta Z high'),
			 9: ('No grid voltage detected', 'No-Utility'),
			10: ('Ground current is too high', 'Ground I high'),
			11: ('DC bus is not correct', 'DC BUS fails'),
			12: ('Master and Slave firmware version is unmatch', 'M-S Version Fail'),
			13: ('Internal temperature is high', 'Temperature high'),
			14: ('AutoTest failed', 'Test Fail'),
			15: ('PV voltage is too high', 'Vpv high'),
			16: ('Fan Lock', 'FanLock-Warning'),
			17: ('The measured AC voltage is out of tolerable range', 'Vac out of range'),
			18: ('Isulation resistance of PV to earth is too low', 'PV insulation low'),
			19: ('The DC injection to grid is too high', 'DC injection high'),
			20: ('Different measurements between Master and Slave for dl, Fac, Uac or Zac', 'Fac,Zac,Vac differs for M-S'),
			21: ('Different measurements between Master and Slave for grid impedance', 'Zac differs for M-S'),
			22: ('Different measurements between Master and Slave for grid frequency', 'Fac differs for M-S'),
			23: ('Different measurements between Master and Slave for grid voltage', 'Vac differs for M-S'),
			24: ('Memory space is full', 'MemFull-Warning'),
			25: ('Test of output AC relay fails', 'AC relay fails'),
			26: ('The slave impedance is out of tolerable range', 'Zac-Slave out of range'),
			27: ('The measured AC impedance is out of range', 'Zac-Master out of range'),
			28: ('The slave frequency is out of tolerable range', 'Fac-Slave out of range'),
			29: ('The master frequency is out of tolerable range', 'Fac-Master out of range'),
			30: ('EEPROM reading or writing error', 'EEPROM fails'),
			31: ('Communication between microcontrollers fails', 'Comm fails between M-S'),
			}


#Oeffne Seriellen Port
port = serial.Serial('COM5',9600, timeout=0.2)
 
# timeout?
if not port.isOpen():
    print "cannot connect to Sunezy."
    sys.exit(1)
 
print "Port opened."
 
"""
THIS IS THE BEGINNERS WAY OF SENDING A STRING OF ASCII CODES TO THE DEVICE
AND RECEIVING THE SERIAL NUMBER AS A HUMAN READABLE STRING.
"""
 
#Reset
'''
| sync | src | dst | cmd | len | payload | checksum |
| 2B | 2B | 2B | 2B | 1B | len B | 2B |
aaaa 0100 0000 0004 00 0159
'''

def interpret_data(data, layout, dictionary):
	try:
		numbers = struct.unpack('!' + 'H'*len(layout), data)
	except struct.error as e:
		print "Error unpacking data:", e
		return None

	values = dict(zip(layout, numbers))
	return [(name, reduce(lambda x,y:(x<<16) + y, map(values.get, code)) / divisor)
			for name, (code, divisor) in dictionary.items()
			if reduce(lambda x,y: x and y, map(values.has_key, code))]

import struct
 
SYNC = 0xaa
SRC = 0x5501
DST = 0x0000
 
CMD_RST = 0x0010 #Reset
CMD_DSC = 0x0010 #Discover - query serial number
 
data = struct.pack('!HHHHHH', SYNC, SRC, DST, 0x0010, 0x0400, 0x0114)
#checksum = struct.pack('!H', sum(map(ord, data))) # sum over the entire data string without the checksum itself
#data = data + checksum
#print(checksum.encode('hex_codec'))

port.write(data)
print"--> ", data.encode('hex_codec')
 
data = struct.pack('!HHHHHH', SYNC, SRC, DST, 0x0010, 0x0000, 0x0110)
#checksum = struct.pack('!H', sum(map(ord, data)))
#data = data + checksum

port.write(data)
print"--> ", data.encode('hex_codec')
 
time.sleep(.2)
 
in_data =""
if port.inWaiting() > 0:
    in_data = port.read(port.inWaiting())
    print "<-- ", in_data.encode('hex_codec')
    if len(in_data) > 10:
        sn = in_data[9:-2]
        print "Serial Number: %s" % sn
else:
    print "Bytes received: %i" % len(in_data)

print(sn.encode('hex_codec'))

print("sleep")
time.sleep(1)

# Register
data = struct.pack('!HHHHH16sH', SYNC, SRC, DST, 0x0010, 0x0111, sn.encode(), 0x0104)

print(data.encode('hex_codec'))

checksum = struct.pack('<H', 0xb3)

print(checksum.encode('hex_codec'))

data = data + checksum

port.write(data)
print"--> ", data.encode('hex_codec')


#version





#status


data = struct.pack('!HHHHHH', SYNC, SRC, DST, 0x0111, 0x0200, 0x0114)

print(data.encode('hex_codec'))

port.write(data)
print"--> ", data.encode('hex_codec')

while (True):
    if (port.inWaiting() > 0):
        # read the bytes and convert from binary array to ASCII
        data_str = port.read(port.inWaiting())
        # print the incoming string without putting a new-line
        # ('\n') automatically after every print()
        print(data_str.encode('hex_codec')) 
        print(data_str)
        print(interpret_data(data_str, null, Device.STATUS))
    # Put the rest of your code you want here
    
    # Optional, but recommended: sleep 10 ms (0.01 sec) once per loop to let 
    # other threads on your PC run during this time. 
    time.sleep(0.01) 
 
port.close()
