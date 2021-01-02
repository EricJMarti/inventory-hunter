param (
    [String] $Alerter = "email",
    [String] $AlerterConfig = "",
    [String] $Config = "",
    [String] $ChatId = "",
    [String] $Email = "",
    [String] $Image = "ericjmarti/inventory-hunter:latest",
    [String] $Relay = "",
    [String] $UserKey = "",
    [String] $AccessToken = "",
    [String] $Webhook = ""
)

if (-Not $Config) { Throw "missing config argument" }
if (-Not (Test-Path $Config -PathType Leaf)) { Throw "$Config does not exist or is not a regular file" }

if ($AlerterConfig) {
    if (-Not (Test-Path $AlerterConfig -PathType Leaf)) { Throw "$AlerterConfig does not exist or is not a regular file" }
} elseif ($Alerter -eq "email") {
    if (-Not $email) { Throw "missing email argument" }
    if (-Not $relay) { Throw "missing relay argument" }
} elseif ($Alerter -eq "pushover") {
    if (-Not $userKey) { Throw "missing user key argument" }
    if (-Not $accessToken) { Throw "missing access token argument" }
} else {
    if (-Not $webhook) { Throw "missing webhook argument" }
    if ($Alerter -eq "telegram") {
        if (-Not $chatid) { Throw "missing telegram chat id argument" }
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
if ($AlerterConfig) { $AlerterConfig = (Resolve-Path -Path $AlerterConfig) }

$ScriptDir = Split-Path $MyInvocation.MyCommand.Path
$LogDir = "${ScriptDir}\log"
New-Item $LogDir -ItemType Directory -ea 0 | Out-Null

$ContainerName = [System.IO.Path]::GetFileNameWithoutExtension($Config)
$DataDir = "${ScriptDir}\data\${ContainerName}"
$LogFile = "${LogDir}\${ContainerName}.txt"
New-Item $DataDir -ItemType Directory -ea 0 | Out-Null
New-Item $LogFile -ItemType File -ea 0 | Out-Null

$Volumes = "-v ${DataDir}:/data -v ${LogFile}:/log.txt -v ${Config}:/config.yaml"
if ($AlerterConfig) { $Volumes = "$Volumes -v ${AlerterConfig}:/alerters.yaml" }

$DockerRunCmd = "docker run -d --rm --name $ContainerName --network host $Volumes $Image --alerter $Alerter"

if ($AlerterConfig) {
    $DockerRunCmd = "$DockerRunCmd --alerter-config /alerters.yaml"
} elseif ($Alerter -eq "email") {
    $DockerRunCmd = "$DockerRunCmd --email $Email --relay $Relay"
} elseif ($Alerter -eq "pushover") {
    $DockerRunCmd = "$DockerRunCmd --user-key $UserKey --access-token $AccessToken"
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
