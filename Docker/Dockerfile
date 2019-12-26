FROM continuumio/anaconda3
RUN apt update && apt --fix-missing --yes dist-upgrade; \
    adduser conda --system; \
    apt install -y npm; \
    /opt/conda/bin/conda upgrade --yes conda; \ 
    /opt/conda/bin/conda upgrade --yes anaconda; \
    /opt/conda/bin/conda install --yes graphviz python-graphviz; \
COPY update_git.py /usr/bin/
