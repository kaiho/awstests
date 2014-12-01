import csv
import boto
import boto.sqs
import time
import sys

from boto.sqs.message import Message
conn = boto.sqs.connect_to_region("us-east-1")
my_queue = conn.get_queue('test2')

print 'Initial queue size is ' + repr(my_queue.count())

d = {}

while 1:
	result_set = my_queue.get_messages()
	if (len(result_set) == 0):
		
		y = d.keys()
		y.sort()
		for x in y:
			print (x,':',d[x])
 

		#my_queue.clear()

		sys.exit()
	message = result_set[0].get_body()
	 
	if (message in d.keys()):
		print 'A key collision occured, incrementing key'
		d[message] += 1
	else:
		print 'First instance occured' + message
		d[message] = 1

	my_queue.delete_message(result_set[0])

print "Operation complete"

