from pathlib import Path
p=Path(__file__).parent/'registry-presentation.js';s=p.read_text();s=s.replace("const parent=cards[0].parentElement;parent.classList", "const parent=kind?cards[0].parentElement.parentElement:cards[0].parentElement;for(const card of cards)if(kind)card.parentElement.classList.add('nsipa-record-row');parent.classList");p.write_text(s)
