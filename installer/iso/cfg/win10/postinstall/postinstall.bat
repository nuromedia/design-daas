echo off

:: VirtIO guest agent
D:\virtio\virtio-win-guest-tools.exe /install /passive /quite /norestart

:: DHCP and NTP setup
echo D | xcopy /s /Y /I D:\postinstall\startup.bat C:\Users\root\daas\env\startup.bat
echo D | xcopy /s /Y /I D:\postinstall\regenerate_ip.ps1 C:\Users\root\daas\env\regenerate_ip.ps1

:: Proceed installing after first reboot
REG ADD "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\RunOnce" /v "daasreboot" /t REG_SZ /d D:\postinstall\postinstall.bat /f /REG:64

:: Ceph
msiexec /package "D:\postinstall\tools\ceph_reef_beta.msi" /quiet /passive
msiexec /package "D:\postinstall\tools\Dokan_x64-1.0.5.1000.msi" /passive
msiexec /package "D:\postinstall\tools\DokanSetup_redist-1.0.5.1000.exe" /passive
msiexec /package "D:\postinstall\tools\Dokan_x64.msi" /passive

:: Firefox
msiexec /package "D:\postinstall\tools\Firefox_Setup_115.0.3.msi" /passive

:: TightVNC
msiexec /package "D:\postinstall\tools\tightvnc-2.8.81-gpl-setup-64bit.msi" /passive

:: Office
:: start /WAIT D:\postinstall\tools\office\setup.exe /configure D:\postinstall\tools\office\configuration.xml
:: REG ADD "HKLM\SOFTWARE\Microsoft\Office\Common\Privacy" /v "DisableOptionalConnectedExperiences" /t REG_DWORD /d 1 /f /REG:32
:: REG ADD "HKCU\SOFTWARE\Policies\Microsoft\Office\16.0\Registration" /v "AcceptAllEulas" /t REG_DWORD /d 1 /f /REG:64
:: REG DELETE "HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\Run" /f /v "com.squirrel.Teams.Teams"
:: REG DELETE "HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\Run" /f /v "OneDrive"

:: Python
D:\postinstall\tools\python-3.11.4-amd64.exe /passive
powershell.exe "Remove-Item $env:USERPROFILE\AppData\Local\Microsoft\WindowsApps\python*.exe"

:: Python Environment
mkdir C:\Users\root\daas\mnt
mkdir C:\Users\root\daas\mnt\public
mkdir C:\Users\root\daas\mnt\shared
mkdir C:\Users\root\daas\mnt\user
mkdir C:\Users\root\daas\env
mkdir C:\Users\root\daas\qmsg
mkdir C:\Users\root\daas\qmsg\sender
mkdir C:\Users\root\daas\qmsg\receiver
mkdir C:\Users\root\daas\qmsg\common
mkdir C:\Users\root\daas\status
xcopy /s /E /H /C /Y /I D:\postinstall\env\PSTools C:\Users\root\daas\env\pstools
xcopy /s /E /H /C /Y /I D:\postinstall\daas\* C:\Users\root\daas\
setx /M PATH "C:\Users\root\AppData\Local\Programs\Python\Python311\;C:\Users\root\AppData\Local\Programs\Python\Python311\Scripts\;C:\Users\root\daas\env\;C:\Users\root\daas\env\pstools;%PATH%"
C:\Users\root\AppData\Local\Programs\Python\Python311\python -m pip install --upgrade pip
C:\Users\root\AppData\Local\Programs\Python\Python311\Scripts\pip install click psutil pywin32 pika

:: Firewall (Allow icmp)
netsh advfirewall firewall add rule name="ICMP Allow incoming V4 echo request" protocol="icmpv4:8,any" dir=in action=allow
netsh advfirewall firewall add rule name="ICMP Allow incoming V6 echo request" protocol="icmpv6:8,any" dir=in action=allow

:: RDP
reg add "HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\Terminal Server" /v fDenyTSConnections /t REG_DWORD /d 0 /f
powershell.exe "Enable-NetFirewallRule -DisplayGroup 'Remotedesktop'"
sc config TermService start= auto
net start TermService

:: Winget
powershell.exe "Add-AppxPackage D:\postinstall\tools\Microsoft.VCLibs.x64.14.00.Desktop.appx"
powershell.exe "Add-AppxPackage D:\postinstall\tools\Microsoft.UI.Xaml.2.8.x64.appx"
powershell.exe "Add-AppxPackage D:\postinstall\tools\Microsoft.DesktopAppInstaller_8wekyb3d8bbwe.msixbundle"

:: SSH Client and Server
powershell.exe "Add-WindowsCapability -Online -Name OpenSSH.Client~~~~0.0.1.0"
powershell.exe "Add-WindowsCapability -Online -Name OpenSSH.Server~~~~0.0.1.0"
echo D | xcopy /s /Y /I D:\postinstall\ssh\authorized_keys C:\ProgramData\ssh\administrators_authorized_keys
echo D | xcopy /s /Y /I D:\postinstall\ssh\sshd_config C:\ProgramData\ssh\sshd_config
echo D | xcopy /s /Y /I D:\postinstall\ssh\authorized_keys C:\Users\root\.ssh\authorized_keys
powershell.exe "Set-Service ssh-agent -StartupType automatic"
powershell.exe "Start-Service ssh-agent"
powershell.exe "Set-Service sshd -StartupType automatic"
powershell.exe "Start-Service sshd"

:: Set Wallpaper
echo D | xcopy /s /Y /I D:\postinstall\daas.jpg C:\Users\root\daas\env\daas.jpg
echo D | xcopy /s /Y /I D:\postinstall\daas-logo.png C:\Users\root\daas\env\daas-logo.png
reg add "HKEY_CURRENT_USER\Control Panel\Desktop" /v Wallpaper /t REG_SZ /d "C:\Users\root\daas\env\daas.jpg" /f
reg add "HKEY_CURRENT_USER\Control Panel\Desktop" /v WallpaperStyle /t REG_SZ /d 10 /f
reg add "HKEY_CURRENT_USER\Control Panel\Desktop" /v TileWallpaper /t REG_SZ /d 0 /f
RUNDLL32.EXE user32.dll,UpdatePerUserSystemParameters

:: Enable regular reboot
REG ADD "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Run" /v "daasstartup" /t REG_SZ /d "powershell.exe -ExecutionPolicy Bypass -WindowStyle Hidden -File \"C:\Users\root\daas\env\regenerate_ip.ps1\"" /f /REG:64
start /b cmd.exe /C powershell.exe -ExecutionPolicy Bypass -WindowStyle Hidden -File "C:\Users\root\daas\env\regenerate_ip.ps1"

:: Finalize installation
REG DELETE "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\RunOnce" /v "daasreboot" /f
echo INSTALLED > C:\Users\root\daas\status\installer.log

shutdown /r /t 0



