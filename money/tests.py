from django.test import TestCase
import logging as lg
from money import views
from zsfetch import util

dbgFormatter = "%(levelname)s:%(filename)s:%(lineno)s:%(funcName)s() -- %(message)s"
lg.basicConfig(level=lg.DEBUG, format=dbgFormatter)
views.moneydb.logger.setLevel(lg.DEBUG)
views.logger.setLevel(lg.DEBUG)


class MoneyTest(TestCase):

    def test_view_get_money_share(self):

        df = views._get_money_share()
        self.assertEqual(len(df.columns), len(views._share_columns))
        util.check_same_columns_or_raise(df.columns, views._share_columns)
        lg.info("\n{}".format(df.tail(12)))

