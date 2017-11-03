FROM hepsw/cvmfs-cms

LABEL maintainer="kreczko@cern.ch"

# mount /cvmfs/grid.cern.ch & /cvmfs/sft.cern.ch
RUN mkdir -p /cvmfs/grid.cern.ch && mkdir -p /cvmfs/sft.cern.ch && \
    echo "grid.cern.ch /cvmfs/grid.cern.ch cvmfs defaults 0 0" >> /etc/fstab && \
    echo "sft.cern.ch /cvmfs/sft.cern.ch cvmfs defaults 0 0" >> /etc/fstab

RUN yum install -y -q wget git glibc-devel.i686 glibc-devel
#RUN yum install -y -q glibc gcc && yum clean all
RUN useradd cmsl1t
RUN mkdir /analysis && chown -R cmsl1t /analysis
WORKDIR /analysis
#USER cmsl1t

# need to execute env.sh and ntp setup in CMD
# as CVMFS needs 'privileged' rights,
# but cannot do that when building the container
CMD ["/bin/bash", "-c", "ci/run_tests.sh"]
