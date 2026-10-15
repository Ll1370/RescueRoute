# RescueRoute: Transparent Food Rescue Scheduling Engine

> **Disclaimer**: This is an educational prototype using simulated data and should not be used for real-world operational deployment

## Overview
RescueRoute matches surplus food donations with community recipients and volunteer drivers using two distinct scheduling strategies:
1. **FIFO Baseline**: Processes donations strictly by arrival order.
2. **Greedy Urgency-First**: Prioritizes donations with the least remaining shelf life, using quantity and arrival time as tie-breakers.


## Installation & Setup
```bash
git clone <https://github.com/Ll1370/RescueRoute.git>
cd RescueRoute
python3 -m venv venv
source venv/bin/activate
pip install pytest
```

## Running the Application
```bash
python main.py
```
### 

For additional parameters for the command
```bash
python main.py -h
```

## Running the Tests
```bash
python -m pytest tests/ -v
```

## Algorithm Design 

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

## Complexity Analysis

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

## References

Bonnie's Reference: 
CSPC335 Week 2 Data Structure PPT 
- Slides 9 Python list
- Slide 20 Duplicate ID Detection
- Slide 22 Dictionaries for the format and the meaning for the ID's
- I used Codex to help to simulated sample data, and to identify and correct formatting, and logic errors.