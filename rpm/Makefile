PYTHON := python3
BUILD_HELPER := ./build-helper

VERSION = $(shell $(BUILD_HELPER) --version)
RELEASE = $(shell $(BUILD_HELPER) --release)
DATE = $(shell LC_ALL=C date +'%a %b %d %Y')
TARBALL = argparse_manpage-$(VERSION).tar.gz

all: argparse-manpage.spec $(TARBALL)

.PHONY: $(TARBALL)
$(TARBALL):
	rm -f $(TARBALL)
	cd .. && python -m build && cp "dist/argparse_manpage-$(VERSION).tar.gz" rpm/

argparse-manpage.spec: argparse-manpage.spec.tpl ../setup.py
	@echo "  GEN $@" ; \
	rm -f "$@.output" ; \
	sed -e "s|@VERSION@|$(VERSION)|g" \
	    -e "s|@RELEASE@|$(RELEASE)|g" \
	    -e "s|@DATE@|$(DATE)|g" \
	    $< > $@.output ; \
	chmod 0444 "$@.output" ; \
	mv -f "$@.output" "$@" # move when successful

srpm: all
	dir=`pwd` ; \
	rm *.src.rpm ; \
	rpmbuild --define "_sourcedir $$dir" \
		 --define "_rpmdir    $$dir" \
		 --define "_builddir  $$dir" \
		 --define "_specdir   $$dir" \
		 --define "_srcrpmdir $$dir" \
	     -bs *.spec

clean:
	rm -rf *.src.rpm *.tar.gz *.spec noarch
