import { useState } from 'react';
import axios from 'axios';

type Candidate = {
  destination: string;
  airport: string;
  price: number;
  distance_km: number;
  price_per_km: number;
};

type ApiResult =
  | { best: Candidate; comparisons: Candidate[] }
  | { message: string }
  | { error: string };

export default function App() {
  const [fromCity, setFromCity] = useState('');
  const [toCities, setToCities] = useState('');
  const [result, setResult] = useState<ApiResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setResult(null);
    setLoading(true);
    try {
      const to = toCities
        .split(',')
        .map((s) => s.trim())
        .filter(Boolean);

      if (!fromCity.trim() || to.length === 0) {
        setError("Please enter a 'From city' and at least one destination.");
        setLoading(false);
        return;
      }

      // Same-origin call; Nginx proxies /api to the backend.
      const { data } = await axios.post<ApiResult>('/api/best', {
        from: fromCity,
        to
      });
      setResult(data);
    } catch (err: any) {
      setError(err?.response?.data?.error || 'Unexpected error.');
    } finally {
      setLoading(false);
    }
  };

  // Helper: sort comparisons by $/km ascending (best first)
  const sortedComparisons = (r: ApiResult | null) => {
    if (!r || 'message' in r || 'error' in r) return [];
    return [...r.comparisons].sort((a, b) => a.price_per_km - b.price_per_km);
  };

  const isEnhancedPayload = (
    r: ApiResult | null
  ): r is { best: Candidate; comparisons: Candidate[] } =>
    !!r && 'best' in r && 'comparisons' in r;

  return (
    <div
      style={{
        maxWidth: 760,
        margin: '40px auto',
        fontFamily: 'system-ui, sans-serif'
      }}
    >
      <h1 style={{ fontSize: 40, marginBottom: 16 }}>
        Flight Optimizer ($/km)
      </h1>

      <form onSubmit={onSubmit} style={{ marginBottom: 16 }}>
        <label>From city</label>
        <input
          value={fromCity}
          onChange={(e) => setFromCity(e.target.value)}
          placeholder="London"
          style={{ width: '100%', marginBottom: 8, padding: 8 }}
        />
        <label>To cities (comma separated)</label>
        <input
          value={toCities}
          onChange={(e) => setToCities(e.target.value)}
          placeholder="Paris, Rome, Madrid"
          style={{ width: '100%', marginBottom: 8, padding: 8 }}
        />
        <button
          type="submit"
          disabled={loading}
          style={{ padding: '8px 14px' }}
        >
          {loading ? 'Calculating...' : 'Find best'}
        </button>
      </form>

      {error && <p style={{ color: 'red' }}>{error}</p>}

      {/* Enhanced payload: best + comparisons */}
      {isEnhancedPayload(result) && (
        <div style={{ marginTop: 16, padding: 12, border: '1px solid #ddd' }}>
          <h3 style={{ marginTop: 0 }}>
            Best destination: {result.best.destination}
          </h3>
          <p>Airport: {result.best.airport}</p>
          <p>Distance: {result.best.distance_km} km</p>
          <p>Price: ${result.best.price}</p>
          <p>Price per km: ${result.best.price_per_km}/km</p>

          <hr style={{ margin: '16px 0' }} />
          <h4>All comparisons</h4>
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr>
                <th style={{ textAlign: 'left', padding: '6px 4px' }}>
                  Destination
                </th>
                <th style={{ textAlign: 'left', padding: '6px 4px' }}>
                  Airport
                </th>
                <th style={{ textAlign: 'right', padding: '6px 4px' }}>
                  Distance (km)
                </th>
                <th style={{ textAlign: 'right', padding: '6px 4px' }}>
                  Price
                </th>
                <th style={{ textAlign: 'right', padding: '6px 4px' }}>
                  $ / km
                </th>
              </tr>
            </thead>
            <tbody>
              {sortedComparisons(result).map((c) => {
                const isBest =
                  c.destination === result.best.destination &&
                  c.airport === result.best.airport;
                return (
                  <tr
                    key={`${c.destination}-${c.airport}`}
                    style={{ background: isBest ? '#e8ffe8' : 'transparent' }}
                  >
                    <td style={{ padding: '6px 4px' }}>{c.destination}</td>
                    <td style={{ padding: '6px 4px' }}>{c.airport}</td>
                    <td style={{ textAlign: 'right', padding: '6px 4px' }}>
                      {c.distance_km}
                    </td>
                    <td style={{ textAlign: 'right', padding: '6px 4px' }}>
                      ${c.price}
                    </td>
                    <td style={{ textAlign: 'right', padding: '6px 4px' }}>
                      ${c.price_per_km}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}

      {/* Plain message payload (e.g., no flights in next 24h) */}
      {result && 'message' in result && <p>{result.message}</p>}
    </div>
  );
}
