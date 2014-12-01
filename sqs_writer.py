

import csv
import boto
import boto.sqs

from boto.sqs.message import Message
conn = boto.sqs.connect_to_region("us-east-1")

print conn.get_all_queues()

my_queue = conn.get_queue('test2')

for x in range(0, 100):
    print "We are on time %d" % (x) 

    m=Message()
    m.set_body('we are on number %d' %x)
    my_queue.write(m)


