docker-machine create ms-master --driver virtualbox
docker-machine create ms-agent1 --driver virtualbox
docker-machine create ms-agent2 --driver virtualbox

eval $(docker-machine env ms-master)
masterip=`docker-machine ip ms-master`
docker swarm init --advertise-addr ${masterip}
mastertoken=`docker swarm join-token -q worker`
eval $(docker-machine env ms-agent1)
docker swarm join --token ${mastertoken} ${masterip}:2377
eval $(docker-machine env ms-agent2)
docker swarm join --token ${mastertoken} ${masterip}:2377