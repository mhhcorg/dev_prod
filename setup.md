### SSH (Simplified repo specific) 

* `New-Item -ItemType Directory -Path "$HOME\.ssh" -Force` 
* `Set-Location -Path "$HOME\.ssh"` 
* `Get-Location`
* `ssh-keygen -t- rsa -b 4096 -C "your_email@mhhc.org"`
* `gci -Path "$HOME\.ssh"`
* `gc "$HOME\.ssh\id_rsa.pub"`