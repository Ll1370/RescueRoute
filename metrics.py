from typing import Any
from models import Dataset, Assignment, Donation

def compute_metrics(dataset: Dataset, assignments: list[Assignment], urgent_threshold: int = 120) -> dict[str, Any]:
    donations_map: dict[str, Donation] = {}
    for donation in dataset.donations:
        donations_map[donation.donation_id] = donation

    assigned_records: list[Assignment] = []
    for assignment in assignments:
        if assignment.status == "assigned":
            assigned_records.append(assignment)

    unassigned_records: list[Assignment] = []
    for assignment in assignments:
        if assignment.status == "unassigned":
            unassigned_records.append(assignment)

    donations_received = len(dataset.donations)
    donations_assigned = len(assigned_records)
    donations_unassigned = len(unassigned_records)

    food_quantity_rescued = 0
    for assignment in assigned_records:
        donation = donations_map.get(assignment.donation_id)
        if donation:
            food_quantity_rescued += donation.quantity

    food_quantity_at_risk = 0
    for assignment in unassigned_records:
        donation = donations_map.get(assignment.donation_id)
        if donation:
            food_quantity_at_risk += donation.quantity

    urgent_donations: list[Donation] = []
    for donation in dataset.donations:
        if donation.expiry <= urgent_threshold:
            urgent_donations.append(donation)
    assigned_ids = set()
    for assignment in assigned_records:
        assigned_ids.add(assignment.donation_id)
    urgent_rescued = 0
    for donation in urgent_donations:
        if donation.donation_id in assigned_ids:
              urgent_rescued += 1
    if len(urgent_donations) > 0: # in case there are no urgent donations
        urgent_rescue_rate = (urgent_rescued / len(urgent_donations)) * 100
    else:
        urgent_rescue_rate = 0

    total_recipient_capacity = 0
    for recipient in dataset.recipients:
        total_recipient_capacity += recipient.capacity
    if total_recipient_capacity > 0:
        recipient_capacity_utilization = (food_quantity_rescued / total_recipient_capacity) * 100
    else:
        recipient_capacity_utilization = 0

    total_volunteer_capacity = 0
    for volunteer in dataset.volunteers:
        total_volunteer_capacity += volunteer.vehicle_capacity
    if total_volunteer_capacity > 0:
        volunteer_capacity_utilization = (food_quantity_rescued / total_volunteer_capacity) * 100
    else:
        volunteer_capacity_utilization = 0
    
    return {
         "donations_received": donations_received,
         "donations_assigned": donations_assigned,
         "donations_unassigned": donations_unassigned,
         "food_quantity_rescued": food_quantity_rescued,
         "food_quantity_at_risk": food_quantity_at_risk,
         "urgent_rescue_rate": round(urgent_rescue_rate,2),
         "recipient_capacity_utilization": round(recipient_capacity_utilization, 2),
         "volunteer_capacity_utilization": round(volunteer_capacity_utilization, 2),
    }
    

def compare_strategies(fifo_metrics: dict[str, Any], greedy_metrics: dict[str, Any]) -> dict[str, Any]:
    return {
        "delta_donations_assigned": greedy_metrics["donations_assigned"] - fifo_metrics["donations_assigned"],
        "delta_food_rescued": greedy_metrics["food_quantity_rescued"] - fifo_metrics["food_quantity_rescued"],
        "delta_urgent_rate": round(greedy_metrics["urgent_rescue_rate"] - fifo_metrics["urgent_rescue_rate"], 2),
    }