specs: wiki/packets.md
wiki:
	mkdir wiki

wiki/packets.md: wiki packets.yaml
	node packets2doc.js < packets.yaml > wiki/packets.md



