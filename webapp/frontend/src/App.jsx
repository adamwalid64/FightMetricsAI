import { useState } from 'react';
import './App.css';

function App() {
  const [fighterOne, setFighterOne] = useState('');
  const [fighterTwo, setFighterTwo] = useState('');
  const [inputs, setInputs] = useState('');
  const [prediction, setPrediction] = useState(null);
  const [nameMessage, setNameMessage] = useState('');

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

  const handleNamePrediction = () => {
    if (fighterOne && fighterTwo) {
      setNameMessage(`Prediction for ${fighterOne} vs ${fighterTwo} coming soon`);
    }
  };

  return (
    <div className="app">
      <header className="site-header">
        <div className="logo">FightMetricsAI</div>
        <nav>
          <ul>
            <li><a href="#features">Features</a></li>
            <li><a href="#predict">Predict</a></li>
            <li><a href="#contact">Contact</a></li>
          </ul>
        </nav>
      </header>
      <main>
        <section className="hero">
          <h1>Unlock Fight Insights</h1>
          <p>Use AI-driven analytics to analyze UFC stats and predict outcomes.</p>
          <a className="cta-button" href="#predict">Get Started</a>
        </section>
        <section className="features" id="features">
          <h2>Features</h2>
          <div className="feature-list">
            <div className="feature">
              <h3>Comprehensive Stats</h3>
              <p>Access detailed fighter statistics scraped from multiple sources.</p>
            </div>
            <div className="feature">
              <h3>Machine Learning</h3>
              <p>Advanced models help forecast fight results based on data.</p>
            </div>
            <div className="feature">
              <h3>Interactive Dashboard</h3>
              <p>Visualize metrics and predictions in a clean dashboard.</p>
            </div>
          </div>
        </section>
        <section className="predict-section" id="predict">
          <h2>Try the Predictor</h2>
          <div className="predict-cards">
            <div className="predict-card left-card">
              <h3>Live Fight Prediction</h3>
              <input
                placeholder="Fighter One"
                value={fighterOne}
                onChange={(e) => setFighterOne(e.target.value)}
              />
              <input
                placeholder="Fighter Two"
                value={fighterTwo}
                onChange={(e) => setFighterTwo(e.target.value)}
              />
              <button onClick={handleNamePrediction}>Predict</button>
              {nameMessage && (
                <p className="prediction-result">{nameMessage}</p>
              )}
            </div>
            <div className="predict-card">
              <h3>Analytics</h3>
              <div className="analytics-placeholder">Charts Coming Soon</div>
            </div>
          </div>

          
        </section>
      </main>
      <footer id="contact">
        <p>&copy; {new Date().getFullYear()} FightMetricsAI - All rights reserved.</p>
      </footer>
    </div>
  );
}

export default App;