$source=[IO.File]::ReadAllText((Join-Path $PSScriptRoot 'run_release_workflows.ps1'))
Invoke-Expression $source.Substring(0,$source.IndexOf("foreach(`$kind")).Replace('$PSScriptRoot',"'H:/Nigeria_Mosip/codex/openg2p-lab'")
$kind='individual'
Check returned $kind returned
Check correction2 $kind returned; Ui correct $kind; Check resubmitted $kind returned
Ui level1 $kind; Check level1 $kind returned
Ui level2 $kind; Check published $kind returned
Check prepare $kind rejected
Ui reject-action $kind; Check rejected $kind rejected; Ui rejected-view $kind
Check prepare $kind rejected-level2
Ui reject2-level1 $kind; Check level1 $kind rejected-level2
Ui reject2-action $kind; Check rejected $kind rejected-level2; Ui reject2-view $kind
Check create-change $kind change-returned
Ui return1 $kind change-returned; Check change-returned $kind change-returned
Ui view $kind change-returned; Ui correct $kind change-returned; Check change-resubmitted $kind change-returned
Ui approve1 $kind change-returned; Check change-level1 $kind change-returned
Ui return2 $kind change-returned; Check change-returned $kind change-returned
Check change-correction2 $kind change-returned; Ui correct $kind change-returned; Check change-resubmitted $kind change-returned
Ui approve1 $kind change-returned; Check change-level1 $kind change-returned
Ui approve2 $kind change-returned; Check change-approved $kind change-returned; Ui history $kind change-returned
foreach($stage in @(1,2)){
 $name="change-rejected-level$stage";Check create-change $kind $name
 if($stage -eq 2){Ui approve1 $kind $name; Check change-level1 $kind $name}
 Ui "reject-action$stage" $kind $name; Check change-rejected $kind $name; Ui rejected-view $kind $name
}
