import pandas as pd
import matplotlib.pyplot as plt

# Функция для вычисления скользящего среднего и экстраполяции
def moving_average_extrapolation(series, window, steps):
    values = list(series[-window:])  # Берём последние данные по окну
    forecast = []  # Массив для хранения прогнозов

    for _ in range(steps):
        avg = sum(values[-window:]) / window  # Вычисляем среднее
        forecast.append(avg)
        values.append(avg)  # Добавляем новый прогноз в список

    return forecast

# Функция анализа рождаемости
def analyze_births(children_data_file, total_births_data_file, forecast_years):
    # Загружаем данные из JSON файлов
    children_data = pd.read_json(children_data_file)
    total_births_data = pd.read_json(total_births_data_file)

    # Объединяем данные по году
    df = pd.merge(children_data, total_births_data, on="year")
    df["percentage_out_of_wedlock"] = (df["children_born_out_of_wedlock"] / df["total_births"]) * 100

    # Выводим процент рождаемости вне брака
    print("\nПроцент рождений вне брака по годам:")
    print(df[["year", "percentage_out_of_wedlock"]].to_string(index=False))

    # График фактических данных
    plt.figure(figsize=(10, 5))
    plt.plot(df["year"], df["percentage_out_of_wedlock"], marker="o", label="Факт")
    plt.title("Процент детей, рождённых вне брака")
    plt.xlabel("Год")
    plt.ylabel("Процент")
    plt.grid(True)
    plt.legend()
    plt.show()

    # Изменения по годам
    df["change"] = df["percentage_out_of_wedlock"].diff()  # Разница между текущим и предыдущим годом
    max_change = df["change"].max()
    min_change = df["change"].min()
    max_year = df.loc[df["change"].idxmax(), "year"]
    min_year = df.loc[df["change"].idxmin(), "year"]

    # Выводим информацию об изменениях
    print(f"\n📈 Максимальный рост: {max_change:.2f}% в {max_year} году")
    print(f"📉 Максимальное падение: {min_change:.2f}% в {min_year} году")

    # Прогнозирование (скользящее среднее)
    forecast = moving_average_extrapolation(df["percentage_out_of_wedlock"], window=3, steps=forecast_years)
    forecast_years_range = list(range(df["year"].max() + 1, df["year"].max() + 1 + forecast_years))

    # График с прогнозом
    plt.figure(figsize=(10, 5))
    plt.plot(df["year"], df["percentage_out_of_wedlock"], marker="o", label="Факт")
    plt.plot(forecast_years_range, forecast, marker="x", linestyle="--", label="Прогноз")
    plt.title("Прогноз процента рождённых вне брака (скользящая средняя)")
    plt.xlabel("Год")
    plt.ylabel("Процент")
    plt.grid(True)
    plt.legend()
    plt.show()

# Функция анализа курса валют
def analyze_currency(currency_file, forecast_days):
    df = pd.read_json(currency_file)
    df["date"] = pd.to_datetime(df["date"])  # Преобразуем даты в формат datetime

    # Выводим курс рубля по дням
    print("\nКурс рубля по дням:")
    print(df[["date", "usd", "eur"]].to_string(index=False))

    # График курса валют
    plt.figure(figsize=(12, 6))
    plt.plot(df["date"], df["usd"], label="USD")
    plt.plot(df["date"], df["eur"], label="EUR")
    plt.title("Курс рубля к USD и EUR")
    plt.xlabel("Дата")
    plt.ylabel("Курс")
    plt.legend()
    plt.grid(True)
    plt.show()

    # Изменения по дням
    df["usd_change"] = df["usd"].diff()
    df["eur_change"] = df["eur"].diff()

    max_usd_gain = df["usd_change"].min()  # Максимальное укрепление рубля
    max_usd_gain_date = df.loc[df["usd_change"].idxmin(), "date"]
    max_usd_loss = df["usd_change"].max()  # Максимальное ослабление рубля
    max_usd_loss_date = df.loc[df["usd_change"].idxmax(), "date"]

    max_eur_gain = df["eur_change"].min()  # Максимальное укрепление рубля по EUR
    max_eur_gain_date = df.loc[df["eur_change"].idxmin(), "date"]
    max_eur_loss = df["eur_change"].max()  # Максимальное ослабление рубля по EUR
    max_eur_loss_date = df.loc[df["eur_change"].idxmax(), "date"]
    # Выводим информацию о изменениях
    print(f"\n💵 USD:")
    print(f"  📈 Рубль укрепился на {abs(max_usd_gain):.2f} в {max_usd_gain_date.date()}")
    print(f"  📉 Рубль ослаб на {abs(max_usd_loss):.2f} в {max_usd_loss_date.date()}")
    
    print(f"\n💶 EUR:")
    print(f"  📈 Рубль укрепился на {abs(max_eur_gain):.2f} в {max_eur_gain_date.date()}")
    print(f"  📉 Рубль ослаб на {abs(max_eur_loss):.2f} в {max_eur_loss_date.date()}")

    # Прогнозирование курса валют (скользящее среднее)
    for currency in ["usd", "eur"]:
        forecast = moving_average_extrapolation(df[currency], window=3, steps=forecast_days)
        forecast_dates = pd.date_range(start=df["date"].max() + pd.Timedelta(days=1), periods=forecast_days)

        plt.figure(figsize=(10, 4))
        plt.plot(df["date"], df[currency], label="Факт", marker="o")
        plt.plot(forecast_dates, forecast, label="Прогноз", linestyle="--", marker="x")
        plt.title(f"Прогноз курса рубля к {currency.upper()} (скользящая средняя)")
        plt.xlabel("Дата")
        plt.ylabel("Курс")
        plt.legend()
        plt.grid(True)
        plt.show()

# === Запуск ===
import os

if __name__ == "__main__":
    try:
        forecast_n = int(input("Введите количество лет для прогноза по рождаемости: "))
        
        births_path1 = "d:/4 семестр/1/childrenData.json"
        births_path2 = "d:/4 семестр/1/totalBirthsData.json"
        currency_path = "d:/4 семестр/1/exchangeRates.json"

        
        analyze_births(births_path1, births_path2, forecast_n)

        forecast_n_days = int(input("\nВведите количество дней для прогноза по курсу валют: "))
        analyze_currency(currency_path, forecast_n_days)

    except FileNotFoundError as e:
        print(f"❌ Ошибка: файл не найден — {e}")
    except ValueError:
        print("❌ Ошибка: введено не число.")
    except Exception as e:
        print(f"❌ Произошла ошибка: {e}")
