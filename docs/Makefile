
.PHONY: default build

default: build

clean:
	rm -rf *.aux *.log
	rm -rf authentication.pdf \
		worst_case.pdf worst_case.png \
		best_case.pdf best_case.png \
		privilege_hierarchy.pdf privilege_hierarchy.png

build:
	pdflatex privilege_hierarchy.tex
	convert -density 300 privilege_hierarchy.pdf privilege_hierarchy.png
	pdflatex best_case.tex
	convert -density 300 best_case.pdf best_case.png
	pdflatex worst_case.tex
	convert -density 300 worst_case.pdf worst_case.png
	pandoc authentication.md -o authentication.pdf

