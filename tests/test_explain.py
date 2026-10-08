from explain import (
    format_assigned_reason,
    format_unassigned_reason,
    format_deferred_reason,
)


def test_format_assigned_reason():
    result = format_assigned_reason(
        donation_id="D1",
        recipient_name="Community Shelter",
        volunteer_id="V1",
        shelf_life_remaining=45,
        food_type="produce",
        quantity=20,
    )

    expected = (
        "Donation D1 was assigned to Community Shelter with volunteer V1 "
        "because it expires in 45 mins, the recipient accepts produce, "
        "capacity is available, and the volunteer can carry 20 units."
    )
    assert result == expected


def test_format_unassigned_reason():
    result = format_unassigned_reason(
        donation_id="D2",
        primary_blocker="no volunteer has sufficient vehicle capacity",
    )

    expected = (
        "Donation D2 could not be assigned because "
        "no volunteer has sufficient vehicle capacity."
    )
    assert result == expected


def test_format_deferred_reason():
    result = format_deferred_reason(
        donation_id="D3",
        prioritized_donation_id="D1",
        rule_reason="shorter shelf-life remaining (45 mins vs 180 mins)",
    )

    expected = (
        "Donation D3 was considered after D1 because D1 had "
        "shorter shelf-life remaining (45 mins vs 180 mins) "
        "under the priority rule."
    )
    assert result == expected