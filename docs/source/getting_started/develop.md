# Develop

This page is focused on getting you started with local (personal computer) development of an analysis.
As such, it will require a few example files to test run over.
Here, we use two example files so that we can demonstrate a common workflow in these analyses.
- [`nano_dimuon.root`](https://github.com/scikit-hep/coffea/raw/refs/heads/master/tests/samples/nano_dimuon.root): 40 events of data selected for muon pairs
- [`nano_dy.root`](https://github.com/scikit-hep/coffea/raw/refs/heads/master/tests/samples/nano_dy.root): 40 events of simulated [Drell-Yan](https://en.wikipedia.org/wiki/Drell%E2%80%93Yan_process)

Our overall goal is to reconstruct the Z mass peak by combining the 4-momenta of two muons with opposite charge
and calculating their mass.

## 0. Walk Before You Run
Coffea is focused on separating the code that does the Physics analysis
from the code that is just running the analysis over some amount of data.
For this example, I've done the same thing.
I have two files  `dimuonmass.py` containing the analysis code and `run-local.py`
which has the infrastructure to run the analysis.

:::{literalinclude} eg/0-dimuonmass.py
:caption: dimuonmass.py
:lineno-match:
:::

:::{literalinclude} eg/run-local.py
:caption: run-local.py
:lineno-match:
:::

Cool, let's see what happens when we run this.

:::{note}
I am technically running this example within the Coffea image for stability
and then using [denv](https://tomeichlersmith.github.io/denv/) to shorten
the contaier-running commands.
```
denv init coffeateam/coffea-dask-almalinux9:2026.9.0-py3.13
```
and then prefixing `python3` with `denv` everywhere below.

Using Coffea in this way should not be necessary, please open an issue
if you can show that your environment and the image are showing different
behavior despite using the same Coffea version.
:::

```bash
$ python3 run-local.py
Preprocessing 100% ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 2/2 [ 0:00:01 < 0:00:00 | 1.7 file/s ]
/usr/local/lib/python3.13/site-packages/coffea/nanoevents/schemas/nanoaod.py:297: RuntimeWarning: Missing
cross-reference index for LowPtElectron_electronIdx => Electron
  warnings.warn(
/usr/local/lib/python3.13/site-packages/coffea/nanoevents/schemas/nanoaod.py:297: RuntimeWarning: Missing
cross-reference index for LowPtElectron_genPartIdx => GenPart
  warnings.warn(
/usr/local/lib/python3.13/site-packages/coffea/nanoevents/schemas/nanoaod.py:297: RuntimeWarning: Missing
cross-reference index for LowPtElectron_photonIdx => Photon
  warnings.warn(
/usr/local/lib/python3.13/site-packages/coffea/nanoevents/schemas/nanoaod.py:297: RuntimeWarning: Missing
cross-reference index for FatJet_genJetAK8Idx => GenJetAK8
  warnings.warn(
/usr/local/lib/python3.13/site-packages/coffea/nanoevents/schemas/nanoaod.py:336: RuntimeWarning: Branch Photon_mass
already exists but its values will be replaced with 0.0
  warnings.warn(
/usr/local/lib/python3.13/site-packages/coffea/nanoevents/schemas/nanoaod.py:336: RuntimeWarning: Branch Photon_charge
already exists but its values will be replaced with 0.0
  warnings.warn(
Processing 100% ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 2/2 [ 0:00:01 < 0:00:00 | 1.4 chunk/s ]
{'bytesread': 186962, 'columns': [], 'entries': 80, 'processtime': 8.106231689453125e-06, 'chunks': 2}
{}
```
A few observations of note:
- There are a few warnings about missing cross-reference indices, but I am ignoring them because they pertain to branches that I will not be using in this analysis. Outputs later in this example will omit the them.
- The `Preprocessing` and `Processing` bars load live as the processing happens.
- The metrics report no columns being read but still many bytes read. This is because there are some internals that will be read no matter what.
- The final result output is empty because we didn't do anything!

In conclusion, we can successfully process events and our `run-local.py` script is able to run over the files without issue.

## 1. Count Muons
The main ingredient in our reconstruction of the mass peak is a pair of muons,
so let's start simple and just count the number of muons in the event.

:::{literalinclude} eg/1-dimuonmass.py
:caption: dimuonmass.py
:lineno-match:
:::

which produces
```bash
# omitting pre-processing and its warnings
Processing 100% ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 2/2 [ 0:00:01 < 0:00:00 | 1.1 chunk/s ]
{'bytesread': 187230, 'columns': ['nMuon-offsets'], 'entries': 80, 'processtime': 0.022721052169799805, 'chunks': 2}
{'DYJets': {'h_nmuons': Hist(Integer(0, 10, name='nmuons'), storage=Double()) # Sum: 40.0, 'events': 40}, 'Data': {'h_nmuons': Hist(Integer(0, 10, name='nmuons'), storage=Double()) # Sum: 40.0, 'events': 40}}
```
- We used {any}`ak.num` to count the number of `Muon` objects in each of the events. There are many other helper functions available from `awkward` and `numpy` that are tools in your toolbox when designing your analysis.
- You could use {any}`hist.axis.StrCategory` instead of putting `h_nmuons` inside the sub-dictionary.
  The goal is to keep the separate datasets distinct and these two methods are equivalent.
- The number of `bytesread` and `columns` have increased according to the fact that we have
  now accessed some data from the input files.

<details>
    <summary>Plotting Code</summary>

:::{literalinclude} eg/plot-nmuons.py
:::

</details>


:::{figure} eg/h_nmuons.png
:alt: Image of Muon Count Histograms Separated by Dataset
:figwidth: 500px
:align: center

The filled muon count histograms plot separately by dataset.
We should definitely be prepared for events that don't have exactly two muons!
:::

---
Below is a minimal processor that applies muon scale factors from `correctionlib` and produces a histogram.

```python
import awkward as ak
import correctionlib
import hist
from coffea import processor


class MuonProcessor(processor.ProcessorABC):
    def __init__(self, sf_path: str):
        self.corrections = correctionlib.CorrectionSet.from_file(sf_path)
        self.muon_sf = self.corrections["muon_sf"]

    def process(self, events):
        dataset = events.metadata["dataset"]

        # Create histogram with category axis
        h_mass = hist.Hist.new.StrCat([], growth=True, name="dataset").Reg(
            60, 60, 120, name="mass", label="mμμ [GeV]"
        ).Weight()

        # select OS dimuons
        muons = events.Muon[events.Muon.tightId]
        dimuons = ak.combinations(muons, 2, fields=["lead", "trail"])
        dimuons = dimuons[dimuons.lead.charge != dimuons.trail.charge]

        # correctionlib returns per-muon weights; take product per event
        sf_lead = self.muon_sf.evaluate(dimuons.lead.eta, dimuons.lead.pt)
        sf_trail = self.muon_sf.evaluate(dimuons.trail.eta, dimuons.trail.pt)
        event_weight = sf_lead * sf_trail

        mass = (dimuons.lead + dimuons.trail).mass
        h_mass.fill(
            dataset=dataset,
            mass=mass,
            weight=event_weight,
        )

        return {
            dataset: {
                "mass": h_mass,
                "events": len(events),
            }
        }
```
