
from django.http import HttpResponse, JsonResponse, Http404
from django.template import loader
from django.utils import timezone
import pandas as pd
import logging as lg
from zsfetch.progdb import optiondb

logger = lg.getLogger(__name__)
logger.setLevel(lg.WARNING)

_opdb = optiondb.OptionDB()


def index(request):
    template = loader.get_template('option/index.html')
    context = {
        'hello': 'world',
    }
    return HttpResponse(template.render(context, request))


def grids(request):
    if request.method == 'GET':
        df = get_grids_of_trading_option()
        return JsonResponse(df.to_dict(orient='split'))
    else:
        raise Http404()


def dayline(request):
    '''
    http://127.0.0.1:8000/option/dayline/?optionindex=10001226

    :param request:
    :return:
    '''
    if request.method == 'GET':
        option_index = request.GET.get('optionindex', '')
        df = get_option_history_ohlc(option_index)
        return JsonResponse(df.to_dict(orient='split'))
    else:
        raise Http404()


def get_grids_of_trading_option():
    # NaN is illegal for json
    daily_summary = _opdb.get_daily_summary()

    def col_name_from_code(code):
        return code[7:11] + code[6:7]
    set_months = set()
    set_strikes = set()
    for _, row in daily_summary.iterrows():
        x = row['EXERCISE_PRICE']
        s = col_name_from_code(row[optiondb.COL_OPTION_CODE])
        if x[4] != '0':
            logger.debug("skip divided strikes: {} {} {}".format(x, s, row[optiondb.COL_OPTION_INDEX]))
            continue
        set_strikes.add(x)
        set_months.add(s)
    logger.debug("strikes:{} months:{}".format(set_strikes, set_months))

    index = [x for x in set_strikes]
    index.sort()
    columns = [s for s in set_months]
    columns.sort()
    logger.debug("index:{} columns:{}".format(index, columns))

    grids = pd.DataFrame(columns=columns, index=index)
    for _, row in daily_summary.iterrows():
        x = row['EXERCISE_PRICE']
        s = col_name_from_code(row[optiondb.COL_OPTION_CODE])
        if x in grids.index:
            grids.loc[x][s] = row[optiondb.COL_OPTION_INDEX]
        else:
            logger.debug("skip divided strikes: {} {} {}".format(x, s, row[optiondb.COL_OPTION_INDEX]))

    # trim NaN
    for i in grids.index:
        for c in columns:
            if grids.loc[i][c] != grids.loc[i][c]:
                grids.loc[i][c] = ''

    logger.debug("\n{}".format(grids.tail(1)))
    return grids

_ohlc_columns = ["c", "d", "h", "l", "milliseconds", "o", "trade_date", "v"]


def get_option_history_ohlc(option_index):
    try:
        db = optiondb.OptionDB()
        df = db.get_ohlc(option_index)
        logger.debug("\n{}".format(df.head(2)))
        if df is not None:
            df = df.drop(['_id', 'option_index'], axis=1)
            logger.debug("columns:{}".format(df.columns))
            # "columns": ["c", "d", "h", "l", "milliseconds", "o", "trade_date", "v"]
        else:
            logger.error("No ohlc found: {}".format(option_index))
        # epoch = timezone.datetime.utcfromtimestamp(0)
        # for i in df.index:
        #     logger.debug(df.loc[i]['d'])
        #     logger.debug(df['d'][i])
        #     day_time = timezone.datetime.strptime(df.loc[i]['d'], '%Y-%m-%d')
        #     df.loc[i]['t'] = (day_time - epoch).total_seconds() * 1000
        # logger.debug("\n{}".format(df.head(1)))
    except Exception as e:
        logger.error(e)
    else:
        return df

