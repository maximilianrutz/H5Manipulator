#! /bin/bash

docker rm -f $(docker ps -a -q)
docker-compose up -d
start "" 192.168.99.100:8888
docker exec -ti $(docker ps -l -q) bash -c "cd src && pwd && source activate caiman && jupyter notebook --ip 0.0.0.0 --no-browser --allow-root --NotebookApp.token=''"
