def check_text(value, label):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{label} must be a non-empty string")
    if value != value.strip():
        raise ValueError(f"{label} must not have leading or trailing whitespace")

def check_number(value, label, minimum=0):
    if type(value) is not int or value < minimum:
        raise ValueError(f"{label} must be an integer >= {minimum}")

def check_fields(record, required, label):
    if not isinstance(record, dict):
        raise ValueError(f"{label} must be a dictionary")
    for name in required:
        if name not in record:
            raise ValueError(f"{label} is missing required field '{name}'")
    for name in record:
        if name not in required:
            raise ValueError(f"{label} has an unknown field: {name}")

def check_unique_ids(records, id_field, label):
    seen_ids = set()
    for record in records:
        record_id = record[id_field]
        if record_id in seen_ids:
            raise ValueError(f"{label} has duplicate ID: {record_id}")
        seen_ids.add(record_id)

def validate_donations(records):
    fields = ["donation_id", "donor_name", "food_type", "quantity", "expiry", "pickup_area", "ready_time"]
    for index, record in enumerate(records):
        label = "donations[" + str(index) + "]"
        check_fields(record, fields, label)
        for name in ["donation_id", "donor_name", "food_type", "pickup_area"]:
            check_text(record[name], label + "." + name)
        check_number(record["quantity"], label + ".quantity", minimum=1)
        check_number(record["expiry"], label + ".expiry")
        check_number(record["ready_time"], label + ".ready_time")
        if record["expiry"] <= record["ready_time"]:
            raise ValueError(f"{label} : expiry must be after the ready_time")
    check_unique_ids(records, "donation_id", "donations")

def validate_recipients(records):
    fields = ["recipient_id", "organization_name", "accepted_food_types",
              "capacity", "area", "closing_time"]
    for index, record in enumerate(records):
        label = "recipients[" + str(index) + "]"
        check_fields(record, fields, label)
        for name in ["recipient_id", "organization_name", "area"]:
            check_text(record[name], label + "." + name)
        check_number(record["capacity"], label + ".capacity")
        check_number(record["closing_time"], label + ".closing_time")
        food_types = record["accepted_food_types"]
        if not isinstance(food_types, list):
            raise ValueError(label + ".accepted_food_types must be a list")
        seen_types = set()
        for food_type in food_types:
            check_text(food_type, label + ".accepted_food_types item")
            if food_type in seen_types:
                raise ValueError(label + ": repeated accepted food type " + food_type)
            seen_types.add(food_type)
    check_unique_ids(records, "recipient_id", "recipients")


def validate_volunteers(records):
    fields = ["volunteer_id", "vehicle_capacity", "area", "available_from",
              "available_until", "maximum_pickups"]
    for index, record in enumerate(records):
        label = "volunteers[" + str(index) + "]"
        check_fields(record, fields, label)
        for name in ["volunteer_id", "area"]:
            check_text(record[name], label + "." + name)
        for name in ["vehicle_capacity", "available_from", "available_until", "maximum_pickups"]:
            check_number(record[name], label + "." + name)
        if record["available_until"] < record["available_from"]:
            raise ValueError(label + ": available_until must not be before available_from")
    check_unique_ids(records, "volunteer_id", "volunteers")


def validate_data(data):
    """Return normally for valid input; raise ValueError for invalid input."""
    groups = ["donations", "recipients", "volunteers"]
    check_fields(data, groups, "dataset")
    for group in groups:
        if not isinstance(data[group], list):
            raise ValueError(group + " must be a list")
    validate_donations(data["donations"])
    validate_recipients(data["recipients"])
    validate_volunteers(data["volunteers"])
