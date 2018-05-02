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

_share_columns = [moneydb.COL_MILLISECONDS,
                  'popular', 'others'
                  ]


def _get_money_share():
    popular_fund = [
        '511990',  # hbty
        '511880',  # yhrl
        # '511660',  # jxty
    ]

    df = _modb.get_share([])  # get all
    logger.debug("raw share:{}\n{}".format(len(df.index), df.head(1)))
    df = df.drop(['_id', 'ETF_TYPE', 'NUM', 'SEC_CODE', 'STAT_DATE'], axis=1)
    logger.debug("trim cols share:{}\n{}".format(len(df.index), df.head(1)))
    # df.sort_values(by=[moneydb.COL_MILLISECONDS])  # for map reduce
    # logger.debug("share:\n{}".format(df.head(1)))

    others_dict = {}
    popular_dict = {}
    for _, row in df.iterrows():
        fund_index = row[moneydb.COL_MONEY_FUND_INDEX]
        milliseconds = row[moneydb.COL_MILLISECONDS]
        if fund_index in popular_fund:
            if milliseconds not in popular_dict:
                popular_dict[milliseconds] = float(row['TOT_VOL'])
            else:
                popular_dict[milliseconds] += float(row['TOT_VOL'])
        else:
            if milliseconds not in others_dict:
                others_dict[milliseconds] = float(row['TOT_VOL'])
            else:
                others_dict[milliseconds] += float(row['TOT_VOL'])
    # logger.debug("popular:\n{}".format(len(popular_dict)))
    # logger.debug("others:\n{}".format(len(others_dict)))

    agg_list = []
    for milliseconds in popular_dict:
        agg_dict = {moneydb.COL_MILLISECONDS: milliseconds,
                    'popular': popular_dict[milliseconds]}
        # logger.debug("agg_dict:{}".format(agg_dict))
        if milliseconds in others_dict:
            agg_dict['others'] = others_dict[milliseconds]
        else:
            agg_dict['others'] = 0.0
        agg_list.append(agg_dict)

    agg_df = pd.DataFrame(agg_list, columns=_share_columns)
    agg_df = agg_df.sort_values(by=[moneydb.COL_MILLISECONDS])
    agg_df = agg_df.reset_index(drop=True)
    return agg_df

