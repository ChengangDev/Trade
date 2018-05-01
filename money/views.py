from django.shortcuts import render
from django.http import HttpResponse, JsonResponse, Http404
from django.template import loader
from django.utils import timezone
import pandas as pd
import logging as lg
from zsfetch.progdb import moneydb

logger = lg.getLogger(__name__)
logger.setLevel(lg.INFO)

_modb = moneydb.MoneyDB()


def index(request):
    template = loader.get_template('money/index.html')
    context = {
        'hello': 'world',
    }
    return HttpResponse(template.render(context, request))


def share(request):
    if request.method == 'GET':
        df = _get_money_share()
        return JsonResponse(df.to_dict(orient='split'))
    else:
        raise Http404

_share_columns = ['SEC_NAME', 'TOT_VOL',
                  moneydb.COL_MILLISECONDS,
                  moneydb.COL_TRADE_DATE,
                  moneydb.COL_MONEY_FUND_INDEX
                  ]


def _get_money_share():
    singles = [
        '511990',  # hbty
        '511880',  # yhrl
        '511660',  # jxty
    ]

    df = _modb.get_share([])  # get all
    logger.debug("raw share:\n{}".format(df.head(1)))
    df = df.drop(['_id', 'ETF_TYPE', 'NUM', 'SEC_CODE', 'STAT_DATE'], axis=1)
    logger.debug("trim cols share:\n{}".format(df.head(1)))
    df.sort_values(by=[moneydb.COL_MILLISECONDS])  # for map reduce
    logger.debug("share:\n{}".format(df.head(1)))

    # for float value
    def dict_update(row):
        d = {}
        d.update(row)
        d['TOT_VOL'] = float(d['TOT_VOL'])
        return d
    dict_list = []
    cur = -1
    others_dict = {}
    for _, row in df.iterrows():
        fund_index = row[moneydb.COL_MONEY_FUND_INDEX]
        if fund_index in singles:
            single_dict = dict_update(row)
            dict_list.append(single_dict)
            continue

        # map reduce to sum others
        milliseconds = row[moneydb.COL_MILLISECONDS]
        if cur != milliseconds:  # flag has changed
            if cur != 0:  # not the first, previous exist
                dict_list.append(others_dict)  # append previous sum
            others_dict = dict_update(row)  # new a dict and init with current row
            cur = milliseconds  # keep flag same
        else:  # same flag
            others_dict['TOT_VOL'] += float(row['TOT_VOL'])  # sum

    if bool(others_dict):
        dict_list.append(others_dict)  # do not forget the last one

    agg_df = pd.DataFrame(dict_list)
    # logger.debug("agg share:\n{}".format(agg_df.tail(12)))
    return agg_df

