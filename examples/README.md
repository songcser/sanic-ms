# Sanic MicroService Example

## Enviroment
    We use docker and docker-compose to create the dev env automatically.
    
    Currently it contains three docker images.
	 
	 - "db" for Postgres
	 - "server" for Sanic server

## Install Docker & Docker-Compose
### Install Docker
[Docker For Mac](https://www.docker.com/docker-mac)

### Install Docker-Compose
```bash
(sudo) pip install -U docker-compose
```

### Registry-Mirror
[DaoCloud Mirror](https://www.daocloud.io/mirror)

## Pull Source Code
 ```bash
git clone https://github.com/songcser/sanic-ms
cd sanic-ms/examples
 ```

## Develop
### Pull and run docker container
```bash
BUILD=y PULL=y ./develop/reset.sh
```

### Reset
```bash
./develop/reset.sh
```

## Restart server service
```bash
docker-compose restart server
```

## Logs
```bash
docker-compose logs
```

### Server Logs
```bash
docker-compose logs -f server
```

## Cluster Service
```sh
./develop/cluster.sh
```

## Test

```
./develop/test.sh
```

## Access Server

```
open http://localhost:8000

open http://localhost:8000/users/
```

## Access API

```
open http://localhost:8090
```
![image](https://github.com/songcser/sanic-ms/raw/master/examples/images/1514528294957.jpg)

## Access Zipkin
```
open http://localhost:9411
```
![image](https://github.com/songcser/sanic-ms/raw/master/examples/images/1514528423339.jpg)
![image](https://github.com/songcser/sanic-ms/raw/master/examples/images/1514528479787.jpg)

## Access Consul
```
open http://192.168.99.100:8500/ui/#/dc1/services
```
![image](https://github.com/songcser/sanic-ms/raw/master/examples/images/1514528479788.jpg)