import logging
import consul
import consul.aio
import socket

class Service(object):

    def __init__(self, host='127.0.0.1', port=8500, loop=None, **kwargs):
        self.consul = consul.aio.Consul(host=host, port=port, loop=loop, **kwargs)

    async def register_service(self, name, port, **kwargs):
        address = socket.gethostbyname(socket.gethostname())
        url = 'http://{}:{}/'.format(address, port)
        service = self.consul.agent.service
        check = consul.Check.http(url, '10s')
        await service.register(name, address=address, port=port, check=check, **kwargs)