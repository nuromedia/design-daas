#!/bin/bash

VOLNAME=debian12
INCFOLDER=cfg/debian12
OUTFOLDER=out
ISOFOLDER=iso
QMSGFOLDER=../../src/app/daas/messaging
QINSTFOLDER=../../src/app/inst
ISONAME=${VOLNAME}-amd64-netinst
OUTNAME=${VOLNAME}-amd64-unattend
INFOLDER=$OUTFOLDER/$ISONAME
OUTFILE=$OUTFOLDER/${OUTNAME}
URL="https://cdimage.debian.org/mirror/cdimage/archive/12.0.0/amd64/iso-cd/debian-12.0.0-amd64-netinst.iso"
export DEBIAN_FRONTEND=noninteractive
ROOTPASS=root
HYBRIDMBR=/usr/lib/ISOLINUX/isohdpfx.bin

# Help
usage() {
    echo "Usage: $0 " 1>&2
    echo "      [-a <action>] [-n <isoname>]" 1>&2
    echo "      [-d <outdir>] [-i <incdir>]" 1>&2
    echo "      [-p <userpass>]" 1>&2
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
    sudo -E apt --yes install rsync syslinux syslinux-utils xorriso isolinux \
        1>&2 2>/dev/null
}
# clean
clean(){
    sudo umount "$MNTFOLDER" 1>&2 2>/dev/null
    rm -rf "$INFOLDER" "$MNTFOLDER"
    sudo rm -rf "$MODFOLDER"
    rm -rf "$INFOLDER"
}

# Download
download() {
    mkdir -p "$ISOFOLDER"
    if [ ! -f "$ISOFILE" ] ; then
        wget -O "$ISOFILE" "$URL"
    fi
}

# Mount and extract
copybase(){
    mkdir -p "$MNTFOLDER" "$INFOLDER"
    sudo mount -o loop "$ISOFILE" "$MNTFOLDER"
    rsync -a -H --exclude=TRANS.TBL "$MNTFOLDER"/ "$INFOLDER"
    chmod 755 -R "$INFOLDER"
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
    mkdir -p "$INFOLDER"/postinstall/
    cp -r "$INCFOLDER"/ssh -t "$INFOLDER"/postinstall/
    cp -r "$INCFOLDER"/postinstall/*.bash -t "$INFOLDER"/postinstall/
    cp -r "$INCFOLDER"/postinstall/*.sh -t "$INFOLDER"/postinstall/
    cp -r "$INCFOLDER"/postinstall/daas.jpg -t "$INFOLDER"/postinstall/
    cp -r "$INCFOLDER"/postinstall/daas-logo.png -t "$INFOLDER"/postinstall/
    cp -r "$INCFOLDER"/postinstall/config.py -t "$INFOLDER"/postinstall/
    cp -r "$INCFOLDER"/postinstall/qtile.desktop -t "$INFOLDER"/postinstall/
    cp -r "$INCFOLDER"/isolinux/* -t "$INFOLDER"/isolinux
    sed 's/initrd.gz/initrd.gz file=\/cdrom\/preseed.cfg/' \
        -i "$INFOLDER/isolinux/txt.cfg"
    cp -r "$INCFOLDER"/preseed.cfg "$INFOLDER"/preseed.cfg
    sed "s/root-password password root/root-password password $ROOTPASS/" \
        -i "$INFOLDER/preseed.cfg"
    sed "s/root-password-again password root/root-password-again password $ROOTPASS/" \
        -i "$INFOLDER/preseed.cfg"
    rm -rf "$INFOLDER"/postinstall/daas/qmsg
    mkdir -p "$INFOLDER"/postinstall/daas/qmsg
    mkdir -p "$INFOLDER"/postinstall/daas/env
    cp -r "$QMSGFOLDER"/* "$INFOLDER"/postinstall/daas
    cp -r "$QINSTFOLDER"/* "$INFOLDER"/postinstall/daas/env
    cp /root/.ssh/id_rsa.pub "$INFOLDER"/postinstall/ssh/authorized_keys 
}

# Generate iso
geniso(){
    md5sum "$(find "$INFOLDER" -type f)" > "$INFOLDER"/md5sum.txt
    xorriso -as mkisofs \
      -r \
      -J \
      -V "$VOLNAME" \
      -c isolinux/boot.cat \
      -b isolinux/isolinux.bin \
      -no-emul-boot \
      -boot-info-table \
      -boot-load-size 4 \
      -partition_offset 16 \
      -isohybrid-mbr "$HYBRIDMBR" \
      -o "$OUTFILE".iso \
      "./$INFOLDER"
}
# Update initrd
irmod(){
    sudo rm -fr "$MODFOLDER"/
    sudo mkdir -p "$MODFOLDER"
    BASEDIR=$(realpath "$INFOLDER")
    gzip -d < "$INFOLDER"/install.amd/initrd.gz | sudo cpio -D "$MODFOLDER" \
        --extract --make-directories --no-absolute-filenames
    sudo cp "$INCFOLDER"/preseed.cfg "$MODFOLDER"/preseed.cfg
    sudo chown root:root "$MODFOLDER"/preseed.cfg
    sudo chmod o+w "$INFOLDER"/install.amd/initrd.gz
    cd "$MODFOLDER" || exit 1
    find . | cpio -H newc --create | gzip -9 \
        > "$BASEDIR"/install.amd/initrd.gz
    cd - || exit 1
    sudo chmod o-w "$INFOLDER"/install.amd/initrd.gz
    sudo rm -fr "$MODFOLDER"/
}

while getopts ":a:p:d:i:n:" o; do
    case "$o" in
        a)
            ACTION=${OPTARG}
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

MNTFOLDER=$OUTFOLDER/mnt
MODFOLDER=$OUTFOLDER/irmod
INFOLDER=$OUTFOLDER/$ISONAME
ISOFILE=$ISOFOLDER/${ISONAME}.iso
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
        ;;
    "generate")
        [[ -z "$ISONAME" ]] && echo "No Isoname specified" && usage && exit 1
        clean
        # toolinstall
        download
        copybase
        copyaddons
        irmod >/dev/null
        geniso
        ;;
     *)
        echo "Not a valid target: '$1'"
        ;;
esac

