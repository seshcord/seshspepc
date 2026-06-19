wiki: node_modules wiki/Home.md wiki/Packets.md wiki/Database.md
wiki/Home.md:
	git submodule update --init wiki
wiki/Packets.md: packets.yaml packets2doc.js 
	node packets2doc.js < packets.yaml > wiki/Packets.md
wiki/Database.md: database.yaml db2doc.js 
	node db2doc.js < database.yaml > wiki/Database.md

node_modules: package.json
	npm install
	touch node_modules
