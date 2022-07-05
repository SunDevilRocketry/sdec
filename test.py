teststring = input("input teststring: ")
if ('0x' not in teststring):
	print('Error: 0x not in teststring')
else:
	hexnum = int(teststring, 0)
	print(hexnum)
