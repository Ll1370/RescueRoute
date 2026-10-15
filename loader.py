import json
from models import Donation, Recipient, Volunteer, Dataset
from validation import validate_data

def load_data(file_path):
    try:
        with open(file_path, "r", encoding = "utf-8") as file:
            data = json.load(file)
    except json.JSONDecodeError as error:
        raise ValueError("Invalid JSON in " + str(file_path) + ": " + error.msg) from error
    except UnicodeDecodeError as error:
        raise ValueError("Input file must use UTF-8 text") from error

    validate_data(data)

    donations = []
    for record in data["donations"]:
        donation = Donation(
            donation_id = record["donation_id"],
            donor_name = record["donor_name"],
            food_type = record["food_type"],
            quantity = record["quantity"],
            expiry=record["expiry"],
            pickup_area = record["pickup_area"],
            ready_time = record["ready_time"]
        )
        donations.append(donation)

    recipients = []
    for record in data["recipients"]:
        recipient = Recipient(
            recipient_id = record["recipient_id"],
            organization_name = record["organization_name"],
            accepted_food_types = frozenset(record["accepted_food_types"]),
            capacity = record["capacity"],
            area = record["area"],
            closing_time = record["closing_time"]
        )
        recipients.append(recipient)

    volunteers = []
    for record in data["volunteers"]:
        volunteer = Volunteer(
            volunteer_id = record["volunteer_id"],
            vehicle_capacity = record["vehicle_capacity"],
            area = record["area"],
            available_from = record["available_from"],
            available_until = record["available_until"],
            maximum_pickups = record["maximum_pickups"]
        )
        volunteers.append(volunteer)
    return Dataset(donations, recipients, volunteers)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description = "Check and load RescueRoute JSON data")
    parser.add_argument("file_path", help = "Path to the JSON input file")
    args = parser.parse_args()
    try:
        dataset = load_data(args.file_path)
    except (ValueError, OSError) as error:
        parser.exit(1, "Error: " + str(error) + "\n")
    print("Loaded", len(dataset.donations), "donations")
    print("Loaded", len(dataset.recipients), "recipients")
    print("Loaded", len(dataset.volunteers), "volunteers")
