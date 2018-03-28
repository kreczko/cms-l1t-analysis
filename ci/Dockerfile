FROM hepsw/cvmfs-cms

MAINTAINER kreczko@cern.ch

# mount /cvmfs/grid.cern.ch & /cvmfs/sft.cern.ch
RUN mkdir -p /cvmfs/grid.cern.ch && mkdir -p /cvmfs/sft.cern.ch && \
    echo "grid.cern.ch /cvmfs/grid.cern.ch cvmfs defaults 0 0" >> /etc/fstab && \
    echo "sft.cern.ch /cvmfs/sft.cern.ch cvmfs defaults 0 0" >> /etc/fstab

RUN yum history sync \
 && yum update -y -q --exclude=cvmfs* \
 && yum install -y -q \
        glibc-devel\
        glibc-devel.i686 \
        git \
        sudo \
        wget \
 &&  rm -fr /var/cache

ENV CMSL1T_CONDA_PATH /software/cmsl1t/miniconda
RUN mkdir -p ${CMSL1T_CONDA_PATH} \
 && rmdir ${CMSL1T_CONDA_PATH} \
 && wget -nv https://repo.continuum.io/miniconda/Miniconda2-latest-Linux-x86_64.sh -O /tmp/miniconda.sh \
 && bash /tmp/miniconda.sh -b -p ${CMSL1T_CONDA_PATH} \
 && rm -f miniconda.sh

ENV PATH="${CMSL1T_CONDA_PATH}/bin:$PATH"

RUN echo "Finished conda installation, updating conda and pip" \
 && conda update conda -yq \
 && conda update pip -yq \
 && conda install psutil -yq \
 && conda config --add channels http://conda.anaconda.org/NLeSC \
 && conda config --set show_channel_urls yes \
 && conda clean -t -y

COPY conda_requirements.txt /tmp/conda_requirements.txt

RUN conda create -n cms python=2.7 -yq &&\
   echo "Created conda environment, installing basic dependencies" && \
   /bin/bash -c "source activate cms && \
   conda install -yq --file /tmp/conda_requirements.txt" && \
   conda clean -t -y

 COPY requirements.txt /tmp/requirements.txt

 RUN /bin/bash -c "source activate cms && \
     pip install --no-cache-dir -r /tmp/requirements.txt"

ENV CODE_PATH /code
ENV USERNAME cmsl1t
ARG USERID=1000
RUN adduser -u ${USERID} ${USERNAME} && \
  echo "${USERNAME} ALL=(root) NOPASSWD:ALL" > /etc/sudoers.d/${USERNAME} && \
  chmod 0440 /etc/sudoers.d/${USERNAME} && \
  cp -p /root/.bashrc /home/${USERNAME}/. && \
  chown ${USERNAME}:${USERNAME} /home/${USERNAME}/.bashrc
RUN mkdir ${CODE_PATH} && chown -R ${USERNAME} ${CODE_PATH}

WORKDIR ${CODE_PATH}
ENV HOME /home/${USERNAME}
USER cmsl1t

ENTRYPOINT sudo /usr/bin/cubied \
        && echo "Starting CMSL1T container" \
        && sleep 20 \
        && bash -c "source ${CODE_PATH}/ci/test.sh"
