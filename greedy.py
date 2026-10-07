"""Approach B: Greedy urgency-first strategy.

GREEDY RULE (state this exactly in the README):
  1. Schedule the donation with the least remaining shelf life first
     (earliest expiry_time).
  2. If two donations expire at the same time, schedule the larger quantity
     first.
  3. If still tied, schedule the one that arrived earlier.

The rule is "greedy" because it makes the locally best-looking choice (most
urgent donation) at every step and never goes back to undo a choice.
"""

import heapq

from matching import SchedulerState
from scheduler_common import process_donation


def priority_key(donation, arrival_index):
    """Smaller tuple = higher priority. Python compares tuples left to right.

    Quantity is negated because heapq is a MIN-heap and we want the LARGER
    quantity to come out first. arrival_index is the final tie-breaker, and
    since it is unique it also guarantees two keys are never fully equal.
    """
    return (donation.expiry_time, -donation.quantity, arrival_index)


def schedule_greedy(donations, recipients, volunteers):
    """Return a list of Assignment objects in the order greedy processed them."""
    state = SchedulerState(recipients, volunteers)
    assignments = []

    # Build the priority queue. Each entry is (key, donation).
    heap = [
        (priority_key(donation, index), donation)
        for index, donation in enumerate(donations)
    ]
    heapq.heapify(heap)                                   # O(D)

    processed = []        # (arrival_index, donation) for everything handled so far

    while heap:
        key, donation = heapq.heappop(heap)               # O(log D)
        arrival_index = key[2]

        assignment = process_donation(donation, recipients, volunteers, state, "greedy")

        # Deferral tracking: which donations arrived AFTER this one but were
        # scheduled BEFORE it? Those are the ones that "jumped the line".
        jumped_ahead = [
            other for other_index, other in processed if other_index > arrival_index
        ]
        if jumped_ahead:
            assignment.deferred_behind = [d.donation_id for d in jumped_ahead]
            assignment.decision_reason += " " + _deferral_note(donation, jumped_ahead)

        processed.append((arrival_index, donation))
        assignments.append(assignment)

    return assignments


def _deferral_note(donation, jumped_ahead):
    """Explain why each line-jumper went first, using the rule that decided it."""
    parts = []
    for other in jumped_ahead:
        if other.expiry_time < donation.expiry_time:
            why = "less remaining shelf life"
        else:
            # Same expiry and it arrived later, so quantity must have decided it.
            why = "same shelf life but a larger quantity"
        parts.append(f"{other.donation_id} ({why})")
    return (
        f"Deferred: {donation.donation_id} was considered after "
        + ", ".join(parts)
        + " under the urgency-first greedy rule."
    )
