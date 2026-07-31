param (
    [Parameter(Mandatory=$true)]
    [string]$TargetDir
)

$ErrorActionPreference = "Continue"

if (-Not (Test-Path -Path $TargetDir)) {
    Write-Error "Thu muc khong ton tai: $TargetDir"
    exit 1
}

$subDirs = Get-ChildItem -Path $TargetDir -Directory
foreach ($Ti in $subDirs) {
    $flattened = $true
    while ($flattened) {
        $flattened = $false
        $TiContents = Get-ChildItem -Path $Ti.FullName -Force
        # Neu thu muc con chi chua dung 1 phan tu va phan tu do la thu muc
        if ($TiContents.Count -eq 1 -and $TiContents[0].PSIsContainer) {
            $X = $TiContents[0]
            Write-Host "Dang chuyen du lieu tu $($X.Name) ra ngoai $($Ti.Name)..."
            
            # Di chuyen toan bo file va thu muc an/hien tu X ra Ti
            Get-ChildItem -Path $X.FullName -Force | Move-Item -Destination $Ti.FullName -Force
            
            # Xoa thu muc X (bo qua loi neu con file bi khoa)
            Remove-Item -Path $X.FullName -Force -Recurse -ErrorAction SilentlyContinue
            
            $flattened = $true
        }
    }
}

Write-Host "Hoan tat qua trinh lam phang thu muc."
