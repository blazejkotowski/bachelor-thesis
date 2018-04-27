.PHONY: pdf figures clean merge

FIGURES:= phase-transition.png smooth-phase-transition.png real-dft.png spectral-leakage.png bandpass-filter.png bandstop-filter.png ath.png am.png

all: figures pdf

pdf: clean
	pdflatex -shell-escape thesis.tex
	bibtex thesis
	pdflatex -shell-escape thesis.tex
	pdflatex -shell-escape thesis.tex
	rm -f *.aux *.bak *.log *.blg *.bbl *.toc *.out *.pyg *lof

figures: $(FIGURES)

%.png: figures/%.py
	python $<

clean:
	rm -f *.aux *.bak *.log *.blg *.bbl *.toc *.out *.pyg *lof

merge:
	ruby merge.rb
