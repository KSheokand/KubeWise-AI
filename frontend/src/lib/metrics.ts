import {
  PrometheusHistoryResponse,
  ChartDataPoint,
} from "./api";

export function convertPrometheusHistory(
  response: PrometheusHistoryResponse
): ChartDataPoint[] {
  const series = response.results?.[0];

  if (!series?.values) {
    return [];
  }

  return series.values.map(([timestamp, value]) => ({
    time: new Date(timestamp * 1000).toLocaleTimeString(
      "en-IN",
      {
        hour: "2-digit",
        minute: "2-digit",
      }
    ),
    usage: Number(value),
  }));
}