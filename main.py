import argparse
import sys
from pathlib import Path

from fifo import schedule_fifo
from greedy import schedule_greedy
from metrics import compute_metrics, compare_strategies
from reports import generate_comparison_table, generate_explainability_log

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="RescueRoute",
        description="Explainable Food Rescue Matching & Evaluation Engine")

    parser.add_argument(
        "-d", "--data",
        type=str,
        default="data",
        help="Path to directory containing the data files (default: 'data')",
    )
    parser.add_argument(
        "-u", "--urgent-threshold",
        type=int,
        default=120,
        help="Remaining shelf life in minutes considered urgent (default: 120)",
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Display decision audit logs for all items rather than a sample",
    )

    return parser

### Temporary
from models import Donation, Recipient, Volunteer, Dataset
def get_mock_dataset() -> Dataset:
    """Fallback dataset to keep CLI fully functional while loader.py is pending."""
    donations = [
        Donation("D-101", "Downtown Bakery", "baked_goods", 15, 180, "Central", 10),
        Donation("D-102", "City Grocer", "produce", 25, 60, "North", 20),
        Donation("D-103", "Suburban Deli", "prepared", 20, 150, "North", 30),
        Donation("D-104", "Corner Cafe", "dairy", 50, 90, "East", 40),
    ]
    recipients = [
        Recipient("R-201", "Community Shelter", frozenset(["produce", "prepared"]), 40, "North", 300),
        Recipient("R-202", "Family Pantry", frozenset(["baked_goods"]), 30, "Central", 240),
    ]
    volunteers = [
        Volunteer("V-301", 30, "North", 0, 280, 2),
        Volunteer("V-302", 20, "Central", 0, 200, 1),
    ]
    return Dataset(donations=donations, recipients=recipients, volunteers=volunteers)
###

def main():
    parser = build_parser()
    args = parser.parse_args()

    # restore once loader.py is added
    # data_path = Path(args.data)
    # dataset = load_input_data(str(data_path))

    ### Temporary
    dataset  = get_mock_dataset()
    ###

    print(
        f">> Loaded dataset: {len(dataset.donations)} donations, "
        f"{len(dataset.recipients)} recipients, "
        f"{len(dataset.volunteers)} volunteers.\n"
    )

    print(">> Running Baseline: Approach A (FIFO)...")
    fifo_assignments = schedule_fifo(
        dataset.donations, dataset.recipients, dataset.volunteers
    )

    print(">> Running Strategy: Approach B (Greedy Urgency-First)...")
    greedy_assignments = schedule_greedy(
        dataset.donations, dataset.recipients, dataset.volunteers
    )

    print(">> Computing 8 core metrics and comparative deltas...\n")
    fifo_metrics = compute_metrics(
        dataset, fifo_assignments, urgent_threshold=args.urgent_threshold
    )
    greedy_metrics = compute_metrics(
        dataset, greedy_assignments, urgent_threshold=args.urgent_threshold
    )
    deltas = compare_strategies(fifo_metrics, greedy_metrics)

    print(generate_comparison_table(fifo_metrics, greedy_metrics, deltas))

    sample_limit = len(greedy_assignments) if args.verbose else 3
    print("\n" + generate_explainability_log(dataset, greedy_assignments, limit=sample_limit))


if __name__ == "__main__":
    main()