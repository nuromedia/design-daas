
# Get all network adapters that are up
$adapters = Get-NetAdapter | Where-Object { $_.Status -eq 'Up' }

# Disable all network adapters
foreach ($adapter in $adapters) {
    Disable-NetAdapter -Name $adapter.Name -Confirm:$false
}

# Pause for a few seconds to ensure the adapters are fully disabled
Start-Sleep -Seconds 2

# Enable all network adapters
foreach ($adapter in $adapters) {
    Enable-NetAdapter -Name $adapter.Name -Confirm:$false
}

Invoke-Expression "ipconfig /release"
Invoke-Expression "ipconfig /renew"

echo "Query user session"
$foo = Invoke-Expression "query user"
$sessionID = $foo | Select-String -Pattern "\s(\d+)\s" | ForEach-Object{
	$_.MATCHES[0].Groups[1].Value
}
echo "Got session: $sessionID"

echo "Running receiver"
$pstoolsArgs = "C:/Users/root/daas/env/pstools/psexec.exe -nobanner -accepteula -i $sessionID -u root -p root"
$receiverArgs = "pythonw  C:/Users/root/daas/runner_instance.py"
$arglist = "/c $pstoolsArgs $receiverArgs"
echo "Running receiver with '$arglist'"
Start-Process cmd.exe -WindowStyle Hidden  -ArgumentList $arglist
