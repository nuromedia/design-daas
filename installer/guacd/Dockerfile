FROM debian

# Install essentials
ENV DEBIAN_FRONTEND=noninteractive
# Use Debian as the base image

# # Install build dependencies
RUN apt update -y && apt upgrade -y && \
    apt install -y \
    build-essential \
    cmake \
    libcairo2-dev \
    libjpeg62-turbo-dev \
    libpng-dev \
    libossp-uuid-dev \
    freerdp2-dev \
    libfreerdp2-2 \
    libpango1.0-dev \
    libssh2-1-dev \
    libssl-dev \
    libvncserver-dev \
    libpulse-dev \
    libvorbis-dev \
    libwebp-dev \
    wget

# Download guacamole-server source code
WORKDIR /usr/local/src
RUN wget -O guacamole-server-1.5.4.tar.gz https://apache.org/dyn/closer.lua/guacamole/1.5.4/source/guacamole-server-1.5.4.tar.gz?action=download && \
    tar -xzf guacamole-server-1.5.4.tar.gz && \
    cd guacamole-server-1.5.4

# Build guacd
WORKDIR /usr/local/src/guacamole-server-1.5.4
RUN ./configure --with-init-dir=/etc/init.d && \
    make && \
    make install && \
    ldconfig
RUN mkdir /etc/guacamole && \
    echo "guacd.enable-drive: true" \
    echo "guacd.create-drive-path: true" \
    echo "guacd.printer-name: GuacPrint" \
    echo "guacd.audio-enabled: true" \
    > /etc/guacamole/guacamole.properties
RUN apt-get install -y ghostscript cups-bsd

# Expose guacd default port
ENV GUACD_LOG_LEVEL=debug
EXPOSE 4822

# Run guacd
CMD ["guacd", "-f"]

# entrypoint
COPY ./entrypoint.bash /entrypoint.bash
RUN chmod a+x /entrypoint.bash
ENTRYPOINT [ "/entrypoint.bash" ]

