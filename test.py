byte1 = b'\x13'
byte1_int = ord(byte1)
byte2 = b'\x05'
byte2_int = ord(byte2)
print(byte1)
print(byte2)
byte3 = byte1_int + byte2_int
print(byte3)
byte3_byte = byte3.to_bytes(1, byteorder='big', signed=False)
print(byte3_byte)
