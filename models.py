from dataclasses import dataclass
@dataclass(frozen=True)
class Donation:
    donation_id: str
    donor_name: str
    food_type: str
    quantity: int
    expiry: int
    pickup_area: str
    ready_time: int
@dataclass(frozen=True)
class Recipient:
    recipient_id: str
    organization_name: str
    accepted_food_types: frozenset[str]
    capacity: int
    area: str
    closing_time: int
@dataclass(frozen=True)
class Volunteer:
    volunteer_id: str
    vehicle_capacity: int
    area: str
    available_from: int
    available_until: int
    maximum_pickups: int
@dataclass(frozen=True)
class Dataset:
    donations: list[Donation]
    recipients: list[Recipient]
    volunteers: list[Volunteer]
@dataclass(frozen=True)
class Assignment:
    donation_id: str
    recipient_id: str | None
    volunteer_id: str | None
    scheduled_time: int | None
    decision_reason: str
    status: str # "assigned", "unassigned", or "deferred"