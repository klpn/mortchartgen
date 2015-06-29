tex:
	pandoc -o mortchartdoc.tex mortchartdoc.md --template=PMMall.tex --latex-engine=lualatex --biblatex

pdf: tex
	lualatex mortchartdoc.tex

pdfbib: pdf
	biber mortchartdoc
	lualatex mortchartdoc.tex
