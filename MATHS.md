# Mathematics of FTA


## Conway's Preface

For the first two years of working with fault trees,
I believed that the naive "initiator-equals-rate" paradigm
was the only valid framework
for fault trees involving both rates and probabilities.
In this paradigm, certain constructs are considered incorrect
(such as an AND gate with two rate inputs, or an OR gate with mixed inputs).

Having now read Vesely's 1970 paper\*,
I have come to understand that my said belief was incorrect.
Indeed, there are legitimate use cases for those allegedly incorrect constructs
(e.g. an OR gate with both probability and rate input
for modelling a backup generator that has a fixed probability of failing to start
plus a failure rate given it has started).

This page attempts to give an overview of the mathematics (or rather physics)
of Vesely's "Kinetic Tree Theory", which is the general framework
that every fault tree analyst should endeavour to learn and understand.
The naive "initiator-equals-rate" paradigm is merely a special case.

---

\* Vesely, W. E. (1970).
A time-dependent methodology for fault tree evaluation.
<cite>Nuclear engineering and design</cite>, 13(2), 337–360.
<<https://doi.org/10.1016/0029-5493(70)90167-6>>
