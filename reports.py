from typing import List, Dict, Any
from models import Dataset, Assignment
from explain import (
    format_assigned_reason,
    format_unassigned_reason,
    format_deferred_reason,
)


def generate_comparison_table(
    fifo_metrics: Dict[str, Any], 
    greedy_metrics: Dict[str, Any], 
    deltas: Dict[str, Any]
) -> str:
    """Formats side-by-side metric comparison into a clean terminal/markdown table."""
    lines = []
    lines.append("=" * 72)
    lines.append(f"{'METRIC':<36} {'FIFO':<10} {'GREEDY':<10} {'DELTA':<10}")
    lines.append("-" * 72)

    for metric_name, f_val in fifo_metrics.items():
        g_val = greedy_metrics.get(metric_name, 0)
        d_val = deltas.get(f"delta_{metric_name}", g_val - f_val if isinstance(f_val, (int, float)) else "-")

        if "rate" in metric_name or "utilization" in metric_name:
            lines.append(f"{metric_name:<36} {f_val:>8.1f}% {g_val:>8.1f}% {d_val:>+8.1f}%")
        else:
            lines.append(f"{metric_name:<36} {f_val:>9} {g_val:>9} {d_val:>+9}")

    lines.append("=" * 72)
    return "\n".join(lines)


def generate_explainability_log(
    dataset: Dataset, 
    assignments: List[Assignment], 
    limit: int = 5
) -> str:
    """Formats decision explanations for a subset or full list of assignments."""
    lines = [f"--- Decision Explanations Sample (First {limit}) ---"]
    donation_lookup = {d.donation_id: d for d in dataset.donations}

    for a in assignments[:limit]:
        d = donation_lookup.get(a.donation_id)
        if a.status == "assigned":
            shelf_life = (d.expiry - a.scheduled_time) if (d and a.scheduled_time is not None) else 0
            food_type = d.food_type if d else "items"
            qty = d.quantity if d else 0

            lines.append(
                format_assigned_reason(
                    donation_id=a.donation_id,
                    recipient_name=a.recipient_id or "Recipient",
                    volunteer_id=a.volunteer_id or "Volunteer",
                    shelf_life_remaining=shelf_life,
                    food_type=food_type,
                    quantity=qty,
                )
            )
        elif a.status == "unassigned":
            lines.append(
                format_unassigned_reason(
                    donation_id=a.donation_id,
                    primary_blocker=a.decision_reason or "No compatible recipient or volunteer available",
                )
            )
        elif a.status == "deferred":
            lines.append(
                format_deferred_reason(
                    donation_id=a.donation_id,
                    prioritized_donation_id="Urgent Donation",
                    rule_reason=a.decision_reason or "Lower urgency score",
                )
            )
            
    lines.append("-" * 50)
    return "\n".join(lines)


def export_report_to_file(
    filepath: str,
    fifo_metrics: Dict[str, Any],
    greedy_metrics: Dict[str, Any],
    deltas: Dict[str, Any],
    dataset: Dataset,
    greedy_assignments: List[Assignment]
) -> None:
    """Writes the full evaluation report and audit trace to a file."""
    table_text = generate_comparison_table(fifo_metrics, greedy_metrics, deltas)
    audit_text = generate_explainability_log(dataset, greedy_assignments, limit=len(greedy_assignments))

    content = f"# RescueRoute Strategy Comparison Report\n\n{table_text}\n\n{audit_text}\n"

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)