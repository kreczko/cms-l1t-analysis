FROM centos:6

LABEL maintainer="kreczko@cern.ch"

RUN yum history sync \
 && yum update -y -q -e 0 --exclude=cvmfs* \
 && yum install -y -q -e 0 \
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
 && conda update conda -y -q \
 && conda update pip -y -q \
 && conda install psutil -yq \
 && conda config --add channels http://conda.anaconda.org/NLeSC \
 && conda config --set show_channel_urls yes \
 && conda clean -t -y

RUN echo "Created conda environment, installing basic dependencies" \
&& conda install -y -q nomkl \
&& conda install -y -q pandas==0.23 numpy matplotlib pyyaml \
&& conda clean -t -y

COPY conda_requirements.txt /tmp/conda_requirements.txt
RUN echo "... installing project dependencies" \
 && conda install -y -q --file /tmp/conda_requirements.txt \
 && conda clean -t -y

COPY requirements.txt /tmp/requirements.txt
RUN echo "... installing project dependencies" \
 && bash -c "source activate root \
 && pip install --no-cache-dir -r /tmp/requirements.txt"

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

CMD bash -c "source activate root \
 && source ${CODE_PATH}/ci/test.sh"
