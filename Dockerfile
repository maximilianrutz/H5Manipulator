FROM continuumio/anaconda3

RUN conda config --set always_yes yes && conda update --yes conda
RUN apt-get update && apt-get —no-install-recommends install -y gcc g++ libgl1 && rm -rf /var/lib/apt/lists/*
RUN mkdir src && cd src && git clone -b dev https://github.com/flatironinstitute/CaImAn.git && cd CaImAn && conda env create -n caiman -f environment.yml && conda install --override-channels -c conda-forge -n caiman pip
RUN /bin/bash -c "cd src/CaImAn && source activate caiman && /opt/conda/envs/caiman/bin/pip install . && caimanmanager.py install"



