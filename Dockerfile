FROM fedora:latest

RUN dnf -y update && \
    dnf -y install python3 && \
    dnf -y install kakasi kakasi-dict mecab mecab-ipadic-EUCJP

# RUN alternatives --set python /usr/bin/python3

WORKDIR /workdir
# COPY macro_furiganize.py .