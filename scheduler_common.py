"""Logic shared by both scheduling strategies.

FIFO and greedy differ ONLY in the order they look at donations. Once a
donation is chosen, both strategies do exactly the same thing with it, so
that step lives here. This keeps the comparison fair: any difference in the
results comes from the ordering rule and nothing else.
"""

from matching import find_feasible_match
from models import Assignment


def process_donation(donation, recipients, volunteers, state, strategy):
    """Try to place one donation and return an Assignment either way."""
    recipient, volunteer, scheduled_time, reason = find_feasible_match(
        donation, recipients, volunteers, state
    )

    if recipient is None:
        return Assignment(
            donation_id=donation.donation_id,
            recipient_id=None,
            volunteer_id=None,
            scheduled_time=None,
            decision_reason=(
                f"Donation {donation.donation_id} could not be assigned because {reason}."
            ),
            status="unassigned",
            strategy=strategy,
        )

    # Reserve the capacity and the volunteer pickup so later donations see it.
    state.commit(donation, recipient, volunteer)

    return Assignment(
        donation_id=donation.donation_id,
        recipient_id=recipient.recipient_id,
        volunteer_id=volunteer.volunteer_id,
        scheduled_time=scheduled_time,
        decision_reason=(
            f"Donation {donation.donation_id} was assigned to {recipient.name} with "
            f"volunteer {volunteer.volunteer_id} because {reason}."
        ),
        status="assigned",
        strategy=strategy,
    )
