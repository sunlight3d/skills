param (
    [Parameter(Mandatory=$true)]
    [string]$TargetDir
)

$ErrorActionPreference = "Continue"

if (-Not (Test-Path -Path $TargetDir)) {
    Write-Error "Thư mục không tồn tại: $TargetDir"
    exit 1
}

$subDirs = Get-ChildItem -Path $TargetDir -Directory
foreach ($Ti in $subDirs) {
    $TiContents = Get-ChildItem -Path $Ti.FullName -Force
    # Nếu thư mục con chỉ chứa đúng 1 phần tử và phần tử đó là thư mục
    if ($TiContents.Count -eq 1 -and $TiContents[0].PSIsContainer) {
        $X = $TiContents[0]
        Write-Host "Đang chuyển dữ liệu từ $($X.Name) ra ngoài $($Ti.Name)..."
        
        # Di chuyển toàn bộ file và thư mục ẩn/hiện từ X ra Ti
        Get-ChildItem -Path $X.FullName -Force | Move-Item -Destination $Ti.FullName -Force
        
        # Xóa thư mục X (bỏ qua lỗi nếu còn file bị khóa)
        Remove-Item -Path $X.FullName -Force -Recurse -ErrorAction SilentlyContinue
    }
}

Write-Host "Hoàn tất quá trình làm phẳng thư mục."
