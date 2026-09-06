"""Behavior checks using independent arithmetic and synthetic subtitle inputs."""
import importlib.util
import unittest
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


calc = module('calc', 'skills/kaogong-coach/scripts/calc_check.py')
subs = module('subs', 'skills/kaogong-source-distiller/scripts/normalize_transcript.py')
catalog = module('catalog', 'scripts/validate_catalog.py')


class Arithmetic(unittest.TestCase):
    def test_growth_recovers_independently_constructed_base(self):
        for base in [50, 100, 375]:
            for rate in ['-20%', '0%', '10%', '25%']:
                r = calc.number(rate)
                current = Fraction(base) * (1 + r)
                args = {'current': str(current), 'rate': rate}
                self.assertEqual(calc.calculate('base', args), base)
                self.assertEqual(calc.calculate('increment', args), current - base)

    def test_share_difference_vs_two_reconstructed_periods(self):
        # Base: 25 / 100. Current: 30 / 110. Direct difference = 1/44.
        self.assertEqual(calc.calculate('share-difference', {
            'share': '3/11', 'numerator_rate': '20%', 'denominator_rate': '10%'}), Fraction(3, 11) - Fraction(1, 4))

    def test_mixed_growth_direct_totals(self):
        # 100->110 and 300->390: total 400->500, or 25%.
        self.assertEqual(calc.calculate('mixed', {'base1': '100', 'rate1': '10%', 'base2': '300', 'rate2': '30%'}), Fraction(1, 4))
        self.assertEqual(calc.calculate('mixed', {'base1': '100', 'rate1': '-100%', 'base2': '100', 'rate2': '0%'}), Fraction(-1, 2))

    def test_inverse_growth_is_not_cancelled(self):
        self.assertEqual(calc.calculate('interval', {'rate1': '20%', 'rate2': '-20%'}), Fraction(-1, 25))

    def test_ratio_growth(self):
        self.assertEqual(calc.calculate('ratio-growth', {'numerator_rate': '20%', 'denominator_rate': '10%'}), Fraction(1, 11))
        self.assertEqual(calc.calculate('ratio-growth', {'numerator_rate': '-100%', 'denominator_rate': '0%'}), -1)

    def test_invalid_domain(self):
        bad = [('base', {'current': '0', 'rate': '-100%'}),
               ('compare', {'n1': '1', 'd1': '0', 'n2': '1', 'd2': '2'}),
               ('share-difference', {'share': '70%', 'numerator_rate': '-50%', 'denominator_rate': '0%'}),
               ('base', {'current': '-1', 'rate': '20%'})]
        for op, values in bad:
            with self.subTest(op=op, values=values), self.assertRaises(ValueError):
                calc.calculate(op, values)

    def test_compare_sign(self):
        self.assertEqual(calc.calculate('compare', {'n1': '1', 'd1': '-2', 'n2': '1', 'd2': '2'}), -1)


class Subtitles(unittest.TestCase):
    def test_srt_unicode_multiline(self):
        cues = subs.normalize('1\n00:00:01,200 --> 00:00:03,500\n原创练习\n第二行\n\n2\n00:00:04,000 --> 00:00:05,000\n增长率\n', '.srt')
        self.assertEqual(len(cues), 2)
        self.assertEqual(cues[0], {'start': 1.2, 'end': 3.5, 'text': '原创练习\n第二行'})

    def test_vtt_settings_and_tags(self):
        cues = subs.normalize('WEBVTT\n\ncue-1\n00:01.000 --> 00:02.000 align:start\n<b>A &amp; B</b>\n', '.vtt')
        self.assertEqual(cues[0]['text'], 'A & B')

    def test_bilibili_and_json3(self):
        self.assertEqual(subs.normalize('{"body":[{"from":2,"to":3,"content":"自编例子"}]}', '.json')[0]['start'], 2)
        cue = subs.normalize('{"events":[{"tStartMs":1000,"segs":[{"utf8":"自编"},{"utf8":"例子"}]}]}', '.json')[0]
        self.assertIsNone(cue['end'])
        self.assertEqual(cue['text'], '自编例子')

    def test_reject_bad_interval_and_unlocated_text(self):
        for raw, suffix in [('只有普通文本', '.txt'), ('{"body":[{"from":3,"to":2,"content":"x"}]}', '.json')]:
            with self.assertRaises(ValueError):
                subs.normalize(raw, suffix)


class Evidence(unittest.TestCase):
    def test_discovery_cannot_be_promoted(self):
        source = {'id': 's', 'platform': 'bilibili', 'url': 'https://www.bilibili.com/video/test/', 'title': 'test', 'uploader': 'test', 'identity_status': 'unknown', 'evidence_level': 'search_only', 'read_scope': 'title', 'accessed_at': '2026-09-06', 'limitations': ['unread']}
        method = {'id': 'm', 'name': 'test', 'module': 'test', 'status': 'source_verified', 'attribution': 'test', 'triggers': ['x'], 'steps': ['x'], 'limits': ['x'], 'example': {'answer': 'x'}, 'evidence': [{'source_id': 's', 'locator': 'title', 'support': 'title'}]}
        self.assertTrue(any('unsupported promotion' in e for e in catalog.check([source], [method], root=ROOT / 'tests')))


if __name__ == '__main__':
    unittest.main()
