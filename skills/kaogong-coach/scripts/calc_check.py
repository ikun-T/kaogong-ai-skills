#!/usr/bin/env python3
"""Exact arithmetic checks for common aptitude-test quantities (stdlib only)."""
import argparse
import json
from fractions import Fraction


def number(value):
    text = str(value).strip()
    return Fraction(text[:-1]) / 100 if text.endswith('%') else Fraction(text)


def nonzero(value, label):
    if not value:
        raise ValueError(f'{label} must not be zero')
    return value


def growth_factor(rate):
    if rate <= -1:
        raise ValueError('growth rate must exceed -100% for this positive-base model')
    return 1 + rate


def calculate(operation, raw):
    x = {k: number(v) for k, v in raw.items()}
    if 'current' in x and x['current'] < 0:
        raise ValueError('current must be nonnegative for this quantity model')
    if operation == 'base':
        return x['current'] / growth_factor(x['rate'])
    if operation == 'increment':
        return x['current'] * x['rate'] / growth_factor(x['rate'])
    if operation == 'interval':
        return growth_factor(x['rate1']) * growth_factor(x['rate2']) - 1
    if operation == 'ratio-growth':
        if x['numerator_rate'] < -1:
            raise ValueError('numerator rate must be at least -100%')
        return (1 + x['numerator_rate']) / growth_factor(x['denominator_rate']) - 1
    if operation == 'share-difference':
        a, b = x['numerator_rate'], x['denominator_rate']
        growth_factor(b)
        if not 0 <= x['share'] <= 1:
            raise ValueError('current share must be between 0 and 1')
        prior_share = x['share'] * (1 + b) / growth_factor(a)
        if not 0 <= prior_share <= 1:
            raise ValueError('inputs imply an impossible prior share outside [0, 1]')
        return x['share'] * (a - b) / growth_factor(a)
    if operation == 'mixed':
        b1, b2 = x['base1'], x['base2']
        if min(b1, b2) < 0:
            raise ValueError('base weights must be nonnegative')
        if min(x['rate1'], x['rate2']) < -1:
            raise ValueError('component growth rates must be at least -100%')
        return (b1 * x['rate1'] + b2 * x['rate2']) / nonzero(b1 + b2, 'total base')
    if operation == 'compare':
        a = x['n1'] / nonzero(x['d1'], 'd1')
        b = x['n2'] / nonzero(x['d2'], 'd2')
        return Fraction((a > b) - (a < b))
    raise ValueError('unknown operation')


FIELDS = {
    'base': ('current', 'rate'), 'increment': ('current', 'rate'),
    'interval': ('rate1', 'rate2'),
    'ratio-growth': ('numerator_rate', 'denominator_rate'),
    'share-difference': ('share', 'numerator_rate', 'denominator_rate'),
    'mixed': ('base1', 'rate1', 'base2', 'rate2'),
    'compare': ('n1', 'd1', 'n2', 'd2'),
}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('operation', choices=FIELDS)
    parser.add_argument('values', nargs='+', help='key=value; percentages accept 20% or 0.2')
    args = parser.parse_args()
    try:
        pairs = [v.split('=', 1) for v in args.values]
        if any(len(p) != 2 for p in pairs):
            raise ValueError('all values must be key=value')
        raw = dict(pairs)
        if len(raw) != len(pairs) or set(raw) != set(FIELDS[args.operation]):
            raise ValueError('required unique fields: ' + ', '.join(FIELDS[args.operation]))
        result = calculate(args.operation, raw)
        unit = 'ratio' if args.operation in ('interval', 'ratio-growth', 'mixed') else 'input_units'
        if args.operation == 'share-difference':
            unit = 'share_fraction; multiply by 100 for percentage points'
        if args.operation == 'compare':
            unit = '-1: first smaller; 0: equal; 1: first larger'
        print(json.dumps({'operation': args.operation, 'exact': str(result),
                          'decimal': float(result), 'unit': unit}, ensure_ascii=False))
    except (ValueError, ZeroDivisionError, KeyError, OverflowError) as exc:
        parser.error(str(exc))


if __name__ == '__main__':
    main()
