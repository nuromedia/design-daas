#!/bin/bash

# Default config
VOLNAME=Win11
INCFOLDER=cfg/win11
OUTFOLDER=out
ISOFOLDER=iso
QMSGFOLDER="../../src/app/daas/messaging"
QINSTFOLDER="../../src/app/inst"
ISONAME=${VOLNAME}_23H2_German_x64v2
ISONAME_VIO=virtio-win-0.1.266
OUTNAME=${VOLNAME}-23H2_German_x64_unattend
INFOLDER=$OUTFOLDER/$ISONAME
OUTFILE=$OUTFOLDER/${OUTNAME}
VIRTIOFOLDER=$OUTFOLDER/${ISONAME_VIO}
# Enable link at: https://www.microsoft.com/de-de/software-download/windows10ISO
URL_WIN="https://software.download.prss.microsoft.com/dbazure/Win11_23H2_German_x64v2.iso?t=b00a5577-dd76-445c-bb14-325a855593d8&P1=1727830683&P2=601&P3=2&P4=ZYD5moomMv6b5FgWCYk%2bHX3l4UWYMLh8ME8V4Nrjye5l7ECGucuzsDSojlmWQGS4eNfmTYoM5UUgGsKluKy0NialBEGm%2bgMoMqQg3%2b%2bWgzvaAxbWob083Gz3UtjTdT%2bCt%2bUFnj8Z4D3OyKUU0%2bQhrPX%2f4TaWFXDrxARSdusl8MrSaWWPZGDNNRgtPGi9fxX3hGoqPS95kHSdwekMtE8PvbsLZfiEYn4aB2H51YhtoLCzhg6t%2bSVRSvN6xau00M27LsiyTDSRlbR2gtPzj0Vctkpy0pREuLl5%2btWziqXv%2fppJl6EdCBXHa4OHnspm55osHAEMvnIxjdPhW6BeDl%2fyjw%3d%3d"
URL_VIRTIO="https://fedorapeople.org/groups/virt/virtio-win/direct-downloads/archive-virtio/virtio-win-0.1.266-1/virtio-win-0.1.266.iso"
URL_PYTHON="https://www.python.org/ftp/python/3.11.4/python-3.11.4-amd64.exe"
URL_FIREFOX="https://download-installer.cdn.mozilla.net/pub/firefox/releases/115.0.3/win64/de/Firefox%20Setup%20115.0.3.msi"
URL_PSTOOLS="https://download.sysinternals.com/files/PSTools.zip"
URL_OFFICE="https://web.opendrive.com/api/v1/download/file.json/NTNfNDQzNDYxOTdfSTB6ZkM?inline=0"
URL_TIGHTVNC="https://www.tightvnc.com/download/2.8.81/tightvnc-2.8.81-gpl-setup-64bit.msi"
INSTALLER_OFFICE="DE_Office_2021_Professional_Plus_64Bit_v.exe"
URL_WINGET="https://aka.ms/getwinget"
URL_VCLIBS="https://aka.ms/Microsoft.VCLibs.x64.14.00.Desktop.appx"
URL_XAML="https://github.com/microsoft/microsoft-ui-xaml/releases/download/v2.8.6/Microsoft.UI.Xaml.2.8.x64.appx"
URL_CEPH="https://cloudbase.it/downloads/ceph_reef_beta.msi"
URL_DOKANY1="https://github.com/dokan-dev/dokany/releases/download/v1.0.5/Dokan_x64-1.0.5.1000.msi"
URL_DOKANY2="https://github.com/dokan-dev/dokany/releases/download/v2.1.0.1000/Dokan_x64.msi"
URL_DOKANYSETUP="https://github.com/dokan-dev/dokany/releases/download/v1.0.5/DokanSetupDbg_redist-1.0.5.1000.exe"

USERNAME=root
ROOTPASS=root
export DEBIAN_FRONTEND=noninteractive

# Help
usage() {
    echo "Usage: $0 " 1>&2
    echo "      [-a <action>] [-n <isoname>]" 1>&2
    echo "      [-u <username>] [-p <userpass>]" 1>&2
    echo "      [-d <outdir>] [-i <incdir>]" 1>&2
    echo "      " 1>&2
    echo "      Action  : [clean,install,download,generate]" 1>&2
    echo "      Isoname : [isoname in ./iso without extension]" 1>&2
    echo "      Username: [Hostname to connect to (Default: localhost)]" 1>&2
    echo "      Userpass: [User name (Default: root)]" 1>&2
    echo "      Outdir  : [Output folder (Default: ./out)]" 1>&2
    echo "      IncDir  : [Include folder (Default: ./config)]" 1>&2
}

# install
toolinstall(){
    sudo -E apt --yes install rsync unzip unrar isolinux 1>&2 2>/dev/null
}
# clean
clean(){
    sudo umount "$MNTFOLDER" 1>&2 2>/dev/null
    rm -rf "$INFOLDER" "$MNTFOLDER" "$VIRTIOFOLDER"
    sudo rm -rf "$MODFOLDER"
}

# Download
download() {
    mkdir -p "$ISOFOLDER"
    if [ ! -f "$ISOFILE" ] ; then
        wget -O "$ISOFILE" "$URL_WIN"
    fi
    if [ ! -f "$ISOFILE_VIO" ] ; then
        wget -O "$ISOFILE_VIO" "$URL_VIRTIO"
    fi
}
download_tools() {
    mkdir -p "$INCFOLDER/tools"
    if [ ! -f "$INCFOLDER/tools/python-3.11.4-amd64.exe" ] ; then
        wget -O "$INCFOLDER/tools/python-3.11.4-amd64.exe" "$URL_PYTHON"
    fi
    if [ ! -f "$INCFOLDER/tools/Firefox_Setup_115.0.3.msi" ] ; then
        wget -O "$INCFOLDER/tools/Firefox_Setup_115.0.3.msi" "$URL_FIREFOX"
    fi
    if [ ! -f "$INCFOLDER/tools/tightvnc-2.8.81-gpl-setup-64bit.msi" ] ; then
        wget -O "$INCFOLDER/tools/tightvnc-2.8.81-gpl-setup-64bit.msi" "$URL_TIGHTVNC"
    fi
    if [ ! -f "$INCFOLDER/tools/Microsoft.DesktopAppInstaller_8wekyb3d8bbwe.msixbundle" ] ; then
        wget -O "$INCFOLDER/tools/Microsoft.DesktopAppInstaller_8wekyb3d8bbwe.msixbundle" "$URL_WINGET"
    fi
    if [ ! -f "$INCFOLDER/tools/Microsoft.VCLibs.x64.14.00.Desktop.appx" ] ; then
        wget -O "$INCFOLDER/tools/Microsoft.VCLibs.x64.14.00.Desktop.appx" "$URL_VCLIBS"
    fi
    if [ ! -f "$INCFOLDER/tools/Microsoft.UI.Xaml.2.8.x64.appx" ] ; then
        wget -O "$INCFOLDER/tools/Microsoft.UI.Xaml.2.8.x64.appx" "$URL_XAML"
    fi
    if [ ! -f "$INCFOLDER/tools/ceph_reef_beta.msi" ] ; then
        wget -O "$INCFOLDER/tools/ceph_reef_beta.msi" "$URL_CEPH"
    fi
    if [ ! -f "$INCFOLDER/tools/Dokan_x64-1.0.5.1000.msi" ] ; then
        wget -O "$INCFOLDER/tools/Dokan_x64-1.0.5.1000.msi" "$URL_DOKANY1"
    fi
    if [ ! -f "$INCFOLDER/tools/Dokan_x64.msi" ] ; then
        wget -O "$INCFOLDER/tools/Dokan_x64.msi" "$URL_DOKANY2"
    fi
    if [ ! -f "$INCFOLDER/tools/DokanSetup_redist-1.0.5.1000.exe" ] ; then
        wget -O "$INCFOLDER/tools/DokanSetup_redist-1.0.5.1000.exe" "$URL_DOKANYSETUP"
    fi

    mkdir -p "$INCFOLDER/env"
    if [ ! -f "$INCFOLDER/env/PSTools.zip" ] ; then
        wget -O "$INCFOLDER/env/PSTools.zip" "$URL_PSTOOLS"
    fi
    if [ ! -d "$INCFOLDER/env/PSTools" ] ; then
        unzip "$INCFOLDER/env/PSTools.zip" -d "$INCFOLDER/env/PSTools"
    fi
    mkdir -p "$INCFOLDER/tools/office"
    if [ ! -f "$INCFOLDER/tools/office/$INSTALLER_OFFICE" ] ; then
        wget -O "$INCFOLDER/tools/office/$INSTALLER_OFFICE" "$URL_OFFICE"
    fi
    if [ ! -f "$INCFOLDER/tools/office/setup.exe" ] ; then
        unrar e "$INCFOLDER/tools/office/$INSTALLER_OFFICE" "$INCFOLDER/tools/office/"
        sed 's#</Product>#<ExcludeApp ID="Teams" /></Product>#g' \
            -i "$INCFOLDER/tools/office/configuration.xml"
    fi
}

# Mount and extract
copybase(){
    mkdir -p "$MNTFOLDER" "$INFOLDER"
    sudo mount -o loop "$ISOFILE" "$MNTFOLDER"
    rsync -a -H --exclude=TRANS.TBL "$MNTFOLDER"/ "$INFOLDER"
    chmod 755 -R "$INFOLDER"
    sudo umount "$MNTFOLDER"

    sudo mount -o loop "$ISOFILE_VIO" "$MNTFOLDER"
    rsync -a -H --exclude=TRANS.TBL "$MNTFOLDER"/ "$VIRTIOFOLDER"
    chmod 755 -R "$VIRTIOFOLDER"
    sudo umount "$MNTFOLDER"
    sudo rm -rf "$MNTFOLDER"
}

# Ensure ssh key
ensurekey(){
    if [[ ! -f "$INCFOLDER"/ssh/id_rsa.pub ]] ; then
        mkdir -p "$INCFOLDER"/ssh
        if [[ -r /root/.ssh/id_rsa ]] ; then
            cp /root/.ssh/id_rsa* "$INCFOLDER"/ssh
        else
            ssh-keygen -t rsa -N '' -f "$INCFOLDER"/ssh/id_rsa
        fi
    fi
}

# Copy addons
copyaddons(){
    ensurekey
    mkdir -p "$INFOLDER"/postinstall/daas/env
    cp -r "$INCFOLDER"/ssh -t "$INFOLDER"/postinstall/
    cp -r "$INCFOLDER"/env -t "$INFOLDER"/postinstall/
    cp -r "$INCFOLDER"/tools -t "$INFOLDER"/postinstall/
    cp -r "$INCFOLDER"/postinstall/*.bat -t "$INFOLDER"/postinstall/
    cp -r "$INCFOLDER"/postinstall/*.ps1 -t "$INFOLDER"/postinstall/
    cp -r "$INCFOLDER"/postinstall/daas.jpg "$INFOLDER"/postinstall/daas.jpg
    cp -r "$INCFOLDER"/postinstall/daas-logo.png "$INFOLDER"/postinstall/daas-logo.png
    cp -r "$INCFOLDER"/autounattend.xml "$INFOLDER"/autounattend.xml
    cp -r "$QMSGFOLDER"/* "$INFOLDER"/postinstall/daas/env
    cp -r "$QMSGFOLDER"/* "$INFOLDER"/postinstall/daas/qmsg
    cp -r "$QINSTFOLDER"/* "$INFOLDER"/postinstall/daas/qmsg/env
    cp -r "$QMSGFOLDER"/../*.py "$INFOLDER"/postinstall/daas/
    cp /root/.ssh/id_rsa.pub authorized_keys 
    cp -r "$VIRTIOFOLDER" "$INFOLDER"/virtio
}

updateuser() {
    sed "s#<Name>user</Name>#<Name>$USERNAME</Name>#g" \
         -i "$INFOLDER/autounattend.xml"
    sed "s#<Username>user</Username>#<Username>$USERNAME</Username>#g" \
         -i "$INFOLDER/autounattend.xml"
    sed "s#<UserName>user</UserName>#<UserName>$USERNAME</UserName>#g" \
         -i "$INFOLDER/autounattend.xml"
    sed "s#<FullName>user</FullName>#<FullName>$USERNAME</FullName>#g" \
         -i "$INFOLDER/autounattend.xml"
    sed "s#<DisplayName>user</DisplayName>#<DisplayName>$USERNAME</DisplayName>#g" \
         -i "$INFOLDER/autounattend.xml"
    sed "s#<RegisteredOwner>user</RegisteredOwner>#<RegisteredOwner>$USERNAME</RegisteredOwner>#g" \
         -i "$INFOLDER/autounattend.xml"
    sed "s#<Value>user</Value>#<Value>$ROOTPASS</Value>#g" \
         -i "$INFOLDER/autounattend.xml"
    sed "s#C:\\\\Users\\\\root\\\\#C:\\\\Users\\\\$USERNAME\\\\#g" \
         -i "$INFOLDER/postinstall/postinstall.bat"
}

# Generate iso
geniso(){
	mkdir -p "$OUTFOLDER"
	mkisofs  -allow-limited-size \
		-V "$VOLNAME" \
		-no-emul-boot \
		-b boot/etfsboot.com \
		-boot-load-seg 0x07C0 \
		-boot-load-size 8 \
		-iso-level 2 \
		-udf \
		-joliet \
		-D \
		-N \
		-relaxed-filenames \
		-o "$OUTFILE".iso \
		"$INFOLDER"
	#sudo rm -rf $(DATAFOLDER)
}

# Read params
while getopts ":a:u:p:d:i:n:" o; do
    case "$o" in
        a)
            ACTION=${OPTARG}
            ;;
        u)
            USERNAME=${OPTARG}
            ;;
        p)
            ROOTPASS=${OPTARG}
            ;;
        d)
            OUTFOLDER=${OPTARG}
            ;;
        i)
            INCFOLDER=${OPTARG}
            ;;
        n)
            OUTNAME=${OPTARG}
            ;;
        *)
            ;;
    esac
done
shift $((OPTIND-1))

# Dynamic vars
MNTFOLDER=$OUTFOLDER/mnt
MODFOLDER=$OUTFOLDER/irmod
INFOLDER=$OUTFOLDER/$ISONAME
VIRTIOFOLDER=$OUTFOLDER/${ISONAME_VIO}
ISOFILE=$ISOFOLDER/${ISONAME}.iso
ISOFILE_VIO=$ISOFOLDER/${ISONAME_VIO}.iso
OUTFILE=$ISOFOLDER/${OUTNAME}

# Execute action
case "$ACTION" in
    "clean")
        [[ -z "$ISONAME" ]] && echo "No Isoname specified" && usage && exit 1
        clean
        ;;
    "install")
        [[ -z "$ISONAME" ]] && echo "No Isoname specified" && usage && exit 1
        toolinstall
        ;;
    "download")
        [[ -z "$ISONAME" ]] && echo "No Isoname specified" && usage && exit 1
        download
        download_tools
        ;;
    "generate")
        [[ -z "$ISONAME" ]] && echo "No Isoname specified" && usage && exit 1
        clean
        # toolinstall
        download
        download_tools
        copybase
        copyaddons
        updateuser
        geniso
        ;;
     *)
        echo "Not a valid target: '$1'"
        ;;
esac
