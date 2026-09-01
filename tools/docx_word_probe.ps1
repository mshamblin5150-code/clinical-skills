param(
    [Parameter(Mandatory = $true)]
    [string]$ProbeDirectory,

    [Parameter(Mandatory = $true)]
    [string]$EditText
)

$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new($false)

$WdBorderTop = -1
$WdBorderLeft = -2
$WdBorderBottom = -3
$WdBorderRight = -4
$WdBorderHorizontal = -5
$WdBorderVertical = -6
$WdHeaderFooterPrimary = 1
$WdDoNotSaveChanges = 0
$WdActiveEndPageNumber = 3
$WdStatisticPages = 2
$WdAlertsNone = 0

function Border-LineStyle($Borders, [int]$Index) {
    try {
        return [int]$Borders.Item($Index).LineStyle
    }
    catch {
        return $null
    }
}

function Paragraph-Record($Paragraph, [int]$Index) {
    $range = $Paragraph.Range
    $format = $Paragraph.Format
    $style = $range.Style
    [pscustomobject]@{
        index = $Index
        text = $range.Text.Trim([char]13, [char]7)
        style = $style.NameLocal
        page = [int]$range.Information($WdActiveEndPageNumber)
        alignment = [int]$format.Alignment
        first_line_indent_points = [double]$format.FirstLineIndent
        left_indent_points = [double]$format.LeftIndent
        space_after_points = [double]$format.SpaceAfter
        line_spacing_points = [double]$format.LineSpacing
        line_spacing_rule = [int]$format.LineSpacingRule
        page_break_before = [int]$format.PageBreakBefore
        outline_level = [int]$format.OutlineLevel
        font_name = $range.Font.Name
        font_size_points = [double]$range.Font.Size
        bold = [int]$range.Font.Bold
        italic = [int]$range.Font.Italic
    }
}

function Table-Record($Table, [int]$Index) {
    $headerBottoms = @()
    if ($Table.Rows.Count -gt 0) {
        foreach ($cell in $Table.Rows.Item(1).Cells) {
            $headerBottoms += Border-LineStyle $cell.Borders $WdBorderBottom
        }
    }
    $rowBottoms = @()
    foreach ($row in $Table.Rows) {
        $cellBottoms = @()
        foreach ($cell in $row.Cells) {
            $cellBottoms += Border-LineStyle $cell.Borders $WdBorderBottom
        }
        $rowBottoms += ,$cellBottoms
    }
    [pscustomobject]@{
        index = $Index
        rows = [int]$Table.Rows.Count
        columns = [int]$Table.Columns.Count
        style = $Table.Style.NameLocal
        borders = [ordered]@{
            top = Border-LineStyle $Table.Borders $WdBorderTop
            left = Border-LineStyle $Table.Borders $WdBorderLeft
            bottom = Border-LineStyle $Table.Borders $WdBorderBottom
            right = Border-LineStyle $Table.Borders $WdBorderRight
            inside_h = Border-LineStyle $Table.Borders $WdBorderHorizontal
            inside_v = Border-LineStyle $Table.Borders $WdBorderVertical
        }
        header_cell_bottoms = $headerBottoms
        row_cell_bottoms = $rowBottoms
    }
}

$word = $null
$documents = @()
try {
    $word = New-Object -ComObject Word.Application
    $word.Visible = $false
    $word.DisplayAlerts = $WdAlertsNone

    foreach ($file in Get-ChildItem -LiteralPath $ProbeDirectory -Filter "*.docx" |
        Where-Object BaseName -ne "word-saved" | Sort-Object Name) {
        $document = $null
        try {
            $document = $word.Documents.Open($file.FullName, $false, $true, $false)
            $paragraphs = @()
            for ($i = 1; $i -le $document.Paragraphs.Count; $i++) {
                $paragraphs += Paragraph-Record $document.Paragraphs.Item($i) $i
            }

            $tables = @()
            for ($i = 1; $i -le $document.Tables.Count; $i++) {
                $tables += Table-Record $document.Tables.Item($i) $i
            }

            $section = $document.Sections.Item(1)
            $header = $section.Headers.Item($WdHeaderFooterPrimary)
            $fields = @()
            foreach ($field in $header.Range.Fields) {
                $fields += [pscustomobject]@{
                    type = [int]$field.Type
                    code = $field.Code.Text.Trim()
                    result = $field.Result.Text.Trim([char]13, [char]7)
                }
            }

            $documents += [pscustomobject]@{
                key = $file.BaseName
                pages = [int]$document.ComputeStatistics($WdStatisticPages)
                margins_points = [ordered]@{
                    top = [double]$section.PageSetup.TopMargin
                    right = [double]$section.PageSetup.RightMargin
                    bottom = [double]$section.PageSetup.BottomMargin
                    left = [double]$section.PageSetup.LeftMargin
                }
                paragraphs = $paragraphs
                tables = $tables
                header = [pscustomobject]@{
                    exists = [int]$header.Exists
                    alignment = [int]$header.Range.ParagraphFormat.Alignment
                    page_numbers = [int]$header.PageNumbers.Count
                    fields = $fields
                }
            }
        }
        finally {
            if ($null -ne $document) {
                $document.Close($WdDoNotSaveChanges)
                [void][Runtime.InteropServices.Marshal]::FinalReleaseComObject($document)
            }
        }
    }

    $savedCopy = Join-Path $ProbeDirectory "word-saved.docx"
    $saveProbe = $null
    try {
        $saveProbe = $word.Documents.Open($savedCopy, $false, $false, $false)
        $saveProbe.Content.InsertAfter($EditText)
        $saveProbe.Save()
    }
    finally {
        if ($null -ne $saveProbe) {
            $saveProbe.Close($WdDoNotSaveChanges)
            [void][Runtime.InteropServices.Marshal]::FinalReleaseComObject($saveProbe)
        }
    }

    [pscustomobject]@{
        instrument = "Microsoft Word COM"
        word_version = $word.Version
        word_build = $word.Build
        saved_copy = $savedCopy
        documents = $documents
    } | ConvertTo-Json -Depth 10
}
finally {
    if ($null -ne $word) {
        $word.Quit()
        [void][Runtime.InteropServices.Marshal]::FinalReleaseComObject($word)
    }
    [GC]::Collect()
    [GC]::WaitForPendingFinalizers()
}
