from __future__ import annotations

import copy
from collections.abc import Callable, Hashable
from typing import TYPE_CHECKING, Any, Union

if TYPE_CHECKING:
    import dask.base
    import dask_awkward

from coffea.dataset_tools.filespec import (
    DataGroupSpec,
    DatasetSpec,
)
from coffea.nanoevents import BaseSchema, NanoAODSchema, NanoEventsFactory
from coffea.processor import ProcessorABC

if TYPE_CHECKING:
    DaskOutputBaseType = Union[
        dask.base.DaskMethodsMixin,
        dict[Hashable, dask.base.DaskMethodsMixin],
        set[dask.base.DaskMethodsMixin],
        list[dask.base.DaskMethodsMixin],
        tuple[dask.base.DaskMethodsMixin],
    ]
    """short-hand for types we can output from an analysis"""
    # NOTE TO USERS: You can use nested python containers as arguments to dask.compute!
    DaskOutputType = Union[DaskOutputBaseType, tuple[DaskOutputBaseType, ...]]
    """short-hand for outputs of an analysis (one or more `DaskOutputBaseType`)"""
    GenericHEPAnalysis = Callable[[dask_awkward.Array], DaskOutputType]
    """short-hand for a function that injests a `dask_awkard.Array` and outputs `DaskOutputType`"""


def apply_to_dataset(
    data_manipulation: ProcessorABC | GenericHEPAnalysis,
    dataset: DatasetSpec | dict,
    schemaclass: BaseSchema = NanoAODSchema,
    metadata: dict[Hashable, Any] = {},
    uproot_options: dict[str, Any] = {},
) -> DaskOutputType | tuple[DaskOutputType, dask_awkward.Array]:
    """
    Apply the supplied function or processor to the supplied dataset.

    Parameters
    ----------
        data_manipulation : coffea.processor.ProcessorABC
            The user analysis code to run on the input dataset
        dataset : DatasetSpec or dict
            The data to be acted upon by the data manipulation passed in.
        schemaclass : coffea.nanoevents.BaseSchema, default coffea.nanoevents.NanoAODSchema
            The nanoevents schema to interpret the input dataset with.
        metadata : dict, default {}
            Metadata for the dataset that is accessible by the input analysis. Should also be dask-serializable.
            The keys just have to be hashable while the values can be any time.
        uproot_options : dict, default {}
            Options to pass to uproot. Pass at least
            ``{"allow_read_errors_with_report": True}`` to turn on file access reports.
            Since this dict is turned into keyword arguments, the keys have to be `str`.

    Returns
    -------
        out : DaskOutputType
            The output of the analysis workflow applied to the dataset
        report : dask_awkward.Array, optional
            The file access report for running the analysis on the input dataset. Needs to be computed in simultaneously with the analysis to be accurate.
    """
    if isinstance(dataset, dict):
        dataset = DatasetSpec.model_validate(dataset)
    maybe_base_form = dataset.form
    files = dataset.files
    events = NanoEventsFactory.from_root(
        files.model_dump(),
        metadata=metadata,
        schemaclass=schemaclass,
        known_base_form=maybe_base_form,
        uproot_options=uproot_options,
        mode="dask",
    ).events()

    report = None
    if isinstance(events, tuple):
        events, report = events

    out = None
    if isinstance(data_manipulation, ProcessorABC):
        out = data_manipulation.process(events)
    elif isinstance(data_manipulation, Callable):
        out = data_manipulation(events)
    else:
        raise ValueError("data_manipulation must either be a ProcessorABC or Callable")

    if report is not None:
        return out, report
    return (out,)


def apply_to_fileset(
    data_manipulation: ProcessorABC | GenericHEPAnalysis,
    fileset: DataGroupSpec | dict,
    schemaclass: BaseSchema = NanoAODSchema,
    uproot_options: dict[str, Any] = {},
) -> dict[str, DaskOutputType] | tuple[dict[str, DaskOutputType], dask_awkward.Array]:
    """
    Apply the supplied function or processor to the supplied fileset (set of datasets).

    Parameters
    ----------
        data_manipulation : ProcessorABC or GenericHEPAnalysis
            The user analysis code to run on the input dataset
        fileset : DataGroupSpec | dict
            The data to be acted upon by the data manipulation passed in. Metadata within the fileset should be dask-serializable.
        schemaclass : BaseSchema, default NanoAODSchema
            The nanoevents schema to interpret the input dataset with.
        uproot_options : dict[str, Any], default {}
            Options to pass to uproot. Pass at least {"allow_read_errors_with_report": True} to turn on file access reports.

    Returns
    -------
        out : dict[str, DaskOutputType]
            The output of the analysis workflow applied to the datasets, keyed by dataset name.
        report : dask_awkward.Array, optional
            The file access report for running the analysis on the input dataset. Needs to be computed in simultaneously with the analysis to be accurate.
    """
    if isinstance(fileset, dict):
        fileset = DataGroupSpec.model_validate(fileset)
    out = {}
    report = {}
    for name, dataset in fileset.items():
        metadata = copy.deepcopy(dataset.metadata)
        if metadata is None:
            metadata = {}
        metadata.setdefault("dataset", name)
        dataset_out = apply_to_dataset(
            data_manipulation, dataset, schemaclass, metadata, uproot_options
        )
        if isinstance(dataset_out, tuple) and len(dataset_out) > 1:
            out[name], report[name] = dataset_out
        else:
            out[name] = dataset_out[0]
    if len(report) > 0:
        return out, report
    return out
