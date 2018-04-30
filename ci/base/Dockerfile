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
