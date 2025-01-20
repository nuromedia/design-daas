echo off

:: Dhcp and Ntp renewal on boot
net start w32time
w32tm /resync /rediscover
ipconfig /release Eth
ipconfig /release Eth*
ipconfig /renew

:: Sync time
net start w32time
w32tm /resync /rediscover
w32tm /config /update
w32tm /register

:: Renew adapter IP (template dhcp-release might still be valid)
ipconfig /release
ipconfig /renew

