import logbot
import json, os, config
from ftxapi import Ftx
from bybitapi import ByBit

subaccount_name = 'SUBACCOUNT_NAME'
leverage = 1.0
risk = 1.0 / 100
api_key = 'API_KEY'
api_secret = 'API_SECRET'


# ================== SET GLOBAL VARIABLES ==================


def global_var(payload):
    global subaccount_name
    global leverage
    global risk
    global api_key
    global api_secret

    subaccount_name = payload['subaccount']

    if subaccount_name == 'MYBYBITACCOUNT':
        leverage_heroku = os.environ.get('LEVERAGE_MYBYBITACCOUNT')
        leverage = leverage_heroku if leverage_heroku != None else config.LEVERAGE_MYBYBITACCOUNT
        leverage = float(leverage)

        risk_heroku = os.environ.get('RISK_MYBYBITACCOUNT')
        risk = risk_heroku if risk_heroku != None else config.RISK_MYBYBITACCOUNT
        risk = float(risk) / 100

        api_key_heroku = os.environ.get('API_KEY_MYBYBITACCOUNT')
        api_key = api_key_heroku if api_key_heroku != None else config.API_KEY_MYBYBITACCOUNT

        api_secret_heroku = os.environ.get('API_SECRET_MYBYBITACCOUNT')
        api_secret = api_secret_heroku if api_secret_heroku != None else config.API_SECRET_MYBYBITACCOUNT

    elif subaccount_name == 'STRATEGY_TWO':
        leverage_heroku = os.environ.get('LEVERAGE_STRATEGY_TWO')
        leverage = leverage_heroku if leverage_heroku != None else config.LEVERAGE_STRATEGY_TWO
        leverage = float(leverage)

        risk_heroku = os.environ.get('RISK_STRATEGY_TWO')
        risk = risk_heroku if risk_heroku != None else config.RISK_STRATEGY_TWO
        risk = float(risk) / 100

        api_key_heroku = os.environ.get('API_KEY_STRATEGY_TWO')
        api_key = api_key_heroku if api_key_heroku != None else config.API_KEY_STRATEGY_TWO

        api_secret_heroku = os.environ.get('API_SECRET_STRATEGY_TWO')
        api_secret = api_secret_heroku if api_secret_heroku != None else config.API_SECRET_STRATEGY_TWO

    else:
        logbot.logs(">>> /!\ Subaccount name not found", True)
        return {
            "success": False,
            "error": "subaccount name not found"
        }
           
    return {
        "success": True
    }


# ================== MAIN ==================


def order(payload: dict):
    #   DEFINE GLOBAL VARIABLE
    glob = global_var(payload)
    if not glob['success']:
        return glob
    
    init_var = {
        'subaccount_name': subaccount_name,
        'leverage': leverage,
        'risk': risk,
        'api_key': api_key,
        'api_secret': api_secret
    }
    exchange = payload['exchange']
    
    #   SET EXCHANGE CLASS
    exchange_api = None
    try:
        if exchange.upper() == 'FTX':
            exchange_api = Ftx(init_var)
        elif exchange.upper() == 'BYBIT':
            exchange_api = ByBit(init_var)
    except Exception as e:
        logbot.logs('>>> /!\ An exception occured : {}'.format(e), True)
        return {
            "success": False,
            "error": str(e)
        }

    logbot.logs('>>> Exchange : {}'.format(exchange))
    logbot.logs('>>> Subaccount : {}'.format(subaccount_name))

    #   FIND THE APPROPRIATE TICKER IN DICTIONNARY
    ticker = ""
    if exchange.upper() == 'BYBIT':
        ticker = payload['ticker']
    else:
        with open('tickers.json') as json_file:
            tickers = json.load(json_file)
            try:
                ticker = tickers[exchange.lower()][payload['ticker']]
            except Exception as e:
                logbot.logs('>>> /!\ An exception occured : {}'.format(e), True)
                return {
                    "success": False,
                    "error": str(e)
                }
    logbot.logs(">>> Ticker '{}' found".format(ticker))

    #   ALERT MESSAGE CONDITIONS
    if payload['message'] == 'entry':
        logbot.logs(">>> Order message : 'entry'")
        exchange_api.exit_position(ticker)
        orders = exchange_api.entry_position(payload, ticker)
        return orders

    elif payload['message'] == 'exit':
        logbot.logs(">>> Order message : 'exit'")
        exit_res = exchange_api.exit_position(ticker)
        return exit_res

    elif payload['message'][-9:] == 'breakeven':
        logbot.logs(">>> Order message : 'breakeven'")
        breakeven_res = exchange_api.breakeven(payload, ticker)
        return breakeven_res
    
    else:
        logbot.logs(f">>> Order message : '{payload['message']}'")

    return {
        "message": payload['message']
    }
