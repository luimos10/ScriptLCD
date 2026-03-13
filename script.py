import time

from functions import analizarMonedas, buscarTicks, dias, showResults


def main():
    inicio = time.perf_counter()
    ticks = buscarTicks()
    print(f"NUMERO DE TICKS: {len(ticks)}")
    print(f"NUMERO DE DIAS A ESTIMAR: {dias}")

    resultados = analizarMonedas(ticks)
    showResults(resultados)

    duracion = round(time.perf_counter() - inicio, 2)
    print(f"TIEMPO TOTAL: {duracion}s")


if __name__ == '__main__':
    main()
