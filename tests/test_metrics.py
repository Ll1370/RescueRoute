from models import Dataset, Donation, Recipient, Volunteer, Assignment
from metrics import compute_metrics, compare_strategies


def test_compute_metrics():
    dataset = Dataset(
        donations=[
            Donation(donation_id="D1", donor_name="Donor A", food_type="produce", quantity=10, expiry=60, pickup_area="Zone A", ready_time=0),
            Donation(donation_id="D2", donor_name="Donor B", food_type="bakery", quantity=20, expiry=200, pickup_area="Zone B", ready_time=5),
        ],
        recipients=[
            Recipient(recipient_id="R1", organization_name="Shelter 1", accepted_food_types=frozenset(["produce", "bakery"]), capacity=50, area="Zone A", closing_time=300)
        ],
        volunteers=[
            Volunteer(volunteer_id="V1", vehicle_capacity=100, area="Zone A", available_from=0, available_until=300, maximum_pickups=2)
        ],
    )

    assignments = [
        Assignment(donation_id="D1", recipient_id="R1", volunteer_id="V1", scheduled_time=12, decision_reason="Feasible match", status="assigned"),
        Assignment(donation_id="D2", recipient_id=None, volunteer_id=None, scheduled_time=None,decision_reason="No capacity", status="unassigned"),
    ]

    metrics = compute_metrics(dataset, assignments, urgent_threshold=120)

    # Assertions for all 8 metrics
    assert metrics["donations_received"] == 2
    assert metrics["donations_assigned"] == 1
    assert metrics["donations_unassigned"] == 1
    assert metrics["food_quantity_rescued"] == 10
    assert metrics["food_quantity_at_risk"] == 20
    assert metrics["urgent_rescue_rate"] == 100.0
    assert metrics["recipient_capacity_utilization"] == 20.0
    assert metrics["volunteer_capacity_utilization"] == 10.0


def test_compare_strategies():
    fifo = {
        "donations_assigned": 1,
        "food_quantity_rescued": 10,
        "urgent_rescue_rate": 50.0,
    }
    greedy = {
        "donations_assigned": 2,
        "food_quantity_rescued": 25,
        "urgent_rescue_rate": 100.0,
    }

    deltas = compare_strategies(fifo, greedy)

    assert deltas["delta_donations_assigned"] == 1
    assert deltas["delta_food_rescued"] == 15
    assert deltas["delta_urgent_rate"] == 50.0