import { useState } from 'react';
import axios from 'axios';

export default function App() {
  const [fromCity, setFromCity] = useState('');
  const [toCities, setToCities] = useState('');
  const [result, setResult] = useState<any>(null);
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
      const { data } = await axios.post('http://127.0.0.1:8000/api/best', {
        from: fromCity,
        to
      });
      setResult(data);
    } catch (err: any) {
      setError(err?.response?.data?.error || 'Error');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div
      style={{
        maxWidth: 600,
        margin: '40px auto',
        fontFamily: 'system-ui, sans-serif'
      }}
    >
      <h1>Flight Optimizer ($/km)</h1>
      <form onSubmit={onSubmit}>
        <label>From city</label>
        <input
          value={fromCity}
          onChange={(e) => setFromCity(e.target.value)}
          placeholder="London"
          style={{ width: '100%', marginBottom: 8 }}
        />
        <label>To cities (comma separated)</label>
        <input
          value={toCities}
          onChange={(e) => setToCities(e.target.value)}
          placeholder="Paris, Rome, Madrid"
          style={{ width: '100%', marginBottom: 8 }}
        />
        <button type="submit" disabled={loading}>
          {loading ? 'Calculating...' : 'Find best'}
        </button>
      </form>

      {error && <p style={{ color: 'red' }}>{error}</p>}
      {result && !result.message && (
        <div style={{ marginTop: 16, padding: 12, border: '1px solid #ddd' }}>
          <h3>Best destination: {result.destination}</h3>
          <p>Airport: {result.airport}</p>
          <p>Distance: {result.distance_km} km</p>
          <p>Price per km: ${result.price_per_km}/km</p>
          <p>Price (approx): ${result.price}</p>
        </div>
      )}
      {result?.message && <p>{result.message}</p>}
    </div>
  );
}
