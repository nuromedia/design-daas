# Root image
FROM debian:latest

# Python environment
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get -y update && apt-get -y upgrade && apt-get -y install python3 python3-venv pip

# Quart venv
ENV APP_NAME=qweb
ENV FOLDER_VENV=/opt/qweb
RUN mkdir -p $FOLDER_VENV/app $FOLDER_VENV/data $FOLDER_VENV/scripts
COPY scripts/ensure_venv.bash $FOLDER_VENV/scripts/ensure_venv.bash
RUN cd $FOLDER_VENV && ./scripts/ensure_venv.bash -p "quart quart-cors nest_asyncio"
COPY scripts/entrypoint.bash /opt/qweb/scripts/entrypoint.bash
COPY data/qweb.toml /opt/qweb/data/qweb.toml
COPY main.py /opt/qweb/main.py
WORKDIR $FOLDER_VENV
ENTRYPOINT ["/opt/qweb/scripts/entrypoint.bash"]
