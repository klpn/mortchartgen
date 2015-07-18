docsrc:
	cat ../docs/mortchartdoc.md ../docs/refhead.md>mortchartdoc.md

pdf:
	cd ../docs; make pdf

pdfbib:
	cd ../docs; make pdfbib

indexgen:
	./indexgen.py

siteapp:
	ghc --make -threaded site.hs -package pandoc-1.14.1

buildinit: indexgen docsrc siteapp
	./site build

build: indexgen docsrc
	./site build

rebuild: indexgen docsrc siteapp
	./site rebuild
