import boto
import boto.ec2
from boto.vpc import VPCConnection
import time

cloud_network		= '10.1.0.0/16'
blue_subnet 		= '10.1.0.0/24'
green_subnet 		= '10.1.1.0/24'
generic_linux_image	= 'ami-a250ecca'
nat_linux_image		= 'ami-184dc970'

connection			= VPCConnection()
private_cloud 		= connection.create_vpc(cloud_network)

time.sleep(2) #fix race condition later
private_cloud.add_tag('Name', 'virtual-private-cloud')
print ("created vpc", private_cloud.id)

private_subnet = connection.create_subnet(private_cloud.id, green_subnet)
time.sleep(2) #fix race condition later
private_subnet.add_tag('Name', 'green_subnet')
public_subnet = connection.create_subnet(private_cloud.id, blue_subnet)
time.sleep(2)
public_subnet.add_tag('Name', 'blue_subnet')
print "created public and private subnets"

igw = connection.create_internet_gateway()
connection.attach_internet_gateway(igw.id, private_cloud.id)

print "created and attached internet gateway"

host_security_group = connection.create_security_group('private_cloud_sg', 'private_cloud_sg', private_cloud.id)
host_security_group.authorize('tcp', 80, 80, '0.0.0.0/0')
host_security_group.authorize('tcp', 22, 22, '0.0.0.0/0')

print "created security groups"

reservation = connection.run_instances(image_id=nat_linux_image, instance_type='t2.micro', key_name='kaihon', subnet_id=public_subnet.id, security_group_ids=[host_security_group.id])
instance = reservation.instances[0]

connection.modify_instance_attribute(instance.id, attribute='sourceDestCheck', value=False)

print "modified instance to ignore source and destination checks"

## the following does not work
while instance.state == 'pending':
	time.sleep(5)
	instance.update()

instance.add_tag('Name', 'Nat-Instance')

public_route_table	= connection.create_route_table(private_cloud.id)
print "created public route table"
private_route_table = connection.create_route_table(private_cloud.id)
print "created private route table"

connection.create_route(public_route_table.id, '0.0.0.0/0', igw.id, None, None, None, False)
connection.create_route(private_route_table.id, '0.0.0.0/0', None, instance.id, None, None, False)

connection.associate_route_table(private_route_table.id, private_subnet.id)
connection.associate_route_table(public_route_table.id, public_subnet.id)

elastic_ip = connection.allocate_address(domain=None, dry_run=False)
elastic_ip.associate(instance_id=instance.id, network_interface_id=None, private_ip_address=None, allow_reassociation=False, dry_run=False)

