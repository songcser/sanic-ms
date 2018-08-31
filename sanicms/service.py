import logging
import consul
import consul.aio
import socket
import hashlib

class ServiceInfo(object):
    
    def __init__(self, service_name, service_id, service_address, service_port,
                 node, address, service_tags=None):
        self.service_name = service_name
        self.service_id = service_id
        self.service_address = service_address
        self.service_port = service_port
        self.node = node
        self.address = address
        self.service_tags = service_tags


class ServiceManager(object):

    def __init__(self, name=None, loop=None, host='127.0.0.1', port=8500, **kwargs):
        self.name = name
        self.service_id = name
        self.consul = consul.aio.Consul(host=host, port=port, loop=loop, **kwargs)

    def get_host_ip(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip

    async def register_service(self, port, host=None, **kwargs):
        m = hashlib.md5()
        address = host or self.get_host_ip()
        url = 'http://{}:{}/'.format(address, port)
        m.update(url.encode('utf-8'))
        self.service_id = m.hexdigest()
        service = self.consul.agent.service
        check = consul.Check.http(url, '10s')
        await service.register(self.name, service_id=self.service_id, address=address, port=port, check=check, **kwargs)

    async def deregister(self):
        service = self.consul.agent.service
        await service.deregister(self.service_id)

    async def discovery_service(self, service_name):
        catalog = self.consul.catalog
        result = await catalog.service(service_name)
        services = []
        if result:
            for s in result[1]:
                services.append(ServiceInfo(
                    service_name=s['ServiceName'],
                    service_id=s['ServiceID'],
                    service_address=s['ServiceAddress'],
                    service_port=['ServicePort'],
                    node=['Node'],
                    address=['Address'],
                    service_tags=['ServiceTags']
                ))
        return services
