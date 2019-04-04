FROM continuumio/miniconda3

RUN apt-get update && apt-get install -y --no-install-recommends gcc g++ libgl1 && apt-get clean &&\
	conda config --set always_yes yes && conda config --prepend channels conda-forge && conda update conda &&\
	mkdir src && cd src && git clone -b dev https://github.com/flatironinstitute/CaImAn.git &&\
	cd CaImAn && conda env create -f environment.yml -n caiman &&\
	conda install --override-channels -c conda-forge -n caiman pip &&\
	/bin/bash -c "cd /src/CaImAn && source activate caiman && /opt/conda/envs/caiman/bin/pip install . && caimanmanager.py install && conda update -c conda-forge opencv && pip install -U keras tensorflow"
