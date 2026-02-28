# -*- coding: utf-8 -*-
"""
合作协议批量生成器 - 最终版
"""

import os
import subprocess


def main():
    # WSL 路径（用于 Python 检查文件）
    input_dir_wsl = '/mnt/c/Temp/contracts/input'
    output_dir_wsl = '/mnt/c/Temp/contracts/output'
    template_dir_wsl = '/mnt/c/Temp/contracts/中安-合作协议'
    
    # Windows 路径（用于 PowerShell）
    input_dir_win = r'C:\Temp\contracts\input'
    output_dir_win = r'C:\Temp\contracts\output'
    template_dir_win = r'C:\Temp\contracts\中安-合作协议'
    
    print("=" * 50)
    print("  软件著作权合作协议批量生成器")
    print("=" * 50)
    
    # 检查输入目录
    if not os.path.exists(input_dir_wsl):
        os.makedirs(input_dir_wsl)
        print(f"\n已创建输入目录: {input_dir_win}")
        print("请将 .docx 申请表文件放入该目录后重新运行")
        return
    
    # 检查文件
    import glob
    files = glob.glob(os.path.join(input_dir_wsl, '*.docx'))
    print(f"\n找到 {len(files)} 个申请表文件")
    
    if not files:
        print(f"\n请将 .docx 申请表放入: {input_dir_win}")
        return
    
    # 确保输出目录存在
    os.makedirs(output_dir_wsl, exist_ok=True)
    
    # 生成 PowerShell 脚本
    ps_script = f'''
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$inputDir = "{input_dir_win}"
$outputDir = "{output_dir_win}"
$templateDir = "{template_dir_win}"

Write-Host ""
Write-Host "输入目录: $inputDir"
Write-Host "输出目录: $outputDir"  
Write-Host "模板目录: $templateDir"

$tianGan = @('甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸')

function Parse-Date([string]$dateStr) {{
    if ($dateStr -match '(\\d{{4}})年(\\d{{1,2}})月(\\d{{1,2}})日') {{
        $y = [int]$Matches[1]
        $m = [int]$Matches[2] - 3
        $d = [int]$Matches[3]
        if ($m -le 0) {{ $m += 12; $y -= 1 }}
        return "$y年$m月$d日"
    }}
    return "2025年1月1日"
}}

$word = New-Object -ComObject Word.Application
$word.Visible = $false

$files = Get-ChildItem -Path $inputDir -Filter "*.docx"
$successCount = 0
$failCount = 0

foreach ($file in $files) {{
    Write-Host ""
    Write-Host "处理: $($file.Name)"
    
    try {{
        $appDoc = $word.Documents.Open($file.FullName)
        $softwareName = ""
        $version = "V1.0"
        $completionDate = ""
        $owners = @()
        
        foreach ($table in $appDoc.Tables) {{
            for ($i = 1; $i -le $table.Rows.Count; $i++) {{
                $row = $table.Rows.Item($i)
                $rowText = ""
                for ($j = 1; $j -le $row.Cells.Count; $j++) {{
                    $rowText += $row.Cells.Item($j).Range.Text
                }}
                
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
                
                if ($rowText -match '著作权人信息') {{
                    for ($j = $i + 1; $j -le $table.Rows.Count; $j++) {{
                        $checkRow = $table.Rows.Item($j)
                        $checkText = $checkRow.Cells.Item(1).Range.Text
                        if ($checkText -match '联系人' -or $checkText -match '^\\s*$') {{ break }}
                        if ($checkText -match '公司/单位' -or $checkText -match '营业执照') {{ continue }}
                        $ownerName = $checkRow.Cells.Item(1).Range.Text.Trim()
                        if ($ownerName) {{ $owners += $ownerName }}
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
        
        Write-Host "  软件: $softwareName$version"
        Write-Host "  著作权人: $($owners.Count)人 - $($owners -join ', ')"
        
        $templateFile = Join-Path $templateDir "合作协议-$($owners.Count)方.doc"
        if (-not (Test-Path $templateFile)) {{
            Write-Host "  [FAIL] 模板不存在: $($owners.Count)方"
            $failCount++
            continue
        }}
        
        $contractDate = Parse-Date $completionDate
        $softwareFullName = "$softwareName$version"
        $copyCount = $owners.Count + 1
        
        $doc = $word.Documents.Open($templateFile)
        $find = $word.Selection.Find
        
        # 替换软件名称
        $find.Execute('智能心理压力情绪疏导与调解平台V1.0', $false, $false, $false, $false, $false, $true, 1, $false, $softwareFullName, 2)
        
        # 替换日期
        $find.Execute('2025-3-10', $false, $false, $false, $false, $false, $true, 1, $false, $contractDate, 2)
        
        # 替换当事人
        $sampleNames = @('王红梅', '汪庆军', '吴六韬', '赖羽羽', '刘茜茜', '丁姿慧', '刘澈', '曹冬梅', '谢奇秀', '钟海玲')
        for ($i = 0; $i -lt $owners.Count -and $i -lt $sampleNames.Count; $i++) {{
            $find.Execute($sampleNames[$i], $false, $false, $false, $false, $false, $true, 1, $false, $owners[$i], 2)
        }}
        
        # 替换份数
        $numWords = @('三', '四', '五', '六', '七', '八', '九', '十', '十一', '十二', '十三', '十四')
        foreach ($nw in $numWords) {{
            $find.Execute("$nw份", $false, $false, $false, $false, $false, $true, 1, $false, "$copyCount份", 2)
        }}
        
        # 保存
        $safeName = $softwareName -replace '[\\\\/:*?"<>|]', '-'
        $outputPath = Join-Path $outputDir "合作协议-$safeName.doc"
        $doc.SaveAs($outputPath)
        $doc.Close($false)
        
        Write-Host "  [OK] 已生成"
        $successCount++
        
    }} catch {{
        Write-Host "  [FAIL] 错误: $_"
        $failCount++
    }}
}}

$word.Quit()
Write-Host ""
Write-Host "处理完成! 成功: $successCount, 失败: $failCount"
'''
    
    # 保存脚本
    script_path = '/mnt/c/Temp/contracts/generate.ps1'
    with open(script_path, 'w', encoding='utf-8') as f:
        f.write(ps_script)
    
    print(f"\n正在执行生成脚本...")
    
    # 执行
    result = subprocess.run(
        ['powershell.exe', '-ExecutionPolicy', 'Bypass', '-File', 
         r'C:\Temp\contracts\generate.ps1'],
        capture_output=True,
        timeout=300,
        encoding='gbk',
        errors='replace'
    )
    
    print(result.stdout)
    if result.stderr and 'error' in result.stderr.lower():
        print("\n错误信息:", result.stderr)
    
    # 检查输出
    output_files = glob.glob(os.path.join(output_dir_wsl, '*.doc'))
    if output_files:
        print(f"\n生成的文件 ({len(output_files)} 个):")
        for f in output_files:
            print(f"  - {os.path.basename(f)}")
        print(f"\n文件位置: {output_dir_win}")


if __name__ == '__main__':
    main()
