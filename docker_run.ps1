param (
    [String] $Alerter = "email",
    [String] $Config = "",
    [String] $ChatId = "",
    [String] $Email = "",
    [String] $Image = "ericjmarti/inventory-hunter:latest",
    [String] $Relay = "",
    [String] $Webhook = ""
)

if (-Not $Config) { Throw "missing config argument" }
if (-Not (Test-Path $Config -PathType Leaf)) { Throw "$Config does not exist or is not a regular file" }

if ($Alerter -eq "email") {
    if (-Not $email) { throw "missing email argument" }
    if (-Not $relay) { throw "missing relay argument" }
} else {
    if (-Not $webhook) { throw "missing webhook argument" }
    if ($Alerter -eq "telegram") {
        if (-Not $chatid) { throw "missing telegram chat id argument" }
    }
}

if ($Image -eq "ericjmarti/inventory-hunter:latest") {
    docker pull $Image
} else {
    $Result = docker images -q $Image
    if ([String]::IsNullOrEmpty($Result)) {
        Write-Host "the $Image docker image does not exist... please build the image and try again"
        Write-Host "build command: docker build -t $Image ."
        Exit 1
    }
}

$Config = (Resolve-Path -Path $Config)

$ContainerName = [System.IO.Path]::GetFileNameWithoutExtension($Config)

$DockerRunCmd = "docker run -d --rm --name $ContainerName --network host -v ${Config}:/config.yaml $Image --alerter $Alerter"

if ($Alerter -eq "email") {
    $DockerRunCmd = "$DockerRunCmd --email $Email --relay $Relay"
} else {
    $DockerRunCmd = "$DockerRunCmd --webhook $Webhook"
    if ($Alerter -eq "telegram") {
        $DockerRunCmd = "$DockerRunCmd --chat-id $ChatId"
    }
}

$DockerPsCmd = "docker ps -a -f name=$ContainerName"

# Write-Host "$ $DockerRunCmd"
Invoke-Expression $DockerRunCmd
Write-Host
Write-Host "started docker container named $ContainerName"
Write-Host
Write-Host "view the status of this container using the following command:"
Write-Host "$ $DockerPsCmd"
Write-Host
Invoke-Expression $DockerPsCmd
Write-Host
Write-Host "view logs for this container using the following command:"
Write-Host "$ docker logs -f $ContainerName"
Write-Host
