# -*- coding: utf-8 -*-
"""
合作协议批量生成器 v3 - 使用 PowerShell 调用 Word COM
"""

import os
import glob
import subprocess


def batch_generate(input_dir, output_dir, template_dir):
    """批量生成合作协议"""
    
    # PowerShell 脚本
    ps_script = f'''
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$inputDir = "{input_dir}"
$outputDir = "{output_dir}"
$templateDir = "{template_dir}"

Write-Host "=" * 50
Write-Host "  软件著作权合作协议批量生成器"
Write-Host "=" * 50

# 确保目录存在
New-Item -ItemType Directory -Force -Path $outputDir | Out-Null

# 获取申请表文件
$files = Get-ChildItem -Path $inputDir -Filter "*.docx"
Write-Host "`n找到 $($files.Count) 个申请表文件"

# 天干
$tianGan = @('甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸')

function Get-PartyTitle([int]$index) {{
    if ($index -lt 10) {{ return "$($tianGan[$index])方" }}
    else {{ return "第$($index + 1)方" }}
}}

function Parse-Date([string]$dateStr) {{
    if ($dateStr -match '(\\d{{4}})年(\\d{{1,2}})月(\\d{{1,2}})日') {{
        $y = [int]$Matches[1]
        $m = [int]$Matches[2]
        $d = [int]$Matches[3]
        $m = $m - 3
        if ($m -le 0) {{ $m += 12; $y -= 1 }}
        return "$y年$m月$d日"
    }}
    return "2025年1月1日"
}}

# 启动 Word
$word = New-Object -ComObject Word.Application
$word.Visible = $false

$successCount = 0
$failCount = 0

foreach ($file in $files) {{
    Write-Host "`n处理: $($file.Name)"
    
    try {{
        # 打开申请表
        $appDoc = $word.Documents.Open($file.FullName)
        
        # 提取信息
        $softwareName = ""
        $version = "V1.0"
        $completionDate = ""
        $owners = @()
        
        foreach ($table in $appDoc.Tables) {{
            for ($i = 1; $i -le $table.Rows.Count; $i++) {{
                $row = $table.Rows.Item($i)
                $rowText = ""
                for ($j = 1; $j -le $row.Cells.Count; $j++) {{
                    $rowText += $row.Cells.Item($j).Range.Text + " "
                }}
                
                # 软著名称
                if ($rowText -match '软著名称' -and $i + 1 -le $table.Rows.Count) {{
                    $dataRow = $table.Rows.Item($i + 1)
                    $softwareName = $dataRow.Cells.Item(1).Range.Text.Trim()
                    if ($dataRow.Cells.Count -ge 3) {{
                        $v = $dataRow.Cells.Item(3).Range.Text.Trim()
                        if ($v) {{ $version = $v }}
                    }}
                    if ($dataRow.Cells.Count -ge 4) {{
                        $completionDate = $dataRow.Cells.Item(4).Range.Text.Trim()
                    }}
                }}
                
                # 著作权人
                if ($rowText -match '著作权人信息') {{
                    for ($j = $i + 1; $j -le $table.Rows.Count; $j++) {{
                        $checkRow = $table.Rows.Item($j)
                        $checkText = $checkRow.Cells.Item(1).Range.Text
                        if ($checkText -match '联系人' -or $checkText -match '^\\s*$') {{ break }}
                        if ($checkText -match '公司/单位' -or $checkText -match '营业执照') {{ continue }}
                        
                        $ownerName = $checkRow.Cells.Item(1).Range.Text.Trim()
                        if ($ownerName) {{
                            $owners += $ownerName
                        }}
                    }}
                }}
            }}
        }}
        
        $appDoc.Close($false)
        
        if (-not $softwareName) {{
            Write-Host "  [FAIL] 无法提取软件名称"
            $failCount++
            continue
        }}
        
        if ($owners.Count -eq 0) {{
            Write-Host "  [FAIL] 无法提取著作权人"
            $failCount++
            continue
        }}
        
        Write-Host "  软件: $softwareName"
        Write-Host "  著作权人: $($owners.Count)人"
        
        # 选择模板
        $templateFile = Join-Path $templateDir "合作协议-$($owners.Count)方.doc"
        if (-not (Test-Path $templateFile)) {{
            Write-Host "  [FAIL] 模板不存在: $($owners.Count)方"
            $failCount++
            continue
        }}
        
        # 计算日期
        $contractDate = Parse-Date $completionDate
        
        # 软件全名
        $softwareFullName = "$softwareName$version"
        
        # 协议份数
        $copyCount = $owners.Count + 1
        
        # 打开模板
        $doc = $word.Documents.Open($templateFile)
        
        # 替换软件名称（模板中的示例名称）
        $find = $word.Selection.Find
        $find.Execute('智能心理压力情绪疏导与调解平台V1.0', $false, $false, $false, $false, $false, $true, 1, $false, $softwareFullName, 2)
        
        # 替换日期
        $find.Execute('2025-3-10', $false, $false, $false, $false, $false, $true, 1, $false, $contractDate, 2)
        
        # 替换当事人（模板中的示例名字）
        if ($owners.Count -ge 1) {{
            $find.Execute('王红梅', $false, $false, $false, $false, $false, $true, 1, $false, $owners[0], 2)
        }}
        if ($owners.Count -ge 2) {{
            $find.Execute('汪庆军', $false, $false, $false, $false, $false, $true, 1, $false, $owners[1], 2)
        }}
        if ($owners.Count -ge 3) {{
            $find.Execute('吴六韬', $false, $false, $false, $false, $false, $true, 1, $false, $owners[2], 2)
        }}
        if ($owners.Count -ge 4) {{
            $find.Execute('赖羽羽', $false, $false, $false, $false, $false, $true, 1, $false, $owners[3], 2)
        }}
        if ($owners.Count -ge 5) {{
            $find.Execute('刘茜茜', $false, $false, $false, $false, $false, $true, 1, $false, $owners[4], 2)
        }}
        
        # 替换份数
        $find.Execute('三份', $false, $false, $false, $false, $false, $true, 1, $false, "$copyCount份", 2)
        $find.Execute('四份', $false, $false, $false, $false, $false, $true, 1, $false, "$copyCount份", 2)
        $find.Execute('五份', $false, $false, $false, $false, $false, $true, 1, $false, "$copyCount份", 2)
        $find.Execute('六份', $false, $false, $false, $false, $false, $true, 1, $false, "$copyCount份", 2)
        $find.Execute('七份', $false, $false, $false, $false, $false, $true, 1, $false, "$copyCount份", 2)
        $find.Execute('八份', $false, $false, $false, $false, $false, $true, 1, $false, "$copyCount份", 2)
        $find.Execute('九份', $false, $false, $false, $false, $false, $true, 1, $false, "$copyCount份", 2)
        $find.Execute('十份', $false, $false, $false, $false, $false, $true, 1, $false, "$copyCount份", 2)
        $find.Execute('十一份', $false, $false, $false, $false, $false, $true, 1, $false, "$copyCount份", 2)
        $find.Execute('十二份', $false, $false, $false, $false, $false, $true, 1, $false, "$copyCount份", 2)
        $find.Execute('十三份', $false, $false, $false, $false, $false, $true, 1, $false, "$copyCount份", 2)
        $find.Execute('十四份', $false, $false, $false, $false, $false, $true, 1, $false, "$copyCount份", 2)
        
        # 保存
        $safeName = $softwareName -replace '[\\\\/:*?"<>|]', '-'
        $outputPath = Join-Path $outputDir "合作协议-$safeName.doc"
        $doc.SaveAs($outputPath)
        $doc.Close($false)
        
        Write-Host "  [OK] 生成: 合作协议-$safeName.doc"
        $successCount++
        
    }} catch {{
        Write-Host "  [FAIL] 错误: $_"
        $failCount++
    }}
}}

$word.Quit()

Write-Host "`n处理完成! 成功: $successCount, 失败: $failCount"
'''
    
    # 保存脚本
    script_path = '/home/huang777/.openclaw/workspace/contract_generator/run.ps1'
    with open(script_path, 'w', encoding='utf-8') as f:
        f.write(ps_script)
    
    # 执行
    result = subprocess.run(
        ['powershell.exe', '-ExecutionPolicy', 'Bypass', '-File', script_path],
        capture_output=True,
        timeout=300,
        encoding='gbk',
        errors='replace'
    )
    
    print(result.stdout)
    if result.stderr:
        print("错误:", result.stderr)


if __name__ == '__main__':
    batch_generate(
        'C:/Temp/contracts/input',
        'C:/Temp/contracts/output', 
        'C:/Temp/contracts/中安-合作协议'
    )
