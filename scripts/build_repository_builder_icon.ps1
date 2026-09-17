[CmdletBinding()]
param()

# Render the simple vector mark with Windows' drawing library; no Python imaging dependency.
$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Drawing
$assets = Join-Path (Split-Path -Parent $PSScriptRoot) 'repository_builder\assets'
[xml]$svg = Get-Content -LiteralPath (Join-Path $assets 'repository-builder.svg') -Raw
$bitmap = New-Object System.Drawing.Bitmap(1024, 1024)
$graphics = [System.Drawing.Graphics]::FromImage($bitmap)
$graphics.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::AntiAlias
$graphics.ScaleTransform(2, 2)
try {
    $rect = $svg.svg.rect
    $x = [float]$rect.x; $y = [float]$rect.y
    $width = [float]$rect.width; $height = [float]$rect.height; $diameter = 2 * [float]$rect.rx
    $shape = New-Object System.Drawing.Drawing2D.GraphicsPath
    $shape.AddArc($x, $y, $diameter, $diameter, 180, 90)
    $shape.AddArc(($x + $width - $diameter), $y, $diameter, $diameter, 270, 90)
    $shape.AddArc(($x + $width - $diameter), ($y + $height - $diameter), $diameter, $diameter, 0, 90)
    $shape.AddArc($x, ($y + $height - $diameter), $diameter, $diameter, 90, 90)
    $shape.CloseFigure()
    $stops = $svg.svg.defs.linearGradient.stop
    $gradient = New-Object System.Drawing.Drawing2D.LinearGradientBrush(
        ([System.Drawing.RectangleF]::new($x, $y, $width, $height)),
        ([System.Drawing.ColorTranslator]::FromHtml($stops[0].'stop-color')),
        ([System.Drawing.ColorTranslator]::FromHtml($stops[1].'stop-color')),
        ([System.Drawing.Drawing2D.LinearGradientMode]::Vertical))
    $graphics.FillPath($gradient, $shape)
    $gradient.Dispose(); $shape.Dispose()
    foreach ($line in $svg.svg.polyline) {
        [System.Drawing.PointF[]]$points = @($line.points.Split(' ') | ForEach-Object {
            $coords = $_.Split(','); [System.Drawing.PointF]::new([float]$coords[0], [float]$coords[1])
        })
        $pen = [System.Drawing.Pen]::new([System.Drawing.ColorTranslator]::FromHtml($line.stroke), [float]$line.'stroke-width')
        $pen.StartCap = $pen.EndCap = [System.Drawing.Drawing2D.LineCap]::Round
        $pen.LineJoin = [System.Drawing.Drawing2D.LineJoin]::Round
        $graphics.DrawLines($pen, $points)
        $pen.Dispose()
    }
    $polygon = $svg.svg.polygon
    [System.Drawing.PointF[]]$points = @($polygon.points.Split(' ') | ForEach-Object {
        $coords = $_.Split(','); [System.Drawing.PointF]::new([float]$coords[0], [float]$coords[1])
    })
    $brush = [System.Drawing.SolidBrush]::new([System.Drawing.ColorTranslator]::FromHtml($polygon.fill))
    $graphics.FillPolygon($brush, $points)
    $brush.Dispose()
    $sizes = @(16, 20, 24, 32, 40, 48, 64, 128, 256, 512)
    $frames = @()
    foreach ($size in $sizes) {
        $small = New-Object System.Drawing.Bitmap($size, $size)
        $scaled = [System.Drawing.Graphics]::FromImage($small)
        $scaled.InterpolationMode = [System.Drawing.Drawing2D.InterpolationMode]::HighQualityBicubic
        $scaled.PixelOffsetMode = [System.Drawing.Drawing2D.PixelOffsetMode]::HighQuality
        $scaled.DrawImage($bitmap, 0, 0, $size, $size)
        $stream = New-Object System.IO.MemoryStream
        $small.Save($stream, [System.Drawing.Imaging.ImageFormat]::Png)
        if ($size -eq 512) {
            [System.IO.File]::WriteAllBytes((Join-Path $assets 'repository-builder.png'), $stream.ToArray())
        } else {
            $frames += [pscustomobject]@{ Size = $size; Bytes = $stream.ToArray() }
        }
        $stream.Dispose(); $scaled.Dispose(); $small.Dispose()
    }
    $output = [System.IO.File]::Create((Join-Path $assets 'repository-builder.ico'))
    $writer = [System.IO.BinaryWriter]::new($output)
    try {
        $writer.Write([uint16]0); $writer.Write([uint16]1); $writer.Write([uint16]$frames.Count)
        $offset = 6 + 16 * $frames.Count
        foreach ($frame in $frames) {
            $dimension = if ($frame.Size -eq 256) { 0 } else { $frame.Size }
            $writer.Write([byte]$dimension); $writer.Write([byte]$dimension)
            $writer.Write([byte]0); $writer.Write([byte]0)
            $writer.Write([uint16]1); $writer.Write([uint16]32)
            $writer.Write([uint32]$frame.Bytes.Length); $writer.Write([uint32]$offset)
            $offset += $frame.Bytes.Length
        }
        foreach ($frame in $frames) { $writer.Write([byte[]]$frame.Bytes) }
    } finally { $writer.Dispose(); $output.Dispose() }
} finally { $graphics.Dispose(); $bitmap.Dispose() }
Write-Output "Created PNG and multi-resolution ICO in $assets"
