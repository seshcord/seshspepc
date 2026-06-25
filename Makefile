wiki: node_modules wiki/Home.md wiki/Specification.md 
wiki/Home.md:
	mkdir -p wiki
	git submodule update --init wiki
wiki/Specification.md: spec.yaml yaml2md.js yaml2wiki.js
	node yaml2wiki.js < spec.yaml > wiki/Specification.md

node_modules: package.json
	npm install
	touch node_modules
