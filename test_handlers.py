import json
import unittest

from handlers import (
    _parse_llm_json,
    _sweep_statutory,
    _sweep_statutory_string,
    _identity_leaks,
)


class TestParseLlmJson(unittest.TestCase):
    def test_plain_object(self):
        self.assertEqual(_parse_llm_json('{"a": 1}'), {'a': 1})

    def test_fenced_json(self):
        raw = '```json\n{"name": "[~Pat~]"}\n```'
        self.assertEqual(_parse_llm_json(raw), {'name': '[~Pat~]'})

    def test_commentary_around_object(self):
        raw = 'Here you go:\n{"ssn": "[b(Ex.3)]"}\nDone.'
        self.assertEqual(_parse_llm_json(raw), {'ssn': '[b(Ex.3)]'})

    def test_unquoted_aggr_marker(self):
        raw = '{"city": [~Portland~]}'
        self.assertEqual(_parse_llm_json(raw), {'city': '[~Portland~]'})


class TestStatutorySweep(unittest.TestCase):
    def test_ssn_in_string(self):
        self.assertEqual(
            _sweep_statutory_string('SSN 412-67-8234 remains'),
            'SSN [b(Ex.3)] remains',
        )

    def test_ssn_field(self):
        out = _sweep_statutory({'ssn': '412-67-8234', 'name': 'Ada Lovelace'})
        self.assertEqual(out['ssn'], '[b(Ex.3)]')
        self.assertEqual(out['name'], 'Ada Lovelace')

    def test_clearance_field(self):
        out = _sweep_statutory({'clearance_level': 'TS/SCI'})
        self.assertEqual(out['clearance_level'], '[b(Ex.1)]')

    def test_nested_records(self):
        out = _sweep_statutory({
            'records': [
                {'ssn': '529-83-1047', 'classification': 'TOP SECRET // HCS // NOFORN'},
            ]
        })
        self.assertEqual(out['records'][0]['ssn'], '[b(Ex.3)]')
        self.assertEqual(out['records'][0]['classification'], '[b(Ex.1)]')

    def test_already_marked_left_alone(self):
        out = _sweep_statutory({'ssn': '[b(Ex.3)]'})
        self.assertEqual(out['ssn'], '[b(Ex.3)]')


class TestDateCloak(unittest.TestCase):
    def test_shift_oct_6_1994(self):
        from handlers import _shift_date_string
        out = _shift_date_string('Oct 6 1994')
        self.assertIsNotNone(out)
        self.assertNotEqual(out.lower(), 'oct 6 1994')
        self.assertRegex(out, r'1995|1996')

    def test_noop_marker_replaced(self):
        from handlers import _fix_noop_aggr_markers
        original = 'on Oct 6 1994, the day after'
        redacted = 'on [~Oct 6 1994~], the day after'
        out = _fix_noop_aggr_markers(original, redacted)
        self.assertNotIn('[~Oct 6 1994~]', out)
        self.assertIn('[~', out)

    def test_leftover_bare_date(self):
        from handlers import _cloak_leftover_dates
        original = 'on Oct 6 1994 I left Helena, MT'
        redacted = 'on Oct 6 1994 I left Helena, MT'
        out = _cloak_leftover_dates(original, redacted, wrap=True)
        self.assertNotIn('Oct 6 1994', out)


class TestCommentaryStrip(unittest.TestCase):
    def test_drops_exemption_walkthrough(self):
        from handlers import _strip_leading_commentary
        original = 'Participant Sandra R. Okonkwo, SSN 412-77-3920'
        leaked = (
            "We need to apply redactions.\n"
            "Tier 1: SSNs are Ex.3. Not present: clearance.\n\n"
            + original
        )
        self.assertEqual(_strip_leading_commentary(leaked, original), original)


class TestIdentityLeaks(unittest.TestCase):
    def test_detects_leftover_ssn(self):
        orig = {'ssn': '412-67-8234', 'name': 'Marcus J. Thompson'}
        red = {'ssn': '412-67-8234', 'name': 'David Ellison'}
        leaks = _identity_leaks(orig, red, 'standard')
        self.assertTrue(any('412-67-8234' in x for x in leaks))

    def test_detects_unchanged_name(self):
        orig = {'name': 'Marcus J. Thompson'}
        red = {'name': 'Marcus J. Thompson'}
        leaks = _identity_leaks(orig, red, 'standard')
        self.assertTrue(any('Marcus' in x for x in leaks))

    def test_reduced_allows_names(self):
        orig = {'name': 'Marcus J. Thompson', 'ssn': '412-67-8234'}
        red = {'name': 'Marcus J. Thompson', 'ssn': '[b(Ex.3)]'}
        leaks = _identity_leaks(orig, red, 'reduced')
        self.assertEqual(leaks, [])


if __name__ == '__main__':
    unittest.main()
