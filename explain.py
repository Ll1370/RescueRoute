from typing import Optional

def format_assigned_reason(
    donation_id: str,
    recipient_name: str,
    volunteer_id: str,
    shelf_life_remaining: int,
    food_type: str,
    quantity: int
) -> str:
    return (
        f"Donation {donation_id} was assigned to {recipient_name} with volunteer "
        f"{volunteer_id} because it expires in {shelf_life_remaining} mins, the recipient "
        f"accepts {food_type}, capacity is available, and the volunteer can carry {quantity} units."
    )

def format_unassigned_reason(donation_id: str, primary_blocker: str) -> str:
    return f"Donation {donation_id} could not be assigned because {primary_blocker}."

def format_deferred_reason(donation_id: str, prioritized_donation_id: str, rule_reason: str) -> str:
    return (
        f"Donation {donation_id} was considered after {prioritized_donation_id} "
        f"because {prioritized_donation_id} had {rule_reason} under the priority rule."
    )