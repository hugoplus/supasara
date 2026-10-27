import {spawnSync} from 'node:child_process';
import {fileURLToPath} from 'node:url';

// OneDrive can mark generated directories read-only. Windows then refuses
// Next.js's rmdir calls, even when their contents are writable.
if(process.platform==='win32'){
 const result=spawnSync('powershell.exe',['-NoProfile','-NonInteractive','-Command',`
$ErrorActionPreference = 'Stop'
$changed = 0
foreach ($name in @('.next', 'out')) {
 if (!(Test-Path -LiteralPath $name)) { continue }
 $root = Get-Item -LiteralPath $name -Force
 if (!$root.PSIsContainer -or $root.LinkType) { throw "Generated path must be an ordinary directory: $name" }
 $pending = New-Object 'System.Collections.Generic.Stack[System.IO.DirectoryInfo]'
 $pending.Push($root)
 while ($pending.Count -gt 0) {
  $directory = $pending.Pop()
  if ($directory.Attributes -band [IO.FileAttributes]::ReadOnly) {
   $directory.Attributes = $directory.Attributes -band (-bnot [IO.FileAttributes]::ReadOnly)
   $changed++
  }
  foreach ($child in @(Get-ChildItem -LiteralPath $directory.FullName -Directory -Force)) {
   if (!$child.LinkType) { $pending.Push($child) }
  }
 }
}
if ($changed -gt 0) { Write-Output "Cleared read-only attributes on $changed generated directories." }
`],{cwd:fileURLToPath(new URL('../',import.meta.url)),stdio:'inherit',windowsHide:true});
 if(result.error)throw result.error;
 if(result.status!==0)process.exit(result.status||1);
}
