docsrc:
	cat ../docs/mortchartdoc.md ../docs/refhead.md>mortchartdoc.md

indexgen:
	./indexgen.py

siteapp:
	ghc --make -threaded site.hs -package pandoc-1.14.1

buildinit: docsrc indexgen siteapp
	./site build

build: docsrc indexgen
	./site build

rebuild: docsrc indexgen siteapp
	./site rebuild
