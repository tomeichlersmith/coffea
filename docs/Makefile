# check whether parallel jobs were enabled for make
_PARALLEL_JOBS_FLAG = $(filter -j%,$(MAKEFLAGS))

# number of processors on this machine (always non-empty)
_NPROC := $(shell nproc)
# number given by jobs flag (empty if `-j` absent or does not have following N)
_NJOBS_REQ = $(patsubst -j%,%,$(_PARALLEL_JOBS_FLAG))
# or returns first instance of non-empty string
# if `-j` given on command line, return N or number of processors
# otherwise use default of 1
NJOBS = $(if $(_PARALLEL_JOBS_FLAG),$(or $(_NJOBS_REQ),$(_NPROC)),1)

# build options
#   --builder html                    : choose to build the html target
# 	--warning-file build/warnings.txt : dump warnings into build/warnings.txt for later review
# 	--nitpicky                        : warn on every missing link
OPTIONS=--builder html --warning-file build/warnings.txt --nitpicky --jobs $(NJOBS)

# sphinx-build
# 	-M     -> use "make mode" for use within a Makefile,
# 			      needs to be first followed by 'builder', source dir, and build dir
# 	html   -> "builder" which type of target to build
# 	source -> directory containing source files relative to this Makefile
# 	build  -> directory where generated files should be put
# 	..args -> rest of the line can be normal sphinx-build arguments
html: source/modules
	sphinx-build source build/html $(OPTIONS)

# auto-generated references
# construct ReST files for the doc website from the module docstrings
# sphinx-autogen
# 	source/api_reference.md -> root source file containing autosummary and/or autodoc
# 	-t source/_templates   -> define directory with custom templates
# 	-o source/modules      -> output directory where generated rst should go
source/modules: source/api_reference.md
	sphinx-autogen source/api_reference.md -t source/_templates -o source/modules

# remove generated files
clean:
	rm -rf build source/modules source/api

# auto-build the site after the source changes
# this is only helpful when doing a lot of writing within the source/
# directory, since updates to the docstrings need to pass through sphinx-autogen
# before getting to sphinx-build, they do not get picked up in the auto-build
watch:
	sphinx-autobuild source build/html $(OPTIONS)
# using 'build/html' as the output directory since that is the output directory
# for "make mode" with the command line '-M html source build'

.PHONY: clean
