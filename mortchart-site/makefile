tex:
	pandoc -o mortchartdoc.tex mortchartdoc_norefhead.md --template=PMMall.tex --latex-engine=lualatex --biblatex

docsrc:
	cat mortchartdoc_norefhead.md refhead.md>mortchartdoc.md

pdf: tex
	lualatex mortchartdoc.tex

pdfbib: pdf
	biber mortchartdoc
	lualatex mortchartdoc.tex

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
