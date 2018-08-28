log() {
	echo "=== $1"
}

SWARM_MASTER=ms-master
NETWORK_NAME=ms_sanic-network
docker-machine create $SWARM_MASTER -d virtualbox

eval $(docker-machine env $SWARM_MASTER)

SWARM_MASTER_IP=`docker-machine ip $SWARM_MASTER`
log "Swarm master ip : $SWARM_MASTER_IP"
docker swarm init --advertise-addr $SWARM_MASTER_IP

SWARM_MASTER_TOKEN=`docker swarm join-token -q worker`
log "Swarm token is: $SWARM_MASTER_TOKEN"

docker network create --attachable --driver overlay $NETWORK_NAME

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
    docker-machine create $node -d virtualbox
    eval $(docker-machine env $node)
    docker swarm join --token $SWARM_MASTER_TOKEN $SWARM_MASTER_IP:2377
    docker-compose build server
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
docker stack deploy -c docker-compose-cluster.yml ms