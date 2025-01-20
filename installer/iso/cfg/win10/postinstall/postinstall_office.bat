echo off

:: VirtIO guest agent
D:\virtio\virtio-win-guest-tools.exe /install /passive /quite /norestart

:: Dhcp renewal on boot
REG ADD "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Run" /v "dhcprenew" /t REG_SZ /d "net start w32time && w32tm /resync /rediscover && ipconfig /release && ipconfig /renew" /f /REG:64

:: Sync time
net start w32time
w32tm /resync /rediscover
w32tm /config /update
w32tm /register

:: Renew adapter IP (template dhcp-release might still be valid)
ipconfig /release
ipconfig /renew

:: Some Tools
REM msiexec /package "D:\postinstall\tools\Firefox Setup 102.12.0esr.msi" /qr
REM D:\postinstall\tools\npp.8.5.3.Installer.x64.exe /S
REM D:\postinstall\tools\Git-2.41.0-64-bit.exe /SILENT
D:\postinstall\tools\python-3.11.4-amd64.exe /passive
msiexec /package "D:\postinstall\tools\Firefox_Setup_115.0.3.msi" /passive
powershell.exe "Remove-Item $env:USERPROFILE\AppData\Local\Microsoft\WindowsApps\python*.exe"

:: Office
start /WAIT D:\postinstall\tools\office\setup.exe /configure D:\postinstall\tools\office\configuration.xml
REG ADD "HKLM\SOFTWARE\Microsoft\Office\Common\Privacy" /v "DisableOptionalConnectedExperiences" /t REG_DWORD /d 1 /f /REG:32
REG ADD "HKCU\SOFTWARE\Policies\Microsoft\Office\16.0\Registration" /v "AcceptAllEulas" /t REG_DWORD /d 1 /f /REG:64
REG DELETE "HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\Run" /f /v "com.squirrel.Teams.Teams"
REG DELETE "HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\Run" /f /v "OneDrive"

:: Daas Environment
mkdir C:\Users\root\daas\env
xcopy /s /E /H /C /Y /I D:\postinstall\env\PSTools C:\Users\root\daas\env\pstools
xcopy /s /E /H /C /Y /I D:\postinstall\daas\CommandProxy.py C:\Users\root\daas\env
setx /M PATH "C:\Users\root\AppData\Local\Programs\Python\Python311\;C:\Users\root\AppData\Local\Programs\Python\Python311\Scripts\;C:\Users\root\daas\env\;C:\Users\root\daas\env\pstools;%PATH%"
C:\Users\root\AppData\Local\Programs\Python\Python311\python -m pip install --upgrade pip
C:\Users\root\AppData\Local\Programs\Python\Python311\Scripts\pip install click

:: Firewall (Allow icmp)
netsh advfirewall firewall add rule name="ICMP Allow incoming V4 echo request" protocol="icmpv4:8,any" dir=in action=allow
netsh advfirewall firewall add rule name="ICMP Allow incoming V6 echo request" protocol="icmpv6:8,any" dir=in action=allow
REM reg add HKEY_LOCAL_MACHINE\Software\Microsoft\Windows\CurrentVersion\Run /t REG_SZ /v ipconfig /d "ipconfig /renew"

:: SSH Client and Server
powershell.exe "Add-WindowsCapability -Online -Name OpenSSH.Client~~~~0.0.1.0"
powershell.exe "Add-WindowsCapability -Online -Name OpenSSH.Server~~~~0.0.1.0"
echo D | xcopy /s /Y /I D:\postinstall\ssh\id_rsa.pub C:\ProgramData\ssh\administrators_authorized_keys
echo D | xcopy /s /Y /I D:\postinstall\ssh\sshd_config C:\ProgramData\ssh\sshd_config
echo D | xcopy /s /Y /I D:\postinstall\ssh\id_rsa.pub C:\Users\root\.ssh\authorized_keys
powershell.exe "Set-Service ssh-agent -StartupType automatic"
powershell.exe "Start-Service ssh-agent"
powershell.exe "Set-Service sshd -StartupType automatic"
powershell.exe "Start-Service sshd"

:: Annoying Teams Update Screen
REG DELETE "HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\Run" /f /v "com.squirrel.Teams.Teams"

:: Windows update
:: powershell.exe -ExecutionPolicy Bypass "Install-Module PSWindowsUpdate -Confirm"
:: powershell.exe -ExecutionPolicy Bypass "Import-Module PSWindowsUpdate"
:: powershell.exe -ExecutionPolicy Bypass "Get-WindowsUpdate"
:: powershell.exe -ExecutionPolicy Bypass "Install-WindowsUpdate -AcceptAll"
:: Reboot
:: shutdown -f -r -t 1
::

