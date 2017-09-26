FROM kreczko/htcondor-in-a-box

ENV CMSL1T_CONDA_PATH /software/cmsl1t/miniconda

# ROOT requirements
RUN sudo apt install -y \
             libjpeg-dev \
             libpng++-dev
             libxft-dev \
             libxpm-dev \

RUN sudo mkdir -p ${CMSL1T_CONDA_PATH};\
  cd ${CMSL1T_CONDA_PATH};\
  cd ..;\
  sudo chown `whoami` $PWD;\
  sudo rmdir ${CMSL1T_CONDA_PATH};

RUN wget -nv https://repo.continuum.io/miniconda/Miniconda2-latest-Linux-x86_64.sh -O /tmp/miniconda.sh && \
  bash /tmp/miniconda.sh -b -p ${CMSL1T_CONDA_PATH} && \
  rm -f miniconda.sh
ENV PATH="${CMSL1T_CONDA_PATH}/bin:$PATH"

RUN echo "Finished conda installation, updating conda and pip" && \
  conda update conda -yq && \
  conda update pip -yq && \
  conda install psutil -yq && \
  conda config --add channels http://conda.anaconda.org/NLeSC && \
  conda config --set show_channel_urls yes && \
  conda clean -t -y

COPY conda_requirements.txt /tmp/conda_requirements.txt

RUN conda create -n cms python=2.7 -yq &&\
  echo "Created conda environment, installing basic dependencies" && \
  /bin/bash -c "source activate cms && \
  conda install -yq --file /tmp/conda_requirements.txt" && \
  conda clean -t -y

COPY requirements.txt /tmp/requirements.txt

RUN /bin/bash -c "source activate cms && \
    pip install --no-cache-dir -r /tmp/requirements.txt"

COPY docker/cdw /usr/local/bin/cdw
