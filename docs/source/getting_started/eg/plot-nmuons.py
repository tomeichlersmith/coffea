import matplotlib.pyplot as plt
import mplhep

from coffea.util import load

mplhep.style.use("ROOT")

full_result = load("dimuonmass.coffea")

for dataset, result in full_result.items():
    result["h_nmuons"].plot(label=dataset)
plt.legend()
plt.ylabel("N Events")
plt.savefig("h_nmuons.png", bbox_inches="tight")
plt.clf()
