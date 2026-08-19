# Scale out

Scaling does not require modifying the processor. Replace the executor and, if needed, provide configuration for the backing service.

```python
from dask.distributed import Client

client = Client("tcp://scheduler:8786")

cluster_runner = processor.Runner(
    executor=processor.DaskExecutor(client=client),
    schema=NanoAODSchema,
    savemetrics=True,
)

result_cluster, metrics_cluster = cluster_runner(
    fileset, processor_instance=MuonProcessor("muon_sf.json.gz")
)
```

You can follow the same pattern with {class}`~coffea.processor.FuturesExecutor`, {class}`~coffea.processor.ParslExecutor`, or {class}`~coffea.processor.TaskVineExecutor`. See {doc}`concepts` for background on processors and executors.
