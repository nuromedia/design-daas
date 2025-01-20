#!/bin/bash

# WINEARCH=win64
# WINEPREFIX=/root/.wine64
#
# # Create wine environments
# chown -R root:root /root/.wine32
# #chown -R root:root /root/.wine64
# WINEARCH=win32 WINEPREFIX=/root/.wine32 winetricks -q --optout arch=32
# #WINEARCH=win64 WINEPREFIX=/root/.wine64 winetricks -q --optout arch=64
#
# # Tools
# WINEARCH=win32 WINEPREFIX=/root/.wine32 winetricks -q --optout arial corefonts
# #WINEARCH=win32 WINEPREFIX=/root/.wine32 winetricks -q --optout ie8
# #WINEARCH=win32 WINEPREFIX=/root/.wine32 winetricks -q --optout ie8
# WINEARCH=win32 WINEPREFIX=/root/.wine32 winetricks -q --optout urlmon \
#     d3dx9 vcrun2005 vcrun2015 wininet
#

# Create a Wine prefix for Battle.net
RUN winecfg && \
	WINEARCH=win64 WINEPREFIX="/home/wineuser/battlenet-prefix" wineboot

# Download Battle.net installer (adjust the URL as needed)
wget -O /home/wineuser/battlenet-installer.exe https://eu.battle.net/download/getInstaller?os=win&installer=Battle.net-Setup.exe

# Install Battle.net using the downloaded installer
WINEARCH=win64 WINEPREFIX="/home/wineuser/battlenet-prefix" wine /home/wineuser/battlenet-installer.exe

# Clean up unnecessary files
rm /home/wineuser/battlenet-installer.exe

# Run Battle.net (replace with your specific Battle.net launcher executable)
wine /home/wineuser/battlenet-prefix/drive_c/Program Files\ (x86)/Battle.net/Battle.net.exe

