# Fault tree analysis mathematics


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

Primary events (called primary failures by Vesely)
are the atoms (representing failures) that make up a fault tree.
These are entities that, over the course of time,
switch from unfailed to failed
(and back to unfailed if the failure is repairable).

In the general framework, *all* primary events are characterised
by a failure rate and a repair rate.


### Failure rate

The failure rate `λ(t)` is defined as

```
λ(t) = Pr(becomes failed between t and t+dt | unfailed at time t) / dt,
```

where `dt` is an infinitesimal increment in the time `t`.
Note the conditional nature of the probability.


### Repair rate

The repair rate `μ(t)` is defined as

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


### Failure probability

The failure probability `q(t)` is found by noting that a factor of `1 − q(t)`
will convert between the conditional quantity `λ(t)`
and the unconditional quantity `ω(t)`, i.e.

```
ω(t) = (1 − q(t)) λ(t),
q(t) = 1 − ω(t) / λ(t).
```


### Special case: constant probability

Initially I could not understand
how a primary failure with constant probability `q(t) = Q`
could be represented using this framework,
which has `λ(t)` and `μ(t)` has the fundamental quantities.

After much thought, it occurred to me that we must have

```
λ(t) = 0,
ω(t) = 0,
q(t) = 1 − 0 / 0,
```

where the indeterminacy in the last expression resolves to Q.

There are two (highly philosophical) ways to think about this:

1. Primary events of constant probability
   don't actually switch from unfailed to failed.
   It's either one or the other for all time,
   with the decision made (by God if you like) outside the confines of time.
2. Primary events of constant probability
   switch instantly from unfailed to failed
   with that probability at `t = 0`.
   In symbols, `ω(t) = Q δ(t)`, where `δ(t)` is the unit impulse (or Dirac delta).

Both are compelling. The first does not require invocation of impulse functions.
The second allows us to think in terms of a random variable for failure time
having the distribution `Q δ(t) + (1−Q) δ(t−∞)`.


## Gates

Gates are the entities that encode failures
as logical combinations of other failures.
Like primary events, gates are entities that, over the course of time,
switch from unfailed to failed
(and back to unfailed if relevant failures are repairable).

- An AND gate (conjunction) is failed if all of its inputs are failed.
- An OR gate (disjunction) is failed if any of its inputs are failed.


## Boolean algebra

It is useful to represent primary events by Boolean expressions,
so that a value of `FALSE` corresponds the unfailed state
and a value of `TRUE` corresponds to the failed state.

The Boolean expression for a gate is obtained by applying the relevant operation
(logical AND or logical OR) to the expressions for the gate's inputs.

In this document we use electrical engineering notation,
where `FALSE` is denoted by `0`, `TRUE` by `1`,
logical AND by multiplication, and logical OR by addition.

For the top gate (or, more generally, any gate),
we reduce its Boolean expression to a sum of products
in which each product is minimal
(i.e. every factor in the product is necessary to cause the failure of the gate).

These minimal product terms are precisely the sought-after
minimal cut sets of fault tree analysis (called mode failures by Vesely).
Having determined the minimal cut sets, it only remains to compute
the failure characteristics (rate, intensity, and probability),
firstly of each minimal cut set, and subsequently of their disjunction (sum).
