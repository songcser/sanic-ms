from setuptools import setup, find_packages
setup(
    name="sanic-ms",
    version="0.1",
    author="songcser",
    author_email="songjiyi2008@163.com",
    description="This is an Example for Sanic",
    license="MIT",
    keywords="sanic micro service",
    url="http://example.com/HelloWorld/",   # project home page, if any
    packages=find_packages(),

    install_requires=[
        'sanic>=0.6.0',
        'uvloop>=0.8.0',
        'peewee>=2.9.1',
        'psycopg2>=2.7.1',
        'asyncpg>=0.11.0',
        'aiohttp>=2.0.7',
        'opentracing>=1.2.2',
        'basictracer>=2.2.0',
        'pyyaml>=3.12'
    ],

    package_data={
        'sanic-ms': ['*.py', '*.yml'],
    },
)
