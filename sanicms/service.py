import logging
import consul
import consul.aio
import socket
import hashlib

class Service(object):

    def __init__(self, name, host='127.0.0.1', port=8500, loop=None, **kwargs):
        self.name = name
        self.service_id = name
        self.consul = consul.aio.Consul(host=host, port=port, loop=loop, **kwargs)

    async def register_service(self, port, **kwargs):
        m = hashlib.md5()
        address = socket.gethostbyname(socket.gethostname())
        url = 'http://{}:{}/'.format(address, port)
        m.update(url)
        self.service_id = m.hexdigest()
        service = self.consul.agent.service
        check = consul.Check.http(url, '10s')
        await service.register(self.name, service_id=self.service_id, address=address, port=port, check=check, **kwargs)
        