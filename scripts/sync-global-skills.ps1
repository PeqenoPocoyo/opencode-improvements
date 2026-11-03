$src = "C:\backups\opencode-global"
$dst = "$env:USERPROFILE\.config\opencode"
New-Item -ItemType Directory -Force -Path $dst | Out-Null
robocopy "$src\skills" "$dst\skills" /E /MT:8 /FFT /R:2 /W:1
Copy-Item "$src\instructions.md" "$dst\" -Force -ErrorAction SilentlyContinue
Copy-Item "$src\settings.json" "$dst\" -Force -ErrorAction SilentlyContinue
Write-Host "Sync finished to $dst"