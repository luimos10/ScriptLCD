import random
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

import config
from binance.client import Client

# Configuración
dias = int(getattr(config, 'dias', 30))
workers = max(1, int(getattr(config, 'workers', 6)))
max_retries = max(1, int(getattr(config, 'max_retries', 6)))
retry_base_delay = float(getattr(config, 'retry_base_delay', 1.0))
request_timeout = int(getattr(config, 'request_timeout', 10))
show_progress = bool(getattr(config, 'show_progress', True))

client = Client(
    getattr(config, 'API_KEY', ''),
    getattr(config, 'API_SECRET', ''),
    tld='com',
    requests_params={'timeout': request_timeout},
)


def _log_error(error):
    with open('log.txt', 'a', encoding='utf-8') as archivo:
        mensaje = time.strftime('%d-%m-%Y %H:%M:%S', time.localtime())
        archivo.write(f"{mensaje} ERROR: {error}\n")


def _with_retry(fn, *args, **kwargs):
    for attempt in range(1, max_retries + 1):
        try:
            return fn(*args, **kwargs)
        except Exception as error:
            print(f"ERROR attempt {attempt}/{max_retries}: {error}")
            _log_error(error)
            if attempt == max_retries:
                raise
            backoff = min(retry_base_delay * (2 ** (attempt - 1)), 30.0)
            time.sleep(backoff + random.uniform(0.0, 0.3))


def buscarTicks():
    list_of_tickers = _with_retry(client.futures_symbol_ticker)
    return [tick['symbol'] for tick in list_of_tickers if tick['symbol'].endswith('USDT')]


def _analizar_moneda(tick):
    klines = _with_retry(
        client.futures_klines,
        symbol=tick,
        interval=client.KLINE_INTERVAL_1DAY,
        limit=dias,
    )

    if not klines or len(klines) < 2:
        return None

    old_close = float(klines[0][4])
    new_close = float(klines[-1][4])
    if old_close == 0:
        return None

    porcentaje = round((new_close - old_close) / old_close * 100, 2)
    return (tick, old_close, new_close, porcentaje)


def analizarMonedas(ticks):
    resultados = []

    if not ticks:
        return resultados

    if workers == 1:
        for index, tick in enumerate(ticks, start=1):
            try:
                resultado = _analizar_moneda(tick)
                if resultado is not None:
                    resultados.append(resultado)
            except Exception as error:
                _log_error(error)
            if show_progress and (index == len(ticks) or index % 25 == 0):
                print(f"ANALIZADAS: {index}/{len(ticks)}")
        return resultados

    with ThreadPoolExecutor(max_workers=workers) as executor:
        future_to_tick = {executor.submit(
            _analizar_moneda, tick): tick for tick in ticks}
        for index, future in enumerate(as_completed(future_to_tick), start=1):
            try:
                resultado = future.result()
                if resultado is not None:
                    resultados.append(resultado)
            except Exception as error:
                _log_error(error)
            if show_progress and (index == len(ticks) or index % 25 == 0):
                print(f"ANALIZADAS: {index}/{len(ticks)}")

    return resultados


def showResults(resultados=None):
    datos = resultados or []
    ordenar = sorted(datos, key=lambda result: result[3])
    for r in ordenar:
        print(f"TICK: {r[0]} OLD:{r[1]} NEW:{r[2]} PORCENTAJE: {r[3]}%")
