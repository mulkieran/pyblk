.PHONY: upload-release
upload-release:
	python setup.py release register sdist upload

.PHONY: pylint
pylint:
	PYTHONPATH=src pylint src/pyblk \
		--reports=no \
		--disable=I \
		--disable=bad-continuation \
		--disable=duplicate-code \
		--msg-template="{path}:{line}: [{msg_id}({symbol}), {obj}] {msg}"

.PHONY: pylint-tests
pylint-tests:
	PYTHONPATH=src pylint tests \
		--reports=no \
		--disable=I \
		--disable=bad-continuation \
		--disable=duplicate-code \
		--disable=no-self-use \
		--msg-template="{path}:{line}: [{msg_id}({symbol}), {obj}] {msg}"

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
