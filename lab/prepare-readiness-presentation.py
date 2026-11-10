from pathlib import Path
root=Path(__file__).parent
p=root/'registration-ui/base.html';s=p.read_text()
marker='<link rel="stylesheet" href="{{prefix}}/static/style.css">'
if 'phase1-portal.css' not in s:
 assert marker in s;s=s.replace(marker,marker+'<link rel="stylesheet" href="{{prefix}}/static/phase1-portal.css">');p.write_text(s)
p=root/'persona-ui/src/shell.js';s=p.read_text()
s=s.replace("bar.id='ng2p-platform-bar';","bar.id='ng2p-platform-bar';bar.lang='en';") if "bar.lang='en'" not in s else s
s=s.replace("panel.id='ng2p-platform-guide';","panel.id='ng2p-platform-guide';panel.lang='en';") if "panel.lang='en'" not in s else s
p.write_text(s)
p=root/'knowledge/help.js';s=p.read_text()
if "button.lang='en'" not in s:s=s.replace("button.id='ng-km-launcher';","button.id='ng-km-launcher';button.lang='en';")
if "panel.lang='en'" not in s:s=s.replace("panel.id='ng-km-panel';","panel.id='ng-km-panel';panel.lang='en';")
if "help.lang='en'" not in s:s=s.replace("help.className='ng-km-inline';","help.className='ng-km-inline';help.lang='en';")
p.write_text(s)
