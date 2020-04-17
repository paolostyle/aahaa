$cwd = Get-Location
$volumePath = Join-Path -Path $cwd -ChildPath "screens"

poetry export -f requirements.txt -o requirements.txt
docker rm afkapi -fv
docker build -t afk-arena-api .
docker run -d --name afkapi -v ${volumePath}:/app/screens -p 8080:8080 afk-arena-api
Remove-Item -Path "./requirements.txt"
