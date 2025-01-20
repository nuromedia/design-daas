FROM x11vnc

# Install essentials
ENV DEBIAN_FRONTEND=noninteractive
RUN apt update -y && apt upgrade -y
RUN apt install -y x11vnc tigervnc-standalone-server openssh-server xvfb
RUN apt install -y xterm python3 pip wget
RUN apt install -y kitty
RUN apt install -y locales vim galculator
RUN pip install click psutil xcffib --break-system-packages
RUN pip install cairocffi --no-cache-dir  --break-system-packages
RUN pip install dbus-next qtile  --no-cache-dir  --break-system-packages

# Wine
# https://wiki.winehq.org/Debian
RUN dpkg --add-architecture i386
RUN mkdir -pm755 /etc/apt/keyrings
RUN wget -O /etc/apt/keyrings/winehq-archive.key https://dl.winehq.org/wine-builds/winehq.key
RUN wget -NP /etc/apt/sources.list.d/ https://dl.winehq.org/wine-builds/debian/dists/bookworm/winehq-bookworm.sources
RUN apt update -y && apt upgrade -y
RUN apt install -y --install-recommends sudo wine32 wine64 curl zenity mono-complete
RUN apt install -y --install-recommends ca-certificates \
	apt-transport-https cabextract git gnupg gosu gpg-agent p7zip \
	pulseaudio pulseaudio-utils unzip winbind

# Winetricks
# https://github.com/Winetricks/winetricks
RUN wget https://raw.githubusercontent.com/Winetricks/winetricks/master/src/winetricks
RUN chmod +x winetricks
RUN mv winetricks /usr/bin
RUN wget https://raw.githubusercontent.com/Winetricks/winetricks/master/src/winetricks.bash-completion
RUN mv winetricks.bash-completion /usr/share/bash-completion/completions/winetricks
RUN wget https://raw.githubusercontent.com/Winetricks/winetricks/master/src/winetricks.1
RUN mv winetricks.1 /usr/share/man/man1/winetricks.1

# RUN echo 'deb http://download.opensuse.org/repositories/home:/strycore/Debian_12/ /' | tee /etc/apt/sources.list.d/home:strycore.list
# RUN curl -fsSL https://download.opensuse.org/repositories/home:strycore/Debian_12/Release.key | gpg --dearmor | tee /etc/apt/trusted.gpg.d/home_strycore.gpg > /dev/null
# RUN apt update
# RUN apt install -y lutris

# Install necessary packages and dependencies
RUN apt-get update -y && apt-get install -y \
	git \
	build-essential \
	wine64 \
	wine32

RUN sudo sed 's/main/main contrib non-free non-free-firmware/g' \
	-i /etc/apt/sources.list.d/debian.sources

RUN apt-get update -y && apt-get upgrade -y && apt-get install -y \
	meson glslang-tools \
	libasound2-plugins:i386 \
	libsdl2-2.0-0:i386 libdbus-1-3:i386 libsqlite3-0:i386 \
	gcc-multilib g++-multilib \
	&& apt-get clean \
	&& rm -rf /var/lib/apt/lists/* \
	&& apt-get update -y && apt-get upgrade -y

#Set environment variables to avoid interaction during installation
ENV DEBIAN_FRONTEND=noninteractive


# Create a non-root user and switch to it
RUN adduser --disabled-password --gecos "" wineuser
RUN sudo usermod -aG sudo wineuser
#VOLUME /home/wineuser/.wine32


# Vulkan/Nvidia
# RUN apt-get update -y && apt-get upgrade -y && apt-get install -y \
# 	libgl1-mesa-dri:i386 mesa-vulkan-drivers mesa-vulkan-drivers:i386 \
# 	goverlay mangohud gamemode \
# 	libsdl2-2.0-0:i386 libdbus-1-3:i386 libsqlite3-0:i386 \
# 	nvidia-driver nvidia-driver-libs:i386 \
# 	nvidia-vulkan-icd:i386 nvidia-vulkan-common:i386 \
# 	libvulkan1 libvulkan1:i386 nvidia-opencl-common:i386 \
# 	&& apt-get clean \
# 	&& rm -rf /var/lib/apt/lists/*
# Create wine environments
#COPY wine-init.bash /wine-init.bash

# Locale
RUN echo "de_DE.UTF-8 UTF-8" > /etc/locale.gen
RUN locale-gen

# ssh
COPY ./authorized_keys /root/.ssh/authorized_keys
EXPOSE 22

# Daas Environment
RUN mkdir -p /root/daas/env
RUN mkdir -p /root/daas/qmsg
RUN mkdir -p /root/daas/status
RUN touch /root/daas/status/cmdout.txt
# COPY ./qmsg/* /root/daas/
COPY ./daas.jpg /root/daas/env/daas.jpg
COPY ./daas-logo.png /root/daas/env/daas-logo.png
RUN [ -f /usr/bin/python ] || ln -s /usr/bin/python3 /usr/bin/python

# qtile
COPY ./config.py /root/.config/qtile/config.py

# tigervnc
COPY ./tiger-vnc-password.txt /tiger-vnc-password.txt
EXPOSE 5900

# pulse audio
#COPY pulse-client.conf /root/pulse/client.config


# Terminal
COPY ./.bashrc /root/.bashrc
COPY ./.Xresources /root/.Xresources
# RUN mkdir /root/.wine32
# RUN mkdir /root/.wine64

# Test application
COPY ./app.exe /root/shared/.wine64/drive_c/app.exe
RUN chmod a+x /root/shared/.wine64/drive_c/app.exe

# entrypoint
COPY ./entrypoint.bash /entrypoint.bash
RUN chmod a+x /entrypoint.bash

USER wineuser
WORKDIR /home/wineuser

# 32 bit
RUN mkdir -p /home/wineuser/shared/.wine32
RUN WINEARCH=win32 WINEPREFIX=/home/wineuser/shared/.wine32 \
	xvfb-run -a wine wineboot -u
RUN WINEARCH=win32 WINEPREFIX=/home/wineuser/shared/.wine32 \
	xvfb-run -a winetricks arial corefonts

# 64 bit
RUN mkdir -p /home/wineuser/shared/.wine64
RUN WINEARCH=win64 WINEPREFIX=/home/wineuser/shared/.wine64 \
	xvfb-run -a wine wineboot -u

USER root
WORKDIR /

ENTRYPOINT [ "/entrypoint.bash" ]
