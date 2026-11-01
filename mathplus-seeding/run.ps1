param (
    [int]$JoinCount = 3,
    [int]$PostCount = 2,
    [switch]$DryRun,
    [int]$DelayMin = 45,
    [int]$DelayMax = 75
)

$scriptPath = Join-Path $PSScriptRoot "scripts\seeder.py"
$params = @(
    "--join-count", $JoinCount,
    "--post-count", $PostCount,
    "--delay-min", $DelayMin,
    "--delay-max", $DelayMax
)

if ($DryRun) {
    $params += "--dry-run"
}

py -3.14 $scriptPath @params
