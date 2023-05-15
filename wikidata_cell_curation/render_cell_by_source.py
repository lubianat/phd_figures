import matplotlib.pyplot as plt
from SPARQLWrapper import SPARQLWrapper, JSON
from collections import Counter
from matplotlib.gridspec import GridSpec

sparql = SPARQLWrapper("https://query.wikidata.org/sparql")

sparql.setQuery(
    """
    # Your SPARQL query goes here
    SELECT DISTINCT  ?reference ?referenceLabel (count(DISTINCT ?item) as ?count) (SAMPLE(?item) as ?sample_item) (SAMPLE(?itemLabel) as ?sample_label)
    WHERE
    {
        ?item wdt:P279* wd:Q7868 .
        ?item rdfs:label ?itemLabel . 
        FILTER(LANG(?itemLabel) = "en")
        ?item p:P31 ?statement. 
        ?statement prov:wasDerivedFrom ?provenance .
        ?provenance pr:P248 ?reference .
        SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en" }
    }
    GROUP BY ?reference ?referenceLabel  
    ORDER BY DESC(?count)
"""
)

sparql.setReturnFormat(JSON)
results = sparql.query().convert()

refs = [result["referenceLabel"]["value"] for result in results["results"]["bindings"]]
counts = [int(result["count"]["value"]) for result in results["results"]["bindings"]]

# Define the subplot layout
fig = plt.figure(figsize=(20, 15))
gs = GridSpec(4, 2, height_ratios=[3, 1, 1, 1], width_ratios=[1, 1])
ax0 = plt.subplot(gs[0:2, 0])  # span all rows and take the first column
ax1 = plt.subplot(gs[0:1, 1])  # take only the first row and the second column


counter = Counter(counts)
ax0.scatter(list(counter.values()), list(counter.keys()), color="skyblue")
ax0.set_yscale("log")
ax0.set_xscale("log")
ax0.set_ylabel("# of cell classes (log10)")
ax0.set_xlabel("# of sources that yielded each a # of cell classes (log10)")
ax0.set_title("A. Distribution of cell classes per source")

refs_top10 = refs[:10]
counts_top10 = counts[:10]

ax1.scatter(range(len(refs_top10)), counts_top10, color="red")
ax1.set_yscale("log")
ax1.set_xticks(range(len(refs_top10)))
ax1.set_xticklabels(refs_top10, rotation=60, fontsize=8, ha="right")  # Adjusted here
ax1.set_ylabel("# of cell classes (log10)")
ax1.set_title("B. Top 10 sources for cell classes on Wikidata")

for i, txt in enumerate(counts_top10):
    ax1.annotate(txt, (i + 0.1, counts_top10[i]))

plt.tight_layout()
plt.savefig("sources_for_cell_classes_on_wikidata.png")
plt.savefig("sources_for_cell_classes_on_wikidata.pdf")
plt.savefig("sources_for_cell_classes_on_wikidata.svg")
plt.show()
