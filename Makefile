.PHONY: run test stress

run:
	python -m swiftroute.api

test:
	python -m unittest discover -s tests -v

stress:
	python -m scripts.stress_simulation
