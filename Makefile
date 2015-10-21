.PHONY: upload-release
upload-release:
	python setup.py release register sdist upload

.PHONY: pylint
pylint:
	PYTHONPATH=src ./check.py src/pyblk

.PHONY: pylint-tests
pylint-tests:
	PYTHONPATH=src ./check.py tests

.PHONY: check
check: pylint pylint-tests

PYREVERSE_OPTS = --output=pdf
.PHONY: view
view:
	-rm -Rf _pyreverse
	mkdir _pyreverse
	PYTHONPATH=src pyreverse ${PYREVERSE_OPTS} --project="pyblk" src/pyblk
	mv classes_pyblk.pdf _pyreverse
	mv packages_pyblk.pdf _pyreverse

.PHONY: archive
archive:
	git archive --output=./pyblk.tar.gz HEAD
