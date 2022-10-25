.PHONY: check lint unittests

check:
	$(MAKE) unittests
	$(MAKE) lint

unittests:
	PYTHON=python3 ./check

lint:
	vcs-diff-lint
