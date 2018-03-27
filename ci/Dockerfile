FROM hepsw/cvmfs-cms

MAINTAINER kreczko@cern.ch

# mount /cvmfs/grid.cern.ch & /cvmfs/sft.cern.ch
RUN mkdir -p /cvmfs/grid.cern.ch && mkdir -p /cvmfs/sft.cern.ch && \
    echo "grid.cern.ch /cvmfs/grid.cern.ch cvmfs defaults 0 0" >> /etc/fstab && \
    echo "sft.cern.ch /cvmfs/sft.cern.ch cvmfs defaults 0 0" >> /etc/fstab

RUN yum update -y -q --exclude=cvmfs* \
 && yum install -y -q wget git \
 &&  rm -fr /var/cache

ENV CODE_PATH /analysis
RUN useradd cmsl1t
RUN mkdir ${CODE_PATH} && chown -R cmsl1t ${CODE_PATH}

WORKDIR ${CODE_PATH}
#USER cmsl1t

ENTRYPOINT /usr/bin/cubied && \
  echo "Starting CMSL1T container" && \
  tail -f /dev/null
