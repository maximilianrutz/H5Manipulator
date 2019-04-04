#! /bin/bash

docker rm -f $(docker ps -a -q)
docker-compose up -d
start chrome 192.168.99.100:8888
docker exec -ti $(docker ps -l -q) /bin/bash -c "export MKL_NUM_THREADS=1 && export OPENBLAS_NUM_THREADS=1 &&\
cd /root/caiman_data && pwd && source activate caiman && jupyter notebook --ip 0.0.0.0 --no-browser --allow-root --NotebookApp.token=''"
