import { useState } from 'react';
import './App.css';

function App() {
  const [inputs, setInputs] = useState('');
  const [prediction, setPrediction] = useState(null);

  const handleSubmit = async () => {
    const res = await fetch('http://localhost:5000/predict', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ features: JSON.parse(inputs) })
    });
    const data = await res.json();
    setPrediction(data.prediction);
  };

  return (
    <div className="App">
      <h1>FightMetricsAI</h1>
      <textarea
        placeholder="Enter feature array (JSON)"
        value={inputs}
        onChange={(e) => setInputs(e.target.value)}
      />
      <button onClick={handleSubmit}>Predict</button>
      {prediction !== null && <div>Prediction: {prediction}</div>}
    </div>
  );
}

export default App;
