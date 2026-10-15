class SchedulerState:
    def __init__(self, recipients, volunteers, current_time=0):
        self.current_time = current_time
        self.remaining_capacity = {}
        self.pickups_used = {}

        for recipient in recipients:
            self.remaining_capacity[recipient.recipient_id] = recipient.capacity
        for volunteer in volunteers:
            self.pickups_used[volunteer.volunteer_id] = 0

    def commit(self, donation, recipient, volunteer):
        recipient_id = recipient.recipient_id
        volunteer_id = volunteer.volunteer_id
        self.remaining_capacity[recipient_id] -= donation.quantity
        self.pickups_used[volunteer_id] += 1


def check_pair(donation, recipient, volunteer, state):
    if donation.food_type not in recipient.accepted_food_types:
        return None, "the recipient does not accept this type of food"

    remaining = state.remaining_capacity[recipient.recipient_id]
    if donation.quantity > remaining:
        return None, "the recipient does not have enough capacity"

    if donation.quantity > volunteer.vehicle_capacity:
        return None, "the volunteer's vehicle does not have enough capacity"

    used = state.pickups_used[volunteer.volunteer_id]
    if used >= volunteer.maximum_pickups:
        return None, "the volunteer has already reached their maximum number of pickups"

    if donation.pickup_area != recipient.area:
        return None, "the recipient is in a different area"
    if donation.pickup_area != volunteer.area:
        return None, "the volunteer is in a different area"

    scheduled_time = max(
        state.current_time, donation.ready_time, volunteer.available_from
    )
    if scheduled_time >= donation.expiry:
        return None, "the donation expires before or at the possible pickup time"
    if scheduled_time >= recipient.closing_time:
        return None, "the recipient is closed at the possible delivery time"
    if scheduled_time >= volunteer.available_until:
        return None, "the volunteer is no longer available at the possible pickup time"

    reason = (
        "the recipient accepts the food, capacity is available, "
        "the volunteer can carry it, and area and time requirements are met"
    )
    return scheduled_time, reason


def find_feasible_match(donation, recipients, volunteers, state):
    if not recipients:
        return None, None, None, "no recipients were provided"
    if not volunteers:
        return None, None, None, "no volunteers were provided"

    reasons = []
    seen_reasons = set()
    for recipient in recipients:
        for volunteer in volunteers:
            scheduled_time, reason = check_pair(
                donation, recipient, volunteer, state
            )
            if scheduled_time is not None:
                return recipient, volunteer, scheduled_time, reason
            if reason not in seen_reasons:
                seen_reasons.add(reason)
                reasons.append(reason)
    reason = "no feasible pair was found; reasons encountered: "
    reason += "; ".join(reasons)
    return None, None, None, reason
