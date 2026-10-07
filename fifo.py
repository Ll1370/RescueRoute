"""Approach A: FIFO baseline.

Donations are processed in arrival order, which is the order they appear in
the input list. Each one gets the first feasible recipient and volunteer.
Donations with no feasible match are recorded as unassigned.
"""

from collections import deque

from matching import SchedulerState
from scheduler_common import process_donation


def schedule_fifo(donations, recipients, volunteers):
    """Return a list of Assignment objects, one per donation, in arrival order."""
    state = SchedulerState(recipients, volunteers)
    assignments = []                      # ordered audit history

    queue = deque(donations)              # deque: O(1) removal from the front
    while queue:
        donation = queue.popleft()        # oldest arrival first
        assignments.append(
            process_donation(donation, recipients, volunteers, state, "fifo")
        )

    return assignments
