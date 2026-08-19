# Getting Started

Coffea couples the columnar data model of Awkward Array with a thin execution layer so that an analysis can move from a laptop to a cluster without rewrites.
The workflow always follows the same pattern:

1. Implement a {class}`coffea.processor.ProcessorABC` that turns event data into accumulators.
2. Execute it with {class}`coffea.processor.Runner` using a local executor while you iterate.
3. Swap the executor when you are ready to scale out.

This overall workflow is pretty abstract. The rest of these sections are focused on helping
explain more of the vocabulary used regularly within coffea and its documentation,
how to install ``coffea``, writing your first ``Processor``, and scaling out your first ``Processor``
to be able to analyze larger amounts of data.

```{toctree}
:maxdepth: 1
:caption: Table of Contents
concepts.md
installation.md
develop-local.md
scale-out.md
```
