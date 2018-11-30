#!/usr/bin/env bash
source "$(dirname ${BASH_SOURCE[0]})/utils.sh"
log() {
	echo "=== $1"
}

SWARM_MASTER=ms-master
NETWORK_NAME=ms_sanic-network
docker-machine rm -f $SWARM_MASTER
docker-machine create $SWARM_MASTER -d virtualbox --virtualbox-boot2docker-url $HOME/.docker/machine/cache/boot2docker.iso

eval $(docker-machine env $SWARM_MASTER)

SWARM_MASTER_IP=`docker-machine ip $SWARM_MASTER`
log "Swarm master ip : $SWARM_MASTER_IP"
docker swarm init --advertise-addr $SWARM_MASTER_IP

SWARM_MASTER_TOKEN=`docker swarm join-token -q worker`
log "Swarm token is: $SWARM_MASTER_TOKEN"

docker network create --attachable --driver overlay $NETWORK_NAME

log "Run progrium/consul"
docker run -d --name $SWARM_MASTER --hostname $SWARM_MASTER \
		-p 8300:8300 \
		-p 8301:8301 \
		-p 8301:8301/udp \
		-p 8302:8302 \
		-p 8302:8302/udp \
		-p 8400:8400 \
		-p 8500:8500 \
		-p 53:53 \
		-p 53:53/udp \
        --net=$NETWORK_NAME \
		progrium/consul \
		-server \
		-advertise $SWARM_MASTER_IP \
		-bootstrap

SWARM_NODES=("ms-node1" "ms-node2")
for node in "${SWARM_NODES[@]}"; do
    log "Create node $node"
    docker-machine rm -f $node
    docker-machine create $node -d virtualbox --virtualbox-boot2docker-url $HOME/.docker/machine/cache/boot2docker.iso
    eval $(docker-machine env $node)
    docker swarm join --token $SWARM_MASTER_TOKEN $SWARM_MASTER_IP:2377
    docker-compose build
    NODE_IP=$(docker-machine ip $node)
    docker run -d --name "consul" --hostname $node \
        -p 8300:8300 \
		-p 8301:8301 \
		-p 8301:8301/udp \
		-p 8302:8302 \
		-p 8302:8302/udp \
		-p 8400:8400 \
		-p 8500:8500 \
		-p 53:53 \
		-p 53:53/udp \
        --network $NETWORK_NAME \
        progrium/consul \
        -server \
        -advertise $NODE_IP \
        -join $SWARM_MASTER_IP
done

eval $(docker-machine env $SWARM_MASTER)
log "Deploy stack ms"
docker stack deploy -c docker-compose-cluster.yml ms
MS_DB_TASK_ID=`docker service ps -q ms_db`
waituntil 200 ">>> connect postgres" docker exec ms_db.1.$MS_DB_TASK_ID pg_isready
log "Deploy stack ms"
docker stack deploy -c docker-compose-service-cluster.yml ms-service