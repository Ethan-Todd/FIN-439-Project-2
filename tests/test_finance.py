import csv
import hashlib
import io
import json
import math
from pathlib import Path
import unittest
from unittest.mock import patch
import numpy as np
import portfolio as p
import analysis as a
import signal_monitor as sm

class FinanceTests(unittest.TestCase):
    def setUp(self):
        self.s, self.c = a.load_prices()

    def test_known_answer_and_independent_covariance(self):
        result = a.optimize(self.s, self.c)
        self.assertEqual(result['weights'], dict(zip(p.UNIVERSE, [.85, 0, 0, .15])))
        prices = np.loadtxt(a.ROOT / 'prices.csv', delimiter=',', skiprows=1, usecols=(1,2,3,4))
        returns = prices[1:] / prices[:-1] - 1
        weights = np.array([.85,0,0,.15])
        self.assertAlmostEqual(result['net_estimated_return'], float(returns.mean(0) @ weights * 12), places=12)
        self.assertAlmostEqual(result['volatility'], float(np.std(returns @ weights, ddof=1) * math.sqrt(12)), places=12)
        # Independent grid search using direct sample returns instead of engine covariance.
        best = min((float(np.std(returns @ w, ddof=1) * math.sqrt(12)), tuple(w))
                   for i in range(2,21) for j in range(21-i) for k in range(21-i-j)
                   if (w := np.array([i,j,k,20-i-j-k])/20) @ returns.mean(0)*12 >= .05-1e-12)
        self.assertAlmostEqual(result['volatility'], best[0], places=12)

    def test_analytic_two_asset_risk(self):
        sleeves = {'A': {'expected_return': .04, 'volatility': .1}, 'B': {'expected_return': .08, 'volatility': .2}}
        corr = {'A': {'A':1, 'B':0}, 'B': {'A':0, 'B':1}}
        p.validate_inputs(sleeves,corr)
        self.assertAlmostEqual(p.portfolio_volatility({'A':.5,'B':.5}, p.build_covariance_matrix(sleeves,corr)), math.sqrt(.0125))
        self.assertAlmostEqual(p.portfolio_expected_return({'A':.5,'B':.5},sleeves),.06)

    def test_bad_matrices(self):
        for matrix in [np.zeros((4,4)), np.array([[1,.9,.9,0],[.9,1,-.9,0],[.9,-.9,1,0],[0,0,0,1]]),
                       np.full((4,4),float('nan'))]:
            c={t:dict(zip(p.UNIVERSE,matrix[i])) for i,t in enumerate(p.UNIVERSE)}
            with self.assertRaises(ValueError):p.validate_inputs(self.s,c)
        c={t:dict(v) for t,v in self.c.items()};c['SGOV']['IEF']=.999
        with self.assertRaises(ValueError):p.validate_inputs(self.s,c)

    def test_invalid_csv(self):
        for text in ['date,A\n2020-01-01,100\n2020-01-02,101\n2022-01-01,103\n',
                     'date,A\n2020-01-01,100\n2020-03-01,101\n2020-04-01,103\n',
                     'date,A\n2020-01-01,100\n2020-02-01,nan\n2020-03-01,103\n',
                     'date,A\n2020-01-01,100\n2020-02-01,-1\n2020-03-01,103\n',
                     'date,A\n2020-01-01,100\n2020-02-01,100\n2020-03-01,100\n']:
            with self.assertRaises(ValueError):p.estimate_from_price_csv(io.StringIO(text))
        with self.assertRaisesRegex(ValueError,'37 monthly'):
            p.estimate_from_price_csv(io.StringIO('date,A\n2020-01-01,100\n2020-02-01,101\n2020-03-01,103\n'),True)

    def test_policy_baseline_and_weights(self):
        with self.assertRaises(ValueError):p.benchmark_weights(self.s)
        with self.assertRaises(ValueError):p.benchmark_weights(self.s,{t:0 for t in p.UNIVERSE})
        with self.assertRaises(ValueError):p.validate_weights({'VOO':1},self.s)
        fixed=a.fixed_baselines(self.s)
        self.assertEqual(fixed['Policy benchmark'],dict(zip(p.UNIVERSE,[1,0,0,0])))
        benchmark=a.evaluate(fixed['Policy benchmark'],self.s,self.c)
        self.assertAlmostEqual(benchmark['net_estimated_return'],.03715074894092623)
        self.assertEqual(benchmark['reserve_weight'],1)
        self.assertEqual(benchmark['verdict'],'FAIL')
        self.assertEqual(benchmark['violated_rules'],['net estimated return below 5.00%'])
        self.assertEqual(len(fixed),3)
        changed={t:{**v,'expected_return':v['expected_return']+.02} for t,v in self.s.items()}
        a.optimize(changed,self.c,.01,.06,.3)
        self.assertEqual(fixed,a.fixed_baselines(self.s))
        self.assertEqual(a.evaluate(p.equal_weights(self.s),self.s,self.c)['verdict'],'FAIL')

    def test_window_and_failure(self):
        s,c=a.load_prices(last_36=True)
        self.assertEqual(a.optimize(s,c)['weights'],dict(zip(p.UNIVERSE,[.95,0,0,.05])))
        self.assertIsNone(a.optimize(self.s,self.c,objective=1))
        self.assertIsNone(a.optimize(self.s,self.c,minimum=1))
        with self.assertRaises(ValueError):a.optimize(self.s,self.c,cost=-.01)
        with self.assertRaises(ValueError):a.optimize(self.s,self.c,objective=float('nan'))

    def test_cost_accounting_and_sensitivity(self):
        report=a.build_report()
        self.assertEqual({r['scenario']['dimension'] for r in report['sensitivity']}, {'reference','estimates','window','costs','constraints'})
        reference=report['candidate']['weights']
        gross=a.evaluate(reference,self.s,self.c)
        costly=a.evaluate(reference,self.s,self.c,.01)
        self.assertAlmostEqual(gross['net_estimated_return']-costly['net_estimated_return'],.01)
        self.assertEqual(costly['verdict'],'FAIL')
        self.assertEqual(report,a.build_report())

    def test_retained_prices_match_sources(self):
        from datetime import datetime,timezone
        rows=list(csv.DictReader(io.StringIO((a.ROOT/'prices.csv').read_text())))
        self.assertEqual(hashlib.sha256((a.ROOT/'prices.csv').read_bytes()).hexdigest(),'600b080f99353ef49334eeb0a25af10586b89659692c4ee7a08de420fbbac961')
        for ticker in p.UNIVERSE:
            source=json.loads((a.ROOT/'price_sources'/f'yahoo_{ticker}_monthly_2021-09_to_2026-09.json').read_text())['chart']['result'][0]
            values={datetime.fromtimestamp(t,timezone.utc).date().isoformat():v for t,v in zip(source['timestamp'],source['indicators']['adjclose'][0]['adjclose'])}
            for row in rows:self.assertLessEqual(abs(float(row[ticker])-values[row['date']]),.0000005)

    def test_signal_rule_and_fail_closed(self):
        self.assertEqual(sm.evaluate_monitor(3,.04)['status'],'REVIEW')
        self.assertEqual(sm.evaluate_monitor(5,.04)['status'],'NO YIELD SHORTFALL FLAG')
        with patch.object(sm,'ROOT',Path('/nonexistent-project2-test')):
            self.assertEqual(sm.signal_status(.04)['status'],'QUARANTINE')
        with self.assertRaises(ValueError):sm.parse_observations('DATE,WRONG\n2026-01-01,4\n')

    def test_archived_signal_and_tamper(self):
        import tempfile
        import shutil
        status=sm.signal_status(self.s['SGOV']['expected_return'])
        self.assertEqual(status['observation_date'],'2026-10-29')
        self.assertEqual(status['yield_percent'],4.18)
        self.assertEqual(status['status'],'NO YIELD SHORTFALL FLAG')
        with tempfile.TemporaryDirectory() as directory:
            folder=Path(directory)/'signal_sources'/sm.CUTOFF
            shutil.copytree(sm.ROOT/'signal_sources'/sm.CUTOFF,folder)
            with (folder/'vintage.csv').open('a') as f:f.write('2026-11-01,0\n')
            with patch.object(sm,'ROOT',Path(directory)):
                result=sm.signal_status(.04)
                self.assertEqual(result['status'],'QUARANTINE')
                self.assertIn('checksum',result['reason'])

    def test_publication_gate_known_answer(self):
        import asof
        panel,_=asof.apply_as_of_rules(asof.ROWS,asof.parse_date(asof.DECISION_DATE))
        self.assertEqual([r['row'] for r in panel],[1,4,5,6,9,12])
        self.assertTrue(all(r['published']<=asof.DECISION_DATE for r in panel))

if __name__=='__main__':unittest.main()
