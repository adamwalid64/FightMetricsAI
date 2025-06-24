import { useState } from 'react';
import './App.css';

function App() {
  const [inputs, setInputs] = useState('');
  const [prediction, setPrediction] = useState(null);

  const handleSubmit = async () => {
    try {
      const res = await fetch('http://localhost:5000/predict', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ features: JSON.parse(inputs) })
      });
      const data = await res.json();
      setPrediction(data.prediction);
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="dashboard">
      <header>
        <h1>FightMetricsAI Dashboard</h1>
      </header>
      <div className="main-layout">
        <aside className="sidebar">
          <nav>
            <ul>
              <li>Overview</li>
              <li>Predictions</li>
              <li>Statistics</li>
            </ul>
          </nav>
        </aside>
        <main className="content">
          <section className="cards">
            <div className="card">Statistic 1</div>
            <div className="card">Statistic 2</div>
            <div className="card">Statistic 3</div>
          </section>
          <section className="predict-section">
            <h2>Predict Outcome</h2>
            <textarea
              placeholder="[feature1, feature2, ...]"
              value={inputs}
              onChange={(e) => setInputs(e.target.value)}
            />
            <button onClick={handleSubmit}>Predict</button>
            {prediction !== null && (
              <p className="prediction-result">Prediction: {prediction}</p>
            )}
          </section>
        </main>
      </div>
    </div>
  );
}

export default App;
