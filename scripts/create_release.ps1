# Script de actualizacion y firma
param (
    [Parameter(Mandatory=$true)][string]$version,
    [Parameter(Mandatory=$true)][string]$notes,
    [string]$KeystorePass = "WFSset400"
)

# Resolvemos Root folder basado en la ubicacion de este script
$ScriptPath = [System.IO.Path]::GetFullPath($MyInvocation.MyCommand.Path)
$ScriptDir  = [System.IO.Path]::GetDirectoryName($ScriptPath)
$RootDir    = [System.IO.Path]::GetDirectoryName($ScriptDir)

Set-Location $RootDir

Write-Host "Iniciando release $version desde $RootDir"

$AndroidApkPath = "$RootDir\android-client\app\build\outputs\apk\release\app-release.apk"
$ServerExePath  = "$RootDir\python-server\dist\MobileWheelServer.exe"
$KeyStorePath   = "$RootDir\playstorekeyTempestgf.jks"

Write-Host "1. Actualizando version en el codigo..."
# Parsear version (ej: "1.0.4" -> 10004) para versionCode de Android
$versionParts = $version.Split('.')
$VersionCode = 1
if ($versionParts.Length -ge 3) {
    $patchPart = $versionParts[2] -replace '\D.*',''
    $VersionCode = ([int]$versionParts[0] * 10000) + ([int]$versionParts[1] * 100) + ([int]$patchPart)
}

# Android build.gradle.kts
$gradleFile = "$RootDir\android-client\app\build.gradle.kts"
$gradleContent = Get-Content $gradleFile -Raw
$gradleContent = $gradleContent -replace 'versionName\s*=\s*".*"', "versionName = `"$version`""
$gradleContent = [regex]::Replace($gradleContent, '(?<=versionCode\s*=\s*)\d+', "$VersionCode")
Set-Content -Path $gradleFile -Value $gradleContent -Encoding UTF8

# Python app_version.py
$pyVersionFile = "$RootDir\python-server\app_version.py"
$pyContent = Get-Content $pyVersionFile -Raw
$pyContent = $pyContent -replace 'APP_VERSION\s*=\s*".*"', "APP_VERSION = `"$version`""
Set-Content -Path $pyVersionFile -Value $pyContent -Encoding UTF8

# READMEs
Write-Host "Actualizando README.md, README.es.md y README.ca.md..."
Get-ChildItem -Filter "README*.md" | ForEach-Object {
    Write-Host "  - Actualizando $_"
    $c = Get-Content $_ -Raw
    $c = [regex]::Replace($c, '1\.\d+\.\d+', $version)
    Set-Content -Path $_ -Value $c -Encoding UTF8
}
Write-Host "READMEs actualizados correctamente."

Write-Host "2. Compilando Android App..."
cd android-client
.\gradlew assembleRelease --no-daemon
cd $RootDir

Write-Host "3. Compilando Server App..."
cd python-server
python -m PyInstaller ServerApp_onefile.spec
cd $RootDir

Write-Host "4. Firmando APK..."
& $env:LOCALAPPDATA\Android\Sdk\build-tools\36.1.0\apksigner.bat sign --ks $KeyStorePath --ks-key-alias key0 --ks-pass "pass:$KeystorePass" $AndroidApkPath

Write-Host "5. Publicando Update a MobileWheelWebsite (Android)..."
python "$RootDir\scripts\android\publish_update_android.py" --apk $AndroidApkPath --version $version --notes $notes --set-app-version

Write-Host "6. Publicando Update a MobileWheelWebsite (Server)..."
python "$RootDir\python-server\build_tools\publish_update.py" --installer $ServerExePath --version $version --notes $notes --set-app-version

Write-Host "7. Git Commit de cambios..."
Write-Host "  - Añadiendo cambios de versión y README a staging..."
git add python-server/app_version.py android-client/app/build.gradle.kts README.md README.es.md README.ca.md
git commit -m "Release v${version}: $notes"
Write-Host "  - Pusheando a developing..."
git push origin developing
Write-Host "  - Creando tag v${version}..."
git tag "v$version"
git push origin "v$version"
Write-Host "Cambios commiteados y pusheados exitosamente."

Write-Host "8. Lanzar gh release..."
Write-Host "Realizando subida a GitHub Releases..."
gh release create "v$version" -t "v$version" -n $notes "$AndroidApkPath#MobileWheelClient-$version.apk" "$ServerExePath#MobileWheelServer-$version.exe"

Write-Host "9. Subiendo cambios de MobileWheelWebsite..."
$WebsiteDir = "C:\Users\Tempestgf\Coding\Web\mobilwheelwebsite"
if (Test-Path $WebsiteDir) {
    cd $WebsiteDir
    git add public/update/
    git commit -m "Update OTA release manifests and payloads for v$version"
    git push origin main
    cd $RootDir
} else {
    Write-Host "No se encontro el directorio de MobileWheelWebsite: $WebsiteDir"
}

Write-Host "DONE!"

