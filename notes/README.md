# Research plan


## Robustness checks to perform to validate the model


1. **Quantify the selection** bias induced when selecting subsamples of patents (EP patents, granted patents, top patents). What happens if we relax one of these constraints? Compare to random selection. Do clusters and clustering scores remain the same?
1. **Impact of modelling choices**. Does the result change if the model takes into account only text *similarity* and does not consider *citations*? What about the different types of citations (direct, BC, CC, LC)?
1. **Comparison between the new classification and the CPC and IPC classification**. Create a heatmap and show that the clusters are logical in all the domains and partially recover the CPC/IPC classification.
1. What if we **change the text source**, using the first page in spite of the claims? Do the clusters remain the same?
1. Does the result change while using different **clustering methods**?
1. Show the results for at least 3 different technological domains (CPC/IPC codes).


## Possible model extension

1. Quantify the **links between the different clusters** and **reduce the graph to its clusters** with the relevant algorithm.

## Research story

1. An appropriate **title** could be *What if we actually read patents? An alternative to the IPC/PC classification using a NLP approach*.
1. Explain that **the paper is a new recombination of well established components**: (1) citation links (2) text similarity using TF-IDF (3) community detection algorithm in weighted networks (Louvain/Leiden methods).
1. If the robustness checks unveil some variations while modifying the parameters, then the different configurations of the model are all useful - they tell a different story.
