FROM kreczko/cms-l1t-analysis-ci-base

MAINTAINER kreczko@cern.ch

COPY conda_requirements.txt /tmp/conda_requirements.txt

RUN /bin/bash -c "source activate cms && \
   conda update -yq --file /tmp/conda_requirements.txt" && \
   conda clean -t -y

 COPY requirements.txt /tmp/requirements.txt

 RUN /bin/bash -c "source activate cms && \
     pip install -U --no-cache-dir -r /tmp/requirements.txt"

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
