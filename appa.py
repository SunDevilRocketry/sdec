
import crc32c #specific library for the checksum algorithm in Python
import struct #turns data into byte-sized packets

def crc32_checksum(data_config):
    data_format = f'<{len(data_config)}f' #defines formatting based on size based of data_config file
    data_bytes = struct.pack(data_format, *data_config) #serializes data_config into bytes
    checksum = crc32c.crc32(data_bytes) #computes the checksum
    checksum_bytes = struct.pack('>I',checksum) #serializing checksum, checking big-endians
    payload = checksum_bytes+data_bytes #prepend the checksum to the data to form the final payload
    return payload
