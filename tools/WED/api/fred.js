// api/fred.js

import API_KEYS from './api_keys.js';

const FRED_API_KEY = API_KEYS.fred;
const FRED_BASE_URL = "https://api.stlouisfed.org/fred";

async function fetchFREDSeriesLatest(seriesId) {
    const url = `${FRED_BASE_URL}/series/observations?series_id=${seriesId}&api_key=${FRED_API_KEY}&file_type=json&sort_order=desc&limit=1`;
    const res = await fetch(url);
    if (!res.ok) throw new Error(`Fehler beim Abruf von ${seriesId}`);
    const data = await res.json();
    return data.observations[0];
}

async function getUSGDP() {
    return await fetchFREDSeriesLatest("GDP");
}

async function getUSInflation() {
    return await fetchFREDSeriesLatest("CPIAUCSL");
}

async function getUSUnemployment() {
    return await fetchFREDSeriesLatest("UNRATE");
}

async function getUSInterestRate() {
    return await fetchFREDSeriesLatest("FEDFUNDS");
}

export {
    getUSGDP,
    getUSInflation,
    getUSUnemployment,
    getUSInterestRate
};
