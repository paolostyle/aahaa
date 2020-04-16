$cwd = Get-Location
$volumePath = Join-Path -Path $cwd -ChildPath "screens"

Invoke-Expression "poetry export -f requirements.txt -o requirements.txt"
Invoke-Expression "docker rm afkapi -fv"
Invoke-Expression "docker build -t afk-arena-api ."
Invoke-Expression "docker run -d --name afkapi -v ${volumePath}:/app/screens -p 8080:8080 afk-arena-api"
Remove-Item -Path "./requirements.txt"
