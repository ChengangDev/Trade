from django.test import TestCase
from option import views
import logging as lg


dbgFormatter = "%(levelname)s:%(filename)s:%(lineno)s:%(funcName)s() -- %(message)s"
lg.basicConfig(level=lg.DEBUG, format=dbgFormatter)
views.optiondb.logger.setLevel(lg.DEBUG)
views.logger.setLevel(lg.DEBUG)


# Create your tests here.
class OptionTest(TestCase):
    def test_view_get_grids_of_trading_option(self):
        grids = views.get_grids_of_trading_option()
        lg.info("\n{}".format(grids.head(2)))

    def test_view_get_option_history_ohlc(self):

        df = views.get_option_history_ohlc('10001115')
        self.assertEqual(len(df.columns), len(views._ohlc_columns))
        for i in range(len(views._ohlc_columns)):
            self.assertEqual(views._ohlc_columns[i], df.columns[i])
        lg.info("\n{}".format(df.head(2)))

