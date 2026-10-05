from pathlib import Path
import base64,json,subprocess
root=Path(__file__).resolve().parents[1]
subprocess.run([str(root/'preview/vendor/node_modules/.bin/esbuild'),str(root/'preview/vendor/viewer.js'),'--bundle','--minify',f'--outfile={root}/preview/viewer.bundle.js'],check=True)
manifest=json.loads((root/'models/manifest.json').read_text())
titles=['Raspberry & cream','Blush & raspberry','Cream & raspberry','Raspberry & cream']
palette={'raspberry':'#ef4c7a','cream':'#fbfacf','blush':'#f9bfc5'}
cards=[]
for i,m in enumerate(manifest):
 m['base64']=base64.b64encode((root/m['file']).read_bytes()).decode()
 dots=''.join(f'<i style="background:{palette[c]}"></i>' for c in dict.fromkeys([m['fill'],m['outline'],m['highlight']]))
 cards.append(f'<article class="card"><div class="cardhead"><span class="num">DESIGN 0{i+1}</span><span class="dots">{dots}</span></div><div class="viewport" aria-label="Interactive 3D logo design {i+1}"></div><div class="cardfoot"><h2>{titles[i]}</h2><p class="details">{m["fill"].capitalize()} face · {m["outline"]} outline<br>Bevelled solid · two-sided details</p><button class="download" data-download="{i}">Download GLB ↓</button></div></article>')
html=(root/'preview/template.html').read_text().replace('__CARDS__',''.join(cards)).replace('__DATA__',json.dumps(manifest)).replace('__SCRIPT__',(root/'preview/viewer.bundle.js').read_text())
(root/'Sembang 3D Preview.html').write_text(html)
print('Built standalone offline preview.')
