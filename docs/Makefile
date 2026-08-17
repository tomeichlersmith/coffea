html: source/modules
	sphinx-build -M html --warning-file build/warnings --nitpicky source build

source/modules: source/api_reference.md
	sphinx-autogen source/api_reference.md -t source/_templates -o source/modules

clean:
	rm -rf build source/modules source/api

watch:
	sphinx-autobuild source build

.PHONY: clean
