"""Tests for the FIFO and greedy schedulers (Algorithm & Optimization Lead)."""

from fifo import schedule_fifo
from greedy import schedule_greedy
from models import Donation, Recipient, Volunteer


# ---------- small builders so each test only states what matters ----------

def donation(donation_id, quantity=10, expiry_time=300, ready_time=0, food_type="prepared"):
    return Donation(donation_id, "Donor", food_type, quantity, expiry_time, "north", ready_time)


def recipient(recipient_id="R1", capacity=100, accepted=("prepared",), closing_time=1000):
    return Recipient(recipient_id, f"Shelter {recipient_id}", set(accepted), capacity, "north", closing_time)


def volunteer(volunteer_id="V1", vehicle_capacity=100, max_pickups=10):
    return Volunteer(volunteer_id, vehicle_capacity, "north", 0, 1000, max_pickups)


def by_id(assignments):
    return {a.donation_id: a for a in assignments}


# ------------------------------ tests ------------------------------------

def test_normal_match_is_assigned_by_both_strategies():
    donations = [donation("D1")]
    for schedule in (schedule_fifo, schedule_greedy):
        result = schedule(donations, [recipient()], [volunteer()])
        assert len(result) == 1
        assert result[0].status == "assigned"
        assert result[0].recipient_id == "R1"
        assert result[0].volunteer_id == "V1"
        assert result[0].scheduled_time == 0
        assert "D1" in result[0].decision_reason


def test_two_donations_competing_for_same_capacity():
    # Room for only one of the two 50-unit donations.
    donations = [donation("D1", quantity=50), donation("D2", quantity=50)]
    result = by_id(schedule_fifo(donations, [recipient(capacity=50)], [volunteer()]))
    assert result["D1"].status == "assigned"
    assert result["D2"].status == "unassigned"
    assert "capacity" in result["D2"].decision_reason


def test_fifo_and_greedy_produce_different_results():
    # D1 arrives first but lasts a long time. D2 arrives second and is urgent.
    donations = [
        donation("D1", quantity=50, expiry_time=600),
        donation("D2", quantity=50, expiry_time=120),
    ]
    recipients, volunteers = [recipient(capacity=50)], [volunteer()]

    fifo = by_id(schedule_fifo(donations, recipients, volunteers))
    greedy = by_id(schedule_greedy(donations, recipients, volunteers))

    assert fifo["D1"].status == "assigned" and fifo["D2"].status == "unassigned"
    assert greedy["D2"].status == "assigned" and greedy["D1"].status == "unassigned"


def test_starvation_case_long_shelf_life_donation_is_deferred():
    # D1 arrived first, but every later donation is more urgent and there are
    # only two pickups available, so D1 is pushed to the back and starves.
    donations = [
        donation("D1", expiry_time=900),
        donation("D2", expiry_time=100),
        donation("D3", expiry_time=200),
    ]
    result = schedule_greedy(donations, [recipient()], [volunteer(max_pickups=2)])

    assert [a.donation_id for a in result] == ["D2", "D3", "D1"]
    starved = result[-1]
    assert starved.status == "unassigned"
    assert starved.deferred_behind == ["D2", "D3"]
    assert "Deferred" in starved.decision_reason
    # FIFO would have served D1, which is the fairness trade-off.
    assert by_id(schedule_fifo(donations, [recipient()], [volunteer(max_pickups=2)]))["D1"].status == "assigned"


def test_greedy_tie_breakers_quantity_then_arrival():
    donations = [
        donation("D1", quantity=10, expiry_time=100),
        donation("D2", quantity=30, expiry_time=100),   # same expiry, larger -> first
        donation("D3", quantity=30, expiry_time=100),   # same as D2, arrived later
    ]
    result = schedule_greedy(donations, [recipient()], [volunteer()])
    assert [a.donation_id for a in result] == ["D2", "D3", "D1"]


def test_greedy_can_rescue_less_food_than_fifo():
    # Known weakness: one pickup available. Greedy spends it on the urgent
    # 5-unit donation; FIFO happens to spend it on the 80-unit one.
    donations = [
        donation("BIG", quantity=80, expiry_time=600),
        donation("SMALL", quantity=5, expiry_time=60),
    ]
    recipients, volunteers = [recipient()], [volunteer(max_pickups=1)]

    def rescued(assignments):
        quantities = {d.donation_id: d.quantity for d in donations}
        return sum(quantities[a.donation_id] for a in assignments if a.status == "assigned")

    assert rescued(schedule_fifo(donations, recipients, volunteers)) == 80
    assert rescued(schedule_greedy(donations, recipients, volunteers)) == 5


def test_fifo_never_marks_a_donation_as_deferred():
    donations = [donation("D1", expiry_time=900), donation("D2", expiry_time=100)]
    result = schedule_fifo(donations, [recipient()], [volunteer()])
    assert [a.donation_id for a in result] == ["D1", "D2"]
    assert all(a.deferred_behind == [] for a in result)


def test_empty_inputs_return_empty_or_unassigned():
    assert schedule_fifo([], [recipient()], [volunteer()]) == []
    assert schedule_greedy([], [recipient()], [volunteer()]) == []
    # Donations but nobody to take them: every donation still gets an explanation.
    for schedule in (schedule_fifo, schedule_greedy):
        result = schedule([donation("D1")], [], [])
        assert result[0].status == "unassigned"
        assert result[0].decision_reason


def test_schedulers_do_not_modify_their_inputs():
    donations = [donation("D1", quantity=50)]
    recipients = [recipient(capacity=50)]
    schedule_fifo(donations, recipients, [volunteer()])
    # Capacity is tracked in SchedulerState, so greedy starts from a clean slate.
    assert recipients[0].capacity == 50
    assert schedule_greedy(donations, recipients, [volunteer()])[0].status == "assigned"
