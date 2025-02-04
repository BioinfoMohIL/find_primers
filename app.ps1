Add-Type -AssemblyName System.Windows.Forms

# Function to get complement sequence
function Get-Complement {
    param ($sequence)
    
    # Flip the sequence
    $charArray = $sequence.ToCharArray()
    [Array]::Reverse($charArray)
    $flippedSequence = -join $charArray

    return ($flippedSequence -replace 'A', 'X' -replace 'T', 'A' -replace 'X', 'T' -replace 'C', 'Y' -replace 'G', 'C' -replace 'Y', 'G')
}

# Create form
$form = New-Object System.Windows.Forms.Form
$form.Text = "DNA Complement Tool"
$form.Size = New-Object System.Drawing.Size(600, 350)
$form.StartPosition = "CenterScreen"

# File Upload Label & Button
$lblFile = New-Object System.Windows.Forms.Label
$lblFile.Text = "Upload File:"
$lblFile.Location = New-Object System.Drawing.Point(20, 20)
$form.Controls.Add($lblFile)

$filePath = New-Object System.Windows.Forms.TextBox
$filePath.Location = New-Object System.Drawing.Point(120, 30)
$filePath.Size = New-Object System.Drawing.Size(320, 30)
$filePath.Padding = New-Object System.Windows.Forms.Padding(5)
$filePath.ReadOnly = $true
$form.Controls.Add($filePath)

$btnUpload = New-Object System.Windows.Forms.Button
$btnUpload.Text = "Browse"
$btnUpload.Location = New-Object System.Drawing.Point(460, 18)
$btnUpload.Add_Click({
    $openFileDialog = New-Object System.Windows.Forms.OpenFileDialog
    if ($openFileDialog.ShowDialog() -eq "OK") {
        $filePath.Text = $openFileDialog.FileName
        Update-LaunchButton
    }
})
$form.Controls.Add($btnUpload)

$defaultFolder = "$PWD" 
# if (Test-Path $defaultFolder) {
#     $defaultFile = Get-ChildItem -Path $defaultFolder -Filter "*.fasta" | Select-Object -First 1
#     if ($defaultFile) {
#         $filePath.Text = $defaultFile.FullName
#     }
# }

# Primer 1
$lblPrimer1 = New-Object System.Windows.Forms.Label
$lblPrimer1.Text = "Primer 1:"
$lblPrimer1.Location = New-Object System.Drawing.Point(20, 70)
$form.Controls.Add($lblPrimer1)

$txtPrimer1 = New-Object System.Windows.Forms.TextBox
$txtPrimer1.Location = New-Object System.Drawing.Point(130, 70)
$txtPrimer1.Size = New-Object System.Drawing.Size(320, 30)
$txtPrimer1.Padding = New-Object System.Windows.Forms.Padding(5)
$txtPrimer1.BackColor = [System.Drawing.Color]::Orange
$txtPrimer1.Add_TextChanged({ Update-LaunchButton })
$form.Controls.Add($txtPrimer1)

$btnComplement1 = New-Object System.Windows.Forms.Button
$btnComplement1.Text = "Swap"
$btnComplement1.Location = New-Object System.Drawing.Point(460, 70)
$btnComplement1.Add_Click({ $txtPrimer1.Text = Get-Complement $txtPrimer1.Text })
$form.Controls.Add($btnComplement1)

# Primer 2
$lblPrimer2 = New-Object System.Windows.Forms.Label
$lblPrimer2.Text = "Primer 2:"
$lblPrimer2.Location = New-Object System.Drawing.Point(20, 120)
$form.Controls.Add($lblPrimer2)

$txtPrimer2 = New-Object System.Windows.Forms.TextBox
$txtPrimer2.Location = New-Object System.Drawing.Point(130, 120)
$txtPrimer2.Size = New-Object System.Drawing.Size(320, 30)
$txtPrimer2.Padding = New-Object System.Windows.Forms.Padding(5)
$txtPrimer2.BackColor = [System.Drawing.Color]::Red
$txtPrimer2.Add_TextChanged({ Update-LaunchButton })
$form.Controls.Add($txtPrimer2)

$btnComplement2 = New-Object System.Windows.Forms.Button
$btnComplement2.Text = "Swap"
$btnComplement2.Location = New-Object System.Drawing.Point(460, 120)
$btnComplement2.Add_Click({ $txtPrimer2.Text = Get-Complement $txtPrimer2.Text })
$form.Controls.Add($btnComplement2)

# Probe
$lblProbe = New-Object System.Windows.Forms.Label
$lblProbe.Text = "Probe:"
$lblProbe.Location = New-Object System.Drawing.Point(20, 170)
$form.Controls.Add($lblProbe)

$txtProbe = New-Object System.Windows.Forms.TextBox
$txtProbe.Location = New-Object System.Drawing.Point(130, 170)
$txtProbe.Size = New-Object System.Drawing.Size(320, 30)
$txtProbe.Padding = New-Object System.Windows.Forms.Padding(5)
$txtProbe.BackColor = [System.Drawing.Color]::Pink
$txtProbe.Add_TextChanged({ Update-LaunchButton })
$form.Controls.Add($txtProbe)

$btnProbe = New-Object System.Windows.Forms.Button
$btnProbe.Text = "Swap"
$btnProbe.Location = New-Object System.Drawing.Point(460, 170)
$btnProbe.Add_Click({ $txtProbe.Text = Get-Complement $txtProbe.Text })
$form.Controls.Add($btnProbe)

# Launch Button
$btnLaunch = New-Object System.Windows.Forms.Button
$btnLaunch.Text = "Launch"
$btnLaunch.Location = New-Object System.Drawing.Point(220, 230)
$btnLaunch.Size = New-Object System.Drawing.Size(150, 40)
$btnLaunch.Enabled = $false
$btnLaunch.Add_Click({
    $pythonScript = "dev\run.py"
    $arguments = "`"$($filePath.Text)`" `"$($txtPrimer1.Text)`" `"$($txtPrimer2.Text)`" `"$($txtProbe.Text)`" `"$($PWD)`"" 
    Start-Process -FilePath "python3" -ArgumentList "$pythonScript $arguments" -NoNewWindow
})
$form.Controls.Add($btnLaunch)

function Update-LaunchButton {
    if ($filePath.Text -and $txtPrimer1.Text -and $txtPrimer2.Text -and $txtProbe.Text) {
        $btnLaunch.Enabled = $true
    } else {
        $btnLaunch.Enabled = $false
    }
}

# Show Form
$form.ShowDialog()
