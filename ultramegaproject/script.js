// script.js

async function loadData() {
  try {
    const childrenResp = await fetch('childrenData.json');
    const birthsResp = await fetch('totalBirthsData.json');
    const currencyResp = await fetch('exchangeRates.json');

    if (!childrenResp.ok || !birthsResp.ok || !currencyResp.ok) {
      console.error("Ошибка загрузки данных");
      return;
    }

    const childrenData = await childrenResp.json();
    const birthsData = await birthsResp.json();
    const currencyData = await currencyResp.json();

    const years = [...new Set(childrenData.map(c => c.year))];
    const yearSelect = document.getElementById('yearInput');
    years.forEach(y => {
      const option = document.createElement('option');
      option.value = y;
      option.textContent = y;
      yearSelect.appendChild(option);
    });

    document.getElementById('submitYearBtn').addEventListener('click', () => {
      const year = parseInt(yearSelect.value);
      const forecastDays = parseInt(document.getElementById('forecastDays').value);
      if (year && forecastDays > 0) {
        analyzeBirths(childrenData, birthsData, year, forecastDays);
        analyzeCurrency(currencyData, year, forecastDays);
      }
    });

  } catch (e) {
    console.error("Ошибка:", e);
  }
}

function movingAverage(series, windowSize, steps) {
  const result = [];
  let values = [...series];

  for (let i = 0; i < steps; i++) {
    const recent = values.slice(-windowSize);
    const avg = recent.reduce((sum, val) => sum + val, 0) / recent.length;
    result.push(avg);
    values.push(avg);
  }

  return result;
}

function analyzeBirths(childrenData, totalData, year, forecastYears) {
  const filtered = childrenData
    .filter(c => totalData.find(t => t.year === c.year))
    .map(c => {
      const total = totalData.find(t => t.year === c.year).total_births;
      return {
        year: c.year,
        percentage: (c.children_born_out_of_wedlock / total) * 100
      };
    })
    .sort((a, b) => a.year - b.year);

  const tableBody = document.querySelector('#birthTable tbody');
  tableBody.innerHTML = '';
  filtered.forEach(row => {
    const tr = document.createElement('tr');
    tr.innerHTML = `<td>${row.year}</td><td>${row.percentage.toFixed(2)}</td>`;
    tableBody.appendChild(tr);
  });

  const percentages = filtered.map(r => r.percentage);
  const years = filtered.map(r => r.year);
  const changes = percentages.map((p, i) => i > 0 ? p - percentages[i - 1] : 0);
  const maxChange = Math.max(...changes);
  const minChange = Math.min(...changes);
  const maxChangeYear = filtered[changes.indexOf(maxChange)].year;
  const minChangeYear = filtered[changes.indexOf(minChange)].year;

  document.getElementById("birthChangeSummary").textContent =
    `Максимальный рост: ${maxChange.toFixed(2)}% (${maxChangeYear}), падение: ${minChange.toFixed(2)}% (${minChangeYear})`;

  const forecast = movingAverage(percentages, 5, forecastYears);
  const forecastYearsRange = Array.from({ length: forecastYears }, (_, i) => years[years.length - 1] + i + 1);

  const traceReal = {
    x: years,
    y: percentages,
    mode: 'lines+markers',
    name: 'Факт'
  };

  const traceForecast = {
    x: forecastYearsRange,
    y: forecast,
    mode: 'lines+markers',
    name: 'Прогноз',
    line: { dash: 'dot' }
  };

  Plotly.newPlot('birthsPlot', [traceReal, traceForecast], {
    title: 'Процент внебрачных рождений',
    xaxis: { title: 'Год' },
    yaxis: { title: '%' }
  });
}

function analyzeCurrency(data, year, forecastDays) {
  const filtered = data.filter(d => new Date(d.date).getFullYear() === year);
  const dates = filtered.map(d => d.date);
  const usd = filtered.map(d => d.usd);
  const eur = filtered.map(d => d.eur);

  const table = document.querySelector("#currencyTable tbody");
  table.innerHTML = "";
  filtered.forEach(d => {
    const row = document.createElement("tr");
    row.innerHTML = `<td>${d.date}</td><td>${d.usd}</td><td>${d.eur}</td>`;
    table.appendChild(row);
  });

  const usdChanges = usd.map((v, i) => i > 0 ? v - usd[i - 1] : 0);
  const eurChanges = eur.map((v, i) => i > 0 ? v - eur[i - 1] : 0);

  const maxUsd = Math.max(...usdChanges);
  const minUsd = Math.min(...usdChanges);
  const maxEur = Math.max(...eurChanges);
  const minEur = Math.min(...eurChanges);

  const maxUsdDate = dates[usdChanges.indexOf(maxUsd)];
  const minUsdDate = dates[usdChanges.indexOf(minUsd)];
  const maxEurDate = dates[eurChanges.indexOf(maxEur)];
  const minEurDate = dates[eurChanges.indexOf(minEur)];

  document.getElementById("currencyChangeSummary").textContent =
    `USD: прирост ${maxUsd.toFixed(2)} (${maxUsdDate}), падение ${minUsd.toFixed(2)} (${minUsdDate}); ` +
    `EUR: прирост ${maxEur.toFixed(2)} (${maxEurDate}), падение ${minEur.toFixed(2)} (${minEurDate})`;

  const forecastUsd = movingAverage(usd, 5, forecastDays);
  const forecastEur = movingAverage(eur, 5, forecastDays);
  const lastDate = new Date(dates[dates.length - 1]);
  const forecastDates = Array.from({ length: forecastDays }, (_, i) => {
    const d = new Date(lastDate);
    d.setDate(d.getDate() + i + 1);
    return d.toISOString().split('T')[0];
  });

  const traceUsd = {
    x: dates,
    y: usd,
    mode: 'lines',
    name: 'USD'
  };
  const traceEur = {
    x: dates,
    y: eur,
    mode: 'lines',
    name: 'EUR'
  };
  const traceUsdForecast = {
    x: forecastDates,
    y: forecastUsd,
    mode: 'lines',
    name: 'USD прогноз',
    line: { dash: 'dot' }
  };
  const traceEurForecast = {
    x: forecastDates,
    y: forecastEur,
    mode: 'lines',
    name: 'EUR прогноз',
    line: { dash: 'dot' }
  };

  Plotly.newPlot('currencyPlot', [traceUsd, traceUsdForecast, traceEur, traceEurForecast], {
    title: 'Курс рубля',
    xaxis: { title: 'Дата' },
    yaxis: { title: 'Курс' }
  });
}

loadData();
