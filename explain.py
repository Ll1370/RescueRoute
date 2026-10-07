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