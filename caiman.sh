#! /bin/sh

sensible-browser #192.168.99.100:8888
docker rm -f $(docker ps -a -q)
docker-compose up -d
docker exec -ti dockertoolbox_neurophys_1 bash -c "cd src && pwd && source activate caiman && jupyter notebook --ip 0.0.0.0 --no-browser --allow-root --NotebookApp.token=''"
