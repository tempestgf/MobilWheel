param(
    [string]$newVersion = "2.0.0" # Prueba
)

$readmeFiles = @("README.md", "README.es.md", "README.ca.md")

foreach ($file in $readmeFiles) {
    if (Test-Path $file) {
        Write-Host "Revisando $file para actualizar a versión $newVersion..."
        
        # Leer el contenido preservando la codificación exacta como UTF-8 crudo (sin BOM añadido por PowerShell)
        $utf8NoBom = New-Object System.Text.UTF8Encoding($False)
        $content = [System.IO.File]::ReadAllText($file, $utf8NoBom)
        
        # Regex para buscar cualquier rastro de versión anterior x.x.x
        $newContent = [regex]::Replace($content, '\d+\.\d+\.\d+', $newVersion)
        
        # Escribir el contenido preservando exactamente el UTF-8 sin BOM
        if ($content -ne $newContent) {
            [System.IO.File]::WriteAllText($file, $newContent, $utf8NoBom)
            Write-Host "✅ Se ha actualizado $file a la versión $newVersion" -ForegroundColor Green
        } else {
            Write-Host "No se encontraron cambios necesarios de versión en $file" -ForegroundColor Yellow
        }
    } else {
        Write-Host "No se encontró el archivo $file" -ForegroundColor Red
    }
}
Write-Host "Prueba finalizada. No se realizarán commits." -ForegroundColor Cyan
