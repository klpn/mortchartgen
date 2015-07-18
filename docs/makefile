tex:
	pandoc -o mortchartdoc.tex mortchartdoc.md --template=PMMall.tex --latex-engine=lualatex --biblatex

html:
	cat mortchartdoc.md refhead.md>mcdtohtml.md
	pandoc -o mortchartdoc.html mcdtohtml.md -s --bibliography=mortchartdoc_biber.bib --smart --mathjax --base-header-level=2 --toc
	perl -i -pe 's/“/”/g;s/‘/’/g' mortchartdoc.html

pdf: tex
	lualatex mortchartdoc.tex

pdfbib: pdf
	biber mortchartdoc
	lualatex mortchartdoc.tex
