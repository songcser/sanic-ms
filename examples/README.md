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

## Test

```
./develop/test.sh
```

## Access

```
open http://localhost:8080
```
