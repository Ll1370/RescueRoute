import unittest
from dataclasses import replace
from models import Donation, Recipient, Volunteer
from matching import SchedulerState, find_feasible_match


class MatchingTests(unittest.TestCase):
    def setUp(self):
        self.donation = Donation("D1", "Sample Cafe", "prepared", 10, 120, "north", 0)
        self.recipient = Recipient("R1", "Sample Shelter", frozenset({"prepared"}), 10, "north", 300)
        self.volunteer = Volunteer("V1", 10, "north", 0, 300, 2)

    def match(self, donation=None, recipient=None, volunteer=None, now=0):
        donation = donation or self.donation
        recipient = recipient or self.recipient
        volunteer = volunteer or self.volunteer
        state = SchedulerState([recipient], [volunteer], now)
        return find_feasible_match(donation, [recipient], [volunteer], state)

    def test_normal_match_at_minute_zero(self):
        r, v, time, reason = self.match()
        self.assertEqual((r.recipient_id, v.volunteer_id, time), ("R1", "V1", 0))
        self.assertTrue(reason)

    def test_incompatible_food(self):
        self.assertIsNone(self.match(donation=replace(self.donation, food_type="bakery"))[0])

    def test_capacity_limits(self):
        self.assertIsNone(self.match(recipient=replace(self.recipient, capacity=5))[0])
        self.assertIsNone(self.match(volunteer=replace(self.volunteer, vehicle_capacity=5))[0])

    def test_expiration_boundary(self):
        self.assertIsNotNone(self.match(now=119)[0])
        self.assertIsNone(self.match(now=120)[0])

    def test_time_windows(self):
        self.assertIsNone(self.match(recipient=replace(self.recipient, closing_time=0))[0])
        self.assertIsNone(self.match(volunteer=replace(self.volunteer, available_until=5), now=6)[0])
        result = self.match(donation=replace(self.donation, ready_time=20))
        self.assertEqual(result[2], 20)

    def test_different_area(self):
        self.assertIsNone(self.match(volunteer=replace(self.volunteer, area="south"))[0])

    def test_search_continues_after_bad_candidate(self):
        bad = replace(self.recipient, recipient_id="R0", capacity=0)
        state = SchedulerState([bad, self.recipient], [self.volunteer])
        result = find_feasible_match(self.donation, [bad, self.recipient], [self.volunteer], state)
        self.assertEqual(result[0].recipient_id, "R1")

    def test_commit_consumes_capacity_without_changing_model(self):
        state = SchedulerState([self.recipient], [self.volunteer])
        find_feasible_match(self.donation, [self.recipient], [self.volunteer], state)
        self.assertEqual(state.remaining_capacity["R1"], 10)
        state.commit(self.donation, self.recipient, self.volunteer)
        self.assertEqual(state.remaining_capacity["R1"], 0)
        self.assertEqual(state.pickups_used["V1"], 1)
        self.assertEqual(self.recipient.capacity, 10)
        self.assertIsNone(find_feasible_match(self.donation, [self.recipient], [self.volunteer], state)[0])

    def test_pickup_limit(self):
        r = replace(self.recipient, capacity=100)
        v = replace(self.volunteer, maximum_pickups=1)
        state = SchedulerState([r], [v])
        state.commit(self.donation, r, v)
        self.assertIsNone(find_feasible_match(self.donation, [r], [v], state)[0])

    def test_empty_resources_and_independent_runs(self):
        state = SchedulerState([], [])
        self.assertIsNone(find_feasible_match(self.donation, [], [], state)[0])
        state1 = SchedulerState([self.recipient], [self.volunteer])
        state2 = SchedulerState([self.recipient], [self.volunteer])
        state1.commit(self.donation, self.recipient, self.volunteer)
        self.assertEqual(state2.remaining_capacity["R1"], 10)


if __name__ == "__main__":
    unittest.main()
