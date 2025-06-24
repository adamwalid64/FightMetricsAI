import { useState, useEffect } from 'react';
import './App.css';

function App() {
  const [fighterOne, setFighterOne] = useState('');
  const [fighterTwo, setFighterTwo] = useState('');
  const [inputs, setInputs] = useState('');
  const [prediction, setPrediction] = useState(null);
  const [nameMessage, setNameMessage] = useState('');

  useEffect(() => {
    const canvas = document.getElementById('decision-canvas');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    let animationFrame;

    function resize() {
      canvas.width = canvas.offsetWidth;
      canvas.height = canvas.offsetHeight;
    }

    window.addEventListener('resize', resize);
    resize();

    const titles = [
      'Striking Accuracy',
      'Takedown Defense',
      'KO Rate',
      'SLpM',
      'Reach',
      'Submission Avg',
      'Guard Passing',
      'Ground Control',
    ];

    const shapes = ['circle', 'square', 'triangle'];
    const numNodes = 30;
    const nodes = [];

    for (let i = 0; i < numNodes; i++) {
      nodes.push({
        x: Math.random() * canvas.width,
        y: Math.random() * canvas.height,
        value: (50 + Math.random() * 50).toFixed(1),
        title: titles[Math.floor(Math.random() * titles.length)],
        shape: shapes[i % shapes.length],
      });
    }

    const edges = [];
    nodes.forEach((from) => {
      // Slightly reduce the number of edges created between nodes
      const connectionCount = 1 + Math.floor(Math.random() * 3); // 1-3 connections
      for (let i = 0; i < connectionCount; i++) {
        let to = nodes[Math.floor(Math.random() * numNodes)];
        if (to === from) continue;
        edges.push([from, to]);
      }
    });

    let offset = 0;
    const speed = 0.5;

    function drawNetwork(xOffset) {
      edges.forEach(([from, to]) => {
        ctx.beginPath();
        ctx.moveTo(from.x + xOffset, from.y);
        ctx.lineTo(to.x + xOffset, to.y);
        ctx.stroke();
      });

      nodes.forEach((node) => {
        const x = node.x + xOffset;
        ctx.beginPath();
        if (node.shape === 'square') {
          ctx.rect(x - 5, node.y - 5, 10, 10);
        } else if (node.shape === 'triangle') {
          ctx.moveTo(x, node.y - 6);
          ctx.lineTo(x - 5, node.y + 5);
          ctx.lineTo(x + 5, node.y + 5);
          ctx.closePath();
        } else {
          ctx.arc(x, node.y, 5, 0, Math.PI * 2);
        }
        ctx.fill();
        ctx.stroke();
        ctx.fillText(`${node.title} ${node.value}%`, x + 8, node.y + 3);
      });
    }

    function draw() {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      ctx.strokeStyle = 'rgba(255,255,255,0.3)';
      ctx.fillStyle = 'rgba(255,255,255,0.8)';

      offset += speed;
      if (offset > canvas.width) offset = 0;

      drawNetwork(offset);
      drawNetwork(offset - canvas.width);
      drawNetwork(offset + canvas.width);

      animationFrame = requestAnimationFrame(draw);
    }

    draw();

    return () => {
      window.removeEventListener('resize', resize);
      cancelAnimationFrame(animationFrame);
    };
  }, []);

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
        <div className="logo">FightMetricsAI<span className="logo-icon" /></div>
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
          <canvas id="decision-canvas" className="decision-canvas"></canvas>
          <div className="hero-content">
            <h1>Unlock Fight Insights</h1>
            <p>Use AI-driven analytics to analyze UFC stats and predict outcomes.</p>
            <a className="cta-button" href="#predict">Get Started</a>
          </div>
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
              <div className="fighter-selection">
                <div className="fighter-input">
                  <div className="fighter-image"></div>
                  <input
                    list="fighter-options"
                    placeholder="Fighter One"
                    value={fighterOne}
                    onChange={(e) => setFighterOne(e.target.value)}
                  />
                </div>
                <span className="vs">vs</span>
                <div className="fighter-input">
                  <div className="fighter-image"></div>
                  <input
                    list="fighter-options"
                    placeholder="Fighter Two"
                    value={fighterTwo}
                    onChange={(e) => setFighterTwo(e.target.value)}
                  />
                </div>
              </div>
              <button onClick={handleNamePrediction}>Predict</button>
              {nameMessage && (
                <p className="prediction-result">{nameMessage}</p>
              )}
              <datalist id="fighter-options">
                <option value="Conor McGregor" />
                <option value="Khabib Nurmagomedov" />
                <option value="Jon Jones" />
                <option value="Israel Adesanya" />
              </datalist>
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
