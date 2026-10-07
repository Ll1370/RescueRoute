# Algorithm Design and Complexity

Paste this section into the README under "Algorithm design" and "Complexity analysis".

## The two strategies

Both strategies run on the same input and use the same feasibility check
(`find_feasible_match`). The only difference is the order in which donations
are considered, so any difference in results is caused by the ordering rule.

**FIFO baseline (`fifo.py`).** Donations are placed in a `deque` in arrival
order and removed from the front one at a time. Each donation gets the first
feasible recipient and volunteer. If none exists it is recorded as unassigned
with the reason.

**Greedy urgency-first (`greedy.py`).** Donations are placed in a `heapq`
priority queue and removed in priority order.

### Greedy rule

1. Schedule the donation with the least remaining shelf life first (earliest `expiry_time`).
2. If two donations have equal shelf life, schedule the larger quantity first.
3. If still tied, schedule the donation that arrived earlier.

This is implemented as the heap key `(expiry_time, -quantity, arrival_index)`.

All donations are planned at the same moment, so "least remaining shelf life"
and "earliest expiry time" give the same order.

## What greedy optimizes and why it is reasonable

At each step greedy picks the donation that will be lost soonest and commits
capacity to it. It never revisits a decision. The local goal is: do not let
the most urgent item wait behind a less urgent one.

This is reasonable because a donation with a long shelf life can often still
be placed later, while an urgent one cannot. FIFO ignores this and can spend
the last capacity on food that had hours left.

## Where greedy fails (trade-offs)

We do not claim the greedy schedule is globally optimal. Known weaknesses,
each backed by a test in `tests/test_schedulers.py`:

- **It can rescue less total food.** Urgency is checked before quantity, so a
  small urgent donation can use the last volunteer pickup that a much larger
  donation needed. See `test_greedy_can_rescue_less_food_than_fifo` (5 units
  rescued instead of 80).
- **Starvation / fairness.** A donation with a long shelf life is pushed
  behind every more urgent donation, even ones that arrived later. If capacity
  runs out first, it is never served although it was first in line. See
  `test_starvation_case_long_shelf_life_donation_is_deferred`. Each deferred
  donation lists who went ahead of it in `deferred_behind` and in its
  explanation.
- **No look-ahead.** Greedy takes the first feasible recipient and does not
  check whether that choice blocks a later donation that had only one
  compatible recipient.

## Complexity

Let **D** = number of donations, **R** = recipients, **V** = volunteers.

**Feasibility check for one donation.** Filtering recipients is O(R),
filtering volunteers is O(V), and the timing check tries recipient/volunteer
pairs, which is O(R * V) in the worst case. Capacity and pickup lookups are
O(1) because they use dictionaries keyed by ID, and the food-type check is
O(1) on average because accepted types are stored in a set.

| Step | FIFO | Greedy |
|---|---|---|
| Build the queue | O(D) | O(D) with `heapify` |
| Remove next donation, total | O(D) | O(D log D) |
| Feasibility checks, total | O(D * R * V) | O(D * R * V) |
| Deferral tracking, total | none | O(D^2) worst case |
| **Overall** | **O(D * R * V)** | **O(D log D + D^2 + D * R * V)** |

The dominant work in both strategies is matching, O(D * R * V). The heap adds
only O(D log D). Deferral tracking compares each donation with the ones
already processed, so it is O(D^2) in the worst case; it exists for
explainability and could be dropped or limited to the most recent line-jumper
if D became large.

Space is O(D + R + V) for the queue, the state dictionaries and the
assignment list, plus up to O(D^2) for the `deferred_behind` lists.

**Assumptions.** All donations are known before scheduling starts (batch
planning, not live arrivals). Input list order is arrival order. Each pickup
is one trip, so vehicle capacity applies per donation. A donation is never
split across recipients.
