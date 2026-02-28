# 软件著作权合作协议批量生成器 - PowerShell版本
# 使用 Word COM 保持模板格式

param(
    [string]$InputDir = "C:\Temp\contracts\input",
    [string]$OutputDir = "C:\Temp\contracts\output",
    [string]$TemplateDir = "C:\Temp\contracts\templates"
)

$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

Write-Host "=" * 60
Write-Host "  软件著作权合作协议批量生成器"
Write-Host "=" * 60

# 天干
$TianGan = @('甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸')

function Get-PartyTitle([int]$index) {
    if ($index -lt 10) {
        return "$($TianGan[$index])方"
    } else {
        return "第$($index + 1)方"
    }
}

function Parse-Date([string]$dateStr) {
    $dateStr = $dateStr.Trim()
    # 尝试解析中文日期
    if ($dateStr -match '(\d{4})年(\d{1,2})月(\d{1,2})日') {
        return [DateTime]::new([int]$Matches[1], [int]$Matches[2], [int]$Matches[3])
    }
    # 尝试其他格式
    try {
        return [DateTime]::Parse($dateStr)
    } catch {
        return [DateTime]::Now
    }
}

function Extract-ApplicationInfo([string]$docxPath, $wordApp) {
    $doc = $wordApp.Documents.Open($docxPath)
    
    $info = @{
        SoftwareName = ''
        Version = 'V1.0'
        CompletionDate = ''
        Owners = @()
    }
    
    # 遍历所有表格
    foreach ($table in $doc.Tables) {
        for ($i = 1; $i -le $table.Rows.Count; $i++) {
            $row = $table.Rows.Item($i)
            $rowText = ''
            for ($j = 1; $j -le $row.Cells.Count; $j++) {
                $rowText += $row.Cells.Item($j).Range.Text + ' '
            }
            
            # 检查是否是软著名称行
            if ($rowText -match '软著名称') {
                # 下一行是数据
                if ($i + 1 -le $table.Rows.Count) {
                    $dataRow = $table.Rows.Item($i + 1)
                    $info.SoftwareName = $dataRow.Cells.Item(1).Range.Text.Trim()
                    if ($dataRow.Cells.Count -ge 3) {
                        $info.Version = $dataRow.Cells.Item(3).Range.Text.Trim()
                        if (-not $info.Version) { $info.Version = 'V1.0' }
                    }
                    if ($dataRow.Cells.Count -ge 4) {
                        $info.CompletionDate = $dataRow.Cells.Item(4).Range.Text.Trim()
                    }
                }
            }
            
            # 检查是否是著作权人信息
            if ($rowText -match '著作权人信息') {
                # 找列标题行
                $headerIdx = -1
                for ($j = $i + 1; $j -le [Math]::Min($i + 3, $table.Rows.Count); $j++) {
                    $checkRow = $table.Rows.Item($j)
                    $checkText = ''
                    for ($k = 1; $k -le $checkRow.Cells.Count; $k++) {
                        $checkText += $checkRow.Cells.Item($k).Range.Text
                    }
                    if ($checkText -match '公司/单位/个人名称') {
                        $headerIdx = $j
                        break
                    }
                }
                
                if ($headerIdx -gt 0) {
                    for ($j = $headerIdx + 1; $j -le $table.Rows.Count; $j++) {
                        $dataRow = $table.Rows.Item($j)
                        $cellText = $dataRow.Cells.Item(1).Range.Text
                        
                        # 检查是否到联系人信息
                        if ($cellText -match '联系人信息' -or $cellText -match '^\s*$') {
                            break
                        }
                        
                        # 跳过标题行
                        if ($cellText -match '公司' -and $cellText -match '营业执照') {
                            continue
                        }
                        
                        $owner = @{
                            Name = $dataRow.Cells.Item(1).Range.Text.Trim()
                        }
                        if ($dataRow.Cells.Count -ge 2) {
                            $owner.IdNumber = $dataRow.Cells.Item(2).Range.Text.Trim()
                        }
                        if ($dataRow.Cells.Count -ge 3) {
                            $owner.Location = $dataRow.Cells.Item(3).Range.Text.Trim()
                        }
                        
                        if ($owner.Name) {
                            $info.Owners += $owner
                        }
                    }
                }
            }
        }
    }
    
    $doc.Close($false)
    return $info
}

function Generate-Contract([hashtable]$info, [string]$templatePath, [string]$outputPath, $wordApp) {
    # 计算协议日期（开发完成时间 - 3个月）
    $completionDate = Parse-Date $info.CompletionDate
    $contractDate = $completionDate.AddMonths(-3)
    $contractDateStr = "$($contractDate.Year)年$($contractDate.Month)月$($contractDate.Day)日"
    
    # 软件全名
    $softwareFullName = "$($info.SoftwareName)$($info.Version)"
    
    # 协议份数
    $copyCount = $info.Owners.Count + 1
    
    # 打开模板
    $doc = $wordApp.Documents.Open($templatePath)
    
    # 生成当事人文本
    $partiesText = ""
    $signaturesText = ""
    for ($i = 0; $i -lt $info.Owners.Count; $i++) {
        $partyTitle = Get-PartyTitle $i
        $partiesText += "$partyTitle：`r`n$($info.Owners[$i].Name)`r`n`r`n"
        $signaturesText += "$partyTitle：`r`n`r`n"
    }
    
    # 替换内容
    $findReplace = $wordApp.Selection.Find
    
    # 替换软件名称和版本
    $findReplace.Execute('智能心理压力情绪疏导与调解平台V1.0', $false, $false, $false, $false, $false, $true, 1, $false, $softwareFullName, 2)
    
    # 替换份数
    $findReplace.Execute('三份', $false, $false, $false, $false, $false, $true, 1, $false, "$copyCount份", 2)
    
    # 替换日期
    $findReplace.Execute('2025-3-10', $false, $false, $false, $false, $false, $true, 1, $false, $contractDateStr, 2)
    
    # 替换当事人（需要更复杂的处理）
    # 先替换甲方
    if ($info.Owners.Count -ge 1) {
        $findReplace.Execute('王红梅', $false, $false, $false, $false, $false, $true, 1, $false, $info.Owners[0].Name, 2)
    }
    # 替换乙方
    if ($info.Owners.Count -ge 2) {
        $findReplace.Execute('汪庆军', $false, $false, $false, $false, $false, $true, 1, $false, $info.Owners[1].Name, 2)
    }
    
    # 保存
    $doc.SaveAs($outputPath)
    $doc.Close($false)
}

# 主程序
Write-Host "`n输入目录: $InputDir"
Write-Host "输出目录: $OutputDir"
Write-Host "模板目录: $TemplateDir"
Write-Host ""

# 创建输出目录
New-Item -ItemType Directory -Force -Path $OutputDir | Out-Null

# 启动 Word
$word = New-Object -ComObject Word.Application
$word.Visible = $false

try {
    # 获取所有申请表文件
    $files = Get-ChildItem -Path $InputDir -Filter "*.docx"
    
    $successCount = 0
    $failCount = 0
    
    foreach ($file in $files) {
        Write-Host "处理: $($file.Name)"
        
        try {
            # 提取信息
            $info = Extract-ApplicationInfo $file.FullName $word
            
            if (-not $info.SoftwareName) {
                Write-Host "  [FAIL] 无法提取软件名称"
                $failCount++
                continue
            }
            
            if ($info.Owners.Count -eq 0) {
                Write-Host "  [FAIL] 无法提取著作权人信息"
                $failCount++
                continue
            }
            
            Write-Host "  软件名: $($info.SoftwareName)"
            Write-Host "  著作权人: $($info.Owners.Count)人"
            
            # 选择模板（根据著作权人数量）
            $templateFile = Join-Path $TemplateDir "合作协议-$($info.Owners.Count)方.doc"
            
            if (-not (Test-Path $templateFile)) {
                Write-Host "  [FAIL] 找不到模板: $templateFile"
                $failCount++
                continue
            }
            
            # 生成输出文件名
            $safeName = $info.SoftwareName -replace '[\\/:*?"<>|]', '-'
            $outputFile = Join-Path $OutputDir "合作协议-$safeName.doc"
            
            # 生成协议
            Generate-Contract $info $templateFile $outputFile $word
            
            Write-Host "  [OK] 生成: 合作协议-$safeName.doc"
            $successCount++
            
        } catch {
            Write-Host "  [FAIL] 错误: $_"
            $failCount++
        }
    }
    
    Write-Host "`n处理完成: $successCount 成功, $failCount 失败"
    
} finally {
    $word.Quit()
}
