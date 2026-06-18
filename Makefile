wiki: wiki/Home.md wiki/Packets.md
wiki/Home.md:
	git submodule update --init wiki
wiki/Packets.md: packets.yaml
	node packets2doc.js < packets.yaml > wiki/Packets.md



