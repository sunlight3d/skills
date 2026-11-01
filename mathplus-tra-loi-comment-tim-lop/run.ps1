param (
    [switch]$Scan,
    [switch]$Confirm,
    [int]$JoinCount = 3,
    [int]$CommentCount = 3,
    [switch]$SkipJoin,
    [int]$DelayMin = 30,
    [int]$DelayMax = 50
)

$scriptPath = Join-Path $PSScriptRoot "scripts\commenter.py"
$params = @(
    "--join-count", $JoinCount,
    "--comment-count", $CommentCount,
    "--delay-min", $DelayMin,
    "--delay-max", $DelayMax
)

if ($Scan) {
    $params += "--scan"
}
if ($Confirm) {
    $params += "--confirm"
}
if ($SkipJoin) {
    $params += "--skip-join"
}

py -3.14 $scriptPath @params
