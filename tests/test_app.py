import unittest
from streamlit.testing.v1 import AppTest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

class AppTests(unittest.TestCase):
    def test_defaults_controls_and_fixed_baselines(self):
        app=AppTest.from_file(str(ROOT/'app.py'),default_timeout=20).run()
        self.assertEqual(len(app.exception),0)
        frame=app.dataframe[0].value
        candidate=frame[frame.Portfolio=='Constrained portfolio'].iloc[0]
        self.assertEqual(candidate.SGOV,'85.00%')
        self.assertEqual(candidate['Working mandate'],'PASS')
        benchmark=frame[frame.Portfolio=='Policy benchmark'].iloc[0]
        self.assertEqual(benchmark.SGOV,'100.00%')
        self.assertEqual(benchmark['Working mandate'],'FAIL')
        self.assertEqual(benchmark['Mandate violations'],'net estimated return below 5.00%')
        fixed=frame[frame.Portfolio!='Constrained portfolio'][['Portfolio','SGOV','IEF','LQD','VOO']].reset_index(drop=True)
        app.sidebar.toggle[0].set_value(True).run()
        self.assertEqual(len(app.exception),0)
        frame=app.dataframe[0].value
        self.assertTrue(fixed.equals(frame[frame.Portfolio!='Constrained portfolio'][['Portfolio','SGOV','IEF','LQD','VOO']].reset_index(drop=True)))
        app.sidebar.number_input[0].set_value(100.0).run()
        self.assertEqual(len(app.exception),0)
        self.assertTrue(any('no mix meets' in e.value for e in app.error))

if __name__=='__main__':unittest.main()
