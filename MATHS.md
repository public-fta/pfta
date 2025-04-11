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
(e.g. an OR gate with both probability and rate input,
for modelling a backup generator that has a fixed probability of failing to start
plus a failure rate given it has started).

This page attempts to give an overview of the mathematics (or rather physics)
of Vesely's "Kinetic Tree Theory", which is the general framework
that every fault tree analyst should endeavour to learn and understand.
The naive "initiator-equals-rate" paradigm is merely a special case of it.

---

\* Vesely, W. E. (1970).
A time-dependent methodology for fault tree evaluation.
<cite>Nuclear engineering and design</cite>, 13(2), 337–360.
<<https://doi.org/10.1016/0029-5493(70)90167-6>>


## Primary events

<i>Primary events</i> (called <i>primary failures</i> by Vesely)
are the atoms (representing failures) that make up a fault tree.
These are entities that, over the course of time,
switch from <i>unfailed</i> to <i>failed</i>
(and back to unfailed if the failure is repairable).

In the general framework, *all* primary events are characterised
by a failure rate and a repair rate.


### Failure rate

The failure rate `λ(t)` of a primary event is defined as

```
λ(t) = Pr(becomes failed between t and t+dt | unfailed at time t) / dt,
```

where `dt` is an infinitesimal increment in the time `t`.
Note the conditional nature of the probability.


### Repair rate

The repair rate `μ(t)` of a primary event is defined as

```
μ(t) = Pr(becomes unfailed between t and t+dt | failed at time t) / dt,
```

where `dt` is an infinitesimal increment in the time `t`.
Note the conditional nature of the probability.


### Failure intensity

The failure intensity `ω(t)` (denoted `w(t)` in Vesely's typography) is defined as

```
ω(t) = (instantaneous) "becomes-failed" count per time at time t.
```
Note the unconditional nature of this expression,
in contrast with the conditional nature of `λ(t)`.

It can be shown that `ω(t)` satisfies an integral equation
whose components are completely determined by `λ(t)` and `μ(t)`.
See Vesely's equation (8).

For the special case where the primary failure is non-repairable,
the solution reduces to

```
ω(t) = λ(t) exp(−∫ [0 to t] λ(t') dt').
```


### Special case: constant probability
