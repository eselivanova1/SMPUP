from flask import Flask, jsonify, request, send_file
import pandas as pd
import matplotlib.pyplot as plt
import io
import base64

app = Flask(__name__)

# Функция скользящего среднего
def moving_average_forecast(series, window, steps):
    forecast = []
    values = list(series[-window:])
    for _ in range(steps):
        avg = sum(values[-window:]) / window
        forecast.append(avg)
        values.append(avg)
    return forecast

# Роут для анализа рождаемости
@app.route('/api/births', methods=['GET'])
def get_birth_data():
    try:
        children = pd.read_json('childrenData.json')
        births = pd.read_json('totalBirthsData.json')
        df = pd.merge(children, births, on='year')
        df['percentage'] = df['children_born_out_of_wedlock'] / df['total_births'] * 100

        # вычисляем изменение по годам
        df['change'] = df['percentage'].diff()
        max_change = df['change'].max()
        min_change = df['change'].min()
        max_year = int(df.loc[df['change'].idxmax(), 'year'])
        min_year = int(df.loc[df['change'].idxmin(), 'year'])

        # прогноз
        forecast_n = int(request.args.get('forecast', 3))
        forecast = moving_average_forecast(df['percentage'], window=3, steps=forecast_n)
        forecast_years = list(range(df['year'].max()+1, df['year'].max()+1+forecast_n))

        # график
        plt.figure(figsize=(10,5))
        plt.plot(df['year'], df['percentage'], label='Факт', marker='o')
        plt.plot(forecast_years, forecast, label='Прогноз', linestyle='--', marker='x')
        plt.xlabel('Год')
        plt.ylabel('% вне брака')
        plt.title('Дети вне брака по годам')
        plt.grid(True)
        plt.legend()
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        encoded = base64.b64encode(buf.read()).decode()
        plt.close()

        return jsonify({
            'table': df[['year', 'percentage']].to_dict(orient='records'),
            'max_change': max_change,
            'max_year': max_year,
            'min_change': min_change,
            'min_year': min_year,
            'forecast': list(zip(forecast_years, forecast)),
            'plot': encoded
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Роут для анализа курса валют
@app.route('/api/currency', methods=['GET'])
def get_currency_data():
    try:
        df = pd.read_json('exchangeRates.json')
        df['date'] = pd.to_datetime(df['date'])
        df.sort_values('date', inplace=True)

        df['usd_change'] = df['usd'].diff()
        df['eur_change'] = df['eur'].diff()

        max_usd_gain = df['usd_change'].min()
        max_usd_loss = df['usd_change'].max()
        max_usd_gain_date = df.loc[df['usd_change'].idxmin(), 'date'].strftime('%Y-%m-%d')
        max_usd_loss_date = df.loc[df['usd_change'].idxmax(), 'date'].strftime('%Y-%m-%d')

        max_eur_gain = df['eur_change'].min()
        max_eur_loss = df['eur_change'].max()
        max_eur_gain_date = df.loc[df['eur_change'].idxmin(), 'date'].strftime('%Y-%m-%d')
        max_eur_loss_date = df.loc[df['eur_change'].idxmax(), 'date'].strftime('%Y-%m-%d')

        forecast_n = int(request.args.get('forecast', 5))
        forecast_usd = moving_average_forecast(df['usd'], window=3, steps=forecast_n)
        forecast_eur = moving_average_forecast(df['eur'], window=3, steps=forecast_n)
        last_date = df['date'].max()
        forecast_dates = pd.date_range(start=last_date + pd.Timedelta(days=1), periods=forecast_n)

        # график
        plt.figure(figsize=(10,6))
        plt.plot(df['date'], df['usd'], label='USD факт')
        plt.plot(df['date'], df['eur'], label='EUR факт')
        plt.plot(forecast_dates, forecast_usd, label='USD прогноз', linestyle='--')
        plt.plot(forecast_dates, forecast_eur, label='EUR прогноз', linestyle='--')
        plt.title('Курс рубля')
        plt.xlabel('Дата')
        plt.ylabel('Курс')
        plt.legend()
        plt.grid(True)
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        encoded = base64.b64encode(buf.read()).decode()
        plt.close()

        return jsonify({
            'table': df[['date','usd','eur']].astype(str).to_dict(orient='records'),
            'max_usd_gain': max_usd_gain,
            'max_usd_gain_date': max_usd_gain_date,
            'max_usd_loss': max_usd_loss,
            'max_usd_loss_date': max_usd_loss_date,
            'max_eur_gain': max_eur_gain,
            'max_eur_gain_date': max_eur_gain_date,
            'max_eur_loss': max_eur_loss,
            'max_eur_loss_date': max_eur_loss_date,
            'forecast': list(zip(forecast_dates.strftime('%Y-%m-%d'), forecast_usd, forecast_eur)),
            'plot': encoded
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
