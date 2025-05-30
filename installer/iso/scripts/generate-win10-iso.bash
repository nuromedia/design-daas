#!/bin/bash

# Default config
VOLNAME=Win10
INCFOLDER=cfg/win10
OUTFOLDER=out
ISOFOLDER=iso
QMSGFOLDER="../../src/app/daas/messaging"
QINSTFOLDER="../../src/app/inst"
ISONAME=${VOLNAME}_22H2_German_x64v1
ISONAME_VIO=virtio-win-0.1.266
OUTNAME=${VOLNAME}-22H2_German_x64_unattend
INFOLDER=$OUTFOLDER/$ISONAME
OUTFILE=$OUTFOLDER/${OUTNAME}
VIRTIOFOLDER=$OUTFOLDER/${ISONAME_VIO}
# Enable link at: https://www.microsoft.com/de-de/software-download/windows10ISO
URL_WIN="https://software.download.prss.microsoft.com/dbazure/Win10_22H2_German_x64v1.iso?t=d00249f6-b289-4d03-82d3-8cb0b549345c&P1=1727830592&P2=601&P3=2&P4=imzKlIRAyyB1Dy6D51Sc6nOyFIigyA4saJLVBP4%2fYzoihad6IV2nqmmpHK%2flH6uIiZDsIIIcKyqprcuOiFtTcKtExqTHoHuIAU5%2bUN%2blDHeW7hKI18lqEALskT0PzswZlUm5PJqLvwi2Wv8BNg3LyK4K0d%2f0B0b74VN%2bmMDfXjsd9c1ribCOBFluDbCsra3dJm6%2b4dlaXKR5FpVJkuMx7JWA7pj7JNTYGUe4UfdxdM1RPCmpuzeBy9Ww6jsICv29K%2fPmfEw72P57v9ta7LSAwdEu0x3ex0gayMi2%2bE0HQtCrDpuhIoiqREYqaark1BJosix90yMAQsfUBvJ9%2b3HG%2bA%3d%3d"
URL_VIRTIO="https://fedorapeople.org/groups/virt/virtio-win/direct-downloads/archive-virtio/virtio-win-0.1.266-1/virtio-win-0.1.266.iso"
URL_PYTHON="https://www.python.org/ftp/python/3.11.4/python-3.11.4-amd64.exe"
URL_FIREFOX="https://download-installer.cdn.mozilla.net/pub/firefox/releases/115.0.3/win64/de/Firefox%20Setup%20115.0.3.msi"
URL_PSTOOLS="https://download.sysinternals.com/files/PSTools.zip"
URL_OFFICE="https://public.boxcloud.com/d/1/b1!SIlDeNnzgjmpSyIw3RJmuU5gFwrSF9RZQtKKYRLhR40d9cjPwlpM6gUgyIllL7Jb-1lc8rCPtt_EPsSqv3ylIYezMeWcREDI5C7_YLQZi9xsrmU_AvjpM47E9IDTKc36WAmow5jKdU3OzRqOgWSHR4vepnREYoWj2-do4Mxfro8XD4HBevd4YgOBngkPKUsT3Q7hDpFqzxo5zZ5OVw8RZeyY11NWxMQx-ujD4S7CKjTPtrjlMPb39J_6qP-Nk4an0iFU8iDClEKMKkSupOvdcdCbM7MzEqDP4jZPJWfGma89Homq7zCkYMAjAWorUXPs-eDzrDY4wq5UdhYO5LpmYCgO_xmYsD2Zan35CVtWcflhmKU7Ij5UufwHmu-ZbN6J8CBdfid4STX8bblHotWKL5r654mACQCWLc2nY22_Yshe6oRPsFBNGCNLs4Avcs_8kZAg4c1XUxv3H9DuIGmklV0evnuhOJP9g0KbX-e6zOrVLlT2MoZwYGHgEoyCdSo6uPyztuH82LwNxvuqum5c0QsJmAC7lbP1FWKGoI17o0ZrmZR9N4VA0dITvR-dxAmoKTQQ8t1DDvMxSJLV86LmIEEXZVRs1xjkc5gn8q4OiWGNQKEz7QHJa2i-ZSY1KMiEw6E9CxjC149PUNaFqICgiAM3NoD2g6prwu51mLR57TyaJPRH9c-6ooVaYPX_6QgDOVvVjLsQUhHFAoSe1Ulbs-LI9vQWkekYNY9Ku7XdS3fC1T7HlUU9-_tE7iWgijU48wSZOBf7rTK9GLStUfqxcphZib_1K9ncsURKpOm2rXP8ok9lohQTK8lHkLDYQduJGQKfa_no3v4qtLlaXMsaQKiCB3qWhjoM3OrtB-GyFjx6bi_Hmbol9znNWra3hNZnBb8jtWbDUGqzxft7CUfmCC3aR-ej2msVDWwp-XgfFKrWpM-OIyRsz7nY6IxXNdYn4Xx0uqinYGYHnday2agRpst7VH7_T2UvtFEZBj1hx47VbiCyONNPAKiSV2JpHY-tmZUYAdg06RpVJjQCx1oI3n2HzWkfPdhI0BCa60NRuOg9zIutZFTuOkDLRXCinudfrtEh4JMv-7WWv1OP_TPtSpv4l0OmXMLRibvPjDjUFqw77NYTzwDfTaLr-FHU-IlSQDFmt9CUOf4kaOJ421eDy6JX8YHoZR5Y5wV9EWNNPH3INLUu7cnDTx9oa0OZsYc1CCb2lmwbPcPgDAWU3xeYvd9LI1RpKW33ll530n8rhd5Ipl3xo82UhPLZNdtGkSLJBwGsZjpZuoXzZs6z-nKBbSmwpCphQKVue2dtnfwn/download"
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
    mkdir -p "$INFOLDER"/postinstall/daas
    mkdir -p "$INFOLDER"/postinstall/daas/env
    cp -r "$INCFOLDER"/ssh -t "$INFOLDER"/postinstall/
    cp -r "$INCFOLDER"/env -t "$INFOLDER"/postinstall/
    cp -r "$INCFOLDER"/tools -t "$INFOLDER"/postinstall/
    cp -r "$INCFOLDER"/postinstall/*.bat -t "$INFOLDER"/postinstall/
    cp -r "$INCFOLDER"/postinstall/*.ps1 -t "$INFOLDER"/postinstall/
    cp -r "$INCFOLDER"/postinstall/daas.jpg "$INFOLDER"/postinstall/daas.jpg
    cp -r "$INCFOLDER"/postinstall/daas-logo.png "$INFOLDER"/postinstall/daas-logo.png
    cp -r "$INCFOLDER"/autounattend.xml "$INFOLDER"/autounattend.xml
    cp -r "$QMSGFOLDER"/* "$INFOLDER"/postinstall/daas/
    cp -r "$QINSTFOLDER"/* "$INFOLDER"/postinstall/daas/env
    cp /root/.ssh/id_rsa.pub "$INFOLDER"/postinstall/ssh/authorized_keys
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
    sed "s#C:\\\\Users\\\\user\\\\#C:\\\\Users\\\\$USERNAME\\\\#g" \
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
        #toolinstall
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
