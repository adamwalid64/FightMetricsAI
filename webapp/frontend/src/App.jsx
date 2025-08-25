import { useState, useEffect } from 'react';
import './App.css';
import logo from '../img/robologo.png';
import bluefighter from '../img/bluerobo.png'
import redfighter from '../img/redrobo.png'
import redroboNews from '../img/redrobo-news.png'
import headCog from '../img/head_cog_b34345_white_outline_clear.png'
import FeatureImportanceChart from './FeatureImportanceChart';
import { apiFetch } from './api';
import AllModelsFeatureImportance from './AllModelsFeatureImportance';
import DataShowcase from './DataShowcase';
import FighterDatabase from './FighterDatabase';
import RAGPipeline from './RAGPipeline';
import FighterDropdown from './FighterDropdown';


function App() {
  const [fighterOne, setFighterOne] = useState('');
  const [fighterTwo, setFighterTwo] = useState('');
  const [prediction, setPrediction] = useState(null);
  const [modelPredictions, setModelPredictions] = useState(null);
  const [ensemblePrediction, setEnsemblePrediction] = useState(null);
  const [fighter1Votes, setFighter1Votes] = useState(0);
  const [fighter2Votes, setFighter2Votes] = useState(0);
  const [activeSection, setActiveSection] = useState('predict');
  const [fighters, setFighters] = useState([]);
  const [loading, setLoading] = useState(true);
  const [predictionLoading, setPredictionLoading] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  // Fetch fighter data from backend
  useEffect(() => {
    const fetchFighters = async () => {
      try {
        console.log('Fetching fighter data from backend...');
        const response = await apiFetch('/fighter-data', {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
          },
        });
        console.log('Response status:', response.status);
        console.log('Response headers:', response.headers);
        
        if (response.ok) {
          const data = await response.json();
          console.log('Fighter data received:', data.length, 'fighters');
          console.log('Sample fighters:', data.slice(0, 5));
          
          // Extract unique fighter names
          const uniqueFighters = [...new Set(data.map(fighter => fighter.name))].sort();
          console.log('Unique fighters:', uniqueFighters.length);
          console.log('Sample unique fighters:', uniqueFighters.slice(0, 10));
          
          setFighters(uniqueFighters);
          console.log('Fighters state updated with:', uniqueFighters.length, 'fighters');
        } else {
          console.error('Failed to fetch fighter data. Status:', response.status);
          const errorText = await response.text();
          console.error('Error response:', errorText);
        }
      } catch (error) {
        console.error('Error fetching fighter data:', error);
        console.error('Error details:', error.message);
      } finally {
        setLoading(false);
        console.log('Loading finished. Current fighters count:', fighters.length);
      }
    };

    fetchFighters();
  }, []);

  // Monitor fighters state changes
  useEffect(() => {
    console.log('Fighters state changed:', fighters.length, 'fighters');
    if (fighters.length > 0) {
      console.log('First 10 fighters:', fighters.slice(0, 10));
    }
  }, [fighters]);

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
    const minDistance = 60; // keep nodes spaced so labels don't overlap

    for (let i = 0; i < numNodes; i++) {
      let x, y, attempts = 0;
      do {
        x = Math.random() * canvas.width;
        y = Math.random() * canvas.height;
        attempts++;
      } while (
        attempts < 100 &&
        nodes.some((n) => Math.hypot(n.x - x, n.y - y) < minDistance)
      );

      nodes.push({
        x,
        y,
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
    // Validate that both fighters are selected
    if (!fighterOne || !fighterTwo) {
      alert('Please select both fighters before making a prediction.');
      return;
    }
    
    // Validate that fighters are different
    if (fighterOne === fighterTwo) {
      alert('Please select two different fighters.');
      return;
    }
    
    try {
      setPredictionLoading(true);
      const res = await apiFetch('/predict', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          fighterOne,
          fighterTwo
        })
      });
      const data = await res.json();
      setPrediction(data.prediction);
      setModelPredictions(data.model_predictions);
      setEnsemblePrediction(data.ensemble_prediction);
      setFighter1Votes(data.fighter1_votes);
      setFighter2Votes(data.fighter2_votes);
    } catch (err) {
      console.error(err);
      alert('An error occurred while making the prediction. Please try again.');
    } finally {
      setPredictionLoading(false);
    }
  };


  return (
    <div className="app">
             <header className="site-header">
         <div className="logo">
           <img src={logo} alt="Logo" className="logo-icon" />
           FightMetricsAI
         </div>
                   <nav className="desktop-nav">
            <ul>
              <li><a href="#predict">Predict</a></li>
              <li><a href="#database">Database</a></li>
              <li><a href="#contact">Contact</a></li>
            </ul>
          </nav>
         <div className="mobile-menu-toggle" onClick={() => setMobileMenuOpen(!mobileMenuOpen)}>
           <div className={`hamburger ${mobileMenuOpen ? 'open' : ''}`}>
             <span></span>
             <span></span>
             <span></span>
           </div>
         </div>
         <nav className={`mobile-nav ${mobileMenuOpen ? 'open' : ''}`}>
           <button 
             className="mobile-nav-close" 
             onClick={() => setMobileMenuOpen(false)}
             aria-label="Close menu"
           >
             ×
           </button>
                       <ul>
              <li><a href="#predict" onClick={() => setMobileMenuOpen(false)}>Predict</a></li>
              <li><a href="#database" onClick={() => setMobileMenuOpen(false)}>Database</a></li>
              <li><a href="#contact" onClick={() => setMobileMenuOpen(false)}>Contact</a></li>
            </ul>
         </nav>
       </header>
      <main>
        <section className="hero">
          <canvas id="decision-canvas" className="decision-canvas"></canvas>
          <div className="hero-content">
            <h1>Smarter UFC Picks, Powered by AI</h1>
            <p>AI-Driven ML & RAG Analytics for Smarter UFC Picks</p>
            <a className="cta-button" href="#predict">Get Started</a>
          </div>
        </section>
        <section className="features" id="features">
          <h2>Predictive Workflow</h2>
          <div className="feature-list">
            <div className="feature">
              <h3>Machine Learning</h3>
              <p>Run a UFC fight prediction using an advanced ensemble system combining XGBoost, Logistic Regression, CatBoost, and MLP models. The ensemble uses Out-of-Fold stacking with a meta-learner to deliver superior predictions, trained on decades of historical data with proven accuracy.</p>
            </div>
            <div className="feature-arrow">
              <div className="arrow-line"></div>
              <div className="arrow-head"></div>
            </div>
            <div className="feature">
              <h3>RAG Sentiment Analysis</h3>
              <p>Verify the AI prediction by automatically scraping the web for hundreds of articles, gathering insights from news outlets, fighters, commentators, and analysts. Summarize prediction confidence, key caveats, and the latest fight-related news—saving hours of manual research</p>
            </div>
            <div className="feature-arrow">
              <div className="arrow-line"></div>
              <div className="arrow-head"></div>
            </div>
            <div className="feature">
              <h3>Final Review & Validation</h3>
              <p>Cross-check the AI prediction and aggregated RAG analysis against the platform’s comprehensive fight database. Conduct your own sentiment and data research to validate outcomes, spot discrepancies, and add your expert perspective before making the final call.</p>
            </div>
          </div>
        </section>
        <section className="predict-section" id="predict">
          <h2>Prediction Dashboard</h2>
          <div className="predict-split-layout">
            <div className="predict-left">
              <div className="ml-predictor">
                <div className="title-section">
                  <div className="icon-container">
                    <img 
                      src={headCog} 
                      alt="ML Prediction Cog Icon" 
                      id="ml-prediction-icon"
                    />
                  </div>
                  <h3>Machine Learning Fight Analysis</h3>
                </div>
                <p className="tool-description">
                Use an ensemble system combining XGBoost, Logistic Regression, CatBoost, and MLP models with Out-of-Fold stacking and a meta-learner. This approach leverages the strengths of multiple algorithms trained on decades of UFC statistics to deliver superior fight predictions with greater accuracy and confidence
                </p>
                <div className="fighter-selection">
                  <FighterDropdown
                    fighters={fighters}
                    value={fighterOne}
                    onChange={setFighterOne}
                    placeholder="Fighter One"
                    fighterImage={redfighter}
                    altText="red robo fighter"
                  />
                  <span className="vs">vs</span>
                  <FighterDropdown
                    fighters={fighters}
                    value={fighterTwo}
                    onChange={setFighterTwo}
                    placeholder="Fighter Two"
                    fighterImage={bluefighter}
                    altText="blue robo fighter"
                  />
                </div>
                <button onClick={handleSubmit}>Predict</button>
                {loading && <p style={{color: 'white', fontSize: '14px'}}>Loading fighters...</p>}
                <p style={{color: 'white', fontSize: '12px'}}>
                  Loaded {fighters.length} fighters
                </p>
                
                {/* Prediction Results */}
                {predictionLoading && (
                  <div className="prediction-loading">
                    <p style={{color: 'white', fontSize: '14px'}}>Analyzing fighters...</p>
                  </div>
                )}
                
                {prediction && modelPredictions && (
                  <div className="prediction-results">
                    <h4 style={{color: 'white', marginBottom: '15px'}}>Prediction Results</h4>
                    
                    {/* Ensemble Prediction - Show prominently if available */}
                    {ensemblePrediction && (
                      <div className="ensemble-result" style={{
                        backgroundColor: 'rgba(76, 175, 80, 0.2)',
                        border: '2px solid rgba(76, 175, 80, 0.6)',
                        padding: '20px',
                        borderRadius: '12px',
                        marginBottom: '25px',
                        textAlign: 'center'
                      }}>
                        <h5 style={{color: '#4CAF50', margin: '0 0 15px 0', fontSize: '18px'}}>
                          🎯 Ensemble Prediction
                        </h5>
                        <p style={{color: 'white', fontSize: '24px', fontWeight: 'bold', margin: '0 0 10px 0'}}>
                          {ensemblePrediction.winner_name} wins!
                        </p>
                        <div style={{
                          display: 'flex',
                          justifyContent: 'space-around',
                          marginTop: '15px',
                          flexWrap: 'wrap',
                          gap: '10px'
                        }}>
                          <div style={{textAlign: 'center'}}>
                            <span style={{color: 'rgba(255, 255, 255, 0.8)', fontSize: '12px'}}>Probability</span>
                            <p style={{color: 'white', fontSize: '18px', fontWeight: 'bold', margin: '5px 0 0 0'}}>
                              {(ensemblePrediction.ensemble_probability * 100).toFixed(1)}%
                            </p>
                          </div>
                          <div style={{textAlign: 'center'}}>
                            <span style={{color: 'rgba(255, 255, 255, 0.8)', fontSize: '12px'}}>Confidence</span>
                            <p style={{color: 'white', fontSize: '18px', fontWeight: 'bold', margin: '5px 0 0 0'}}>
                              {(ensemblePrediction.confidence * 100).toFixed(1)}%
                            </p>
                          </div>
                        </div>
                      </div>
                    )}
                    
                    {/* Overall Result */}
                    <div className="overall-result" style={{
                      backgroundColor: 'rgba(255, 255, 255, 0.1)',
                      padding: '15px',
                      borderRadius: '8px',
                      marginBottom: '20px',
                      textAlign: 'center'
                    }}>
                      <h5 style={{color: 'white', margin: '0 0 10px 0'}}>
                        {ensemblePrediction ? 'Final Prediction' : 'Overall Prediction'}
                      </h5>
                      <p style={{color: 'white', fontSize: '18px', fontWeight: 'bold', margin: '0'}}>
                        {prediction} wins!
                      </p>
                      <p style={{color: 'white', fontSize: '14px', margin: '5px 0 0 0'}}>
                        {ensemblePrediction 
                          ? `Ensemble confidence: ${(ensemblePrediction.confidence * 100).toFixed(1)}%`
                          : `${prediction === fighterOne ? fighter1Votes : fighter2Votes}/4 models picked ${prediction}`
                        }
                      </p>
                    </div>
                    
                    {/* Individual Model Results - Four Models */}
                    <div className="model-breakdown">
                      <h5 style={{color: 'white', marginBottom: '15px'}}>
                        {ensemblePrediction ? 'Base Model Predictions' : 'Individual Model Predictions'}
                      </h5>
                      {Object.entries(modelPredictions).map(([modelName, modelData]) => (
                        <div key={modelName} style={{
                          backgroundColor: 'rgba(255, 255, 255, 0.05)',
                          padding: '12px',
                          borderRadius: '6px',
                          marginBottom: '10px',
                          border: '1px solid rgba(255, 255, 255, 0.1)'
                        }}>
                          <div style={{
                            display: 'flex',
                            justifyContent: 'space-between',
                            alignItems: 'center',
                            marginBottom: '8px'
                          }}>
                            <span style={{color: 'white', fontWeight: 'bold'}}>{modelName}</span>
                            <span style={{
                              color: modelData.prediction === prediction ? '#4CAF50' : '#FF9800',
                              fontSize: '12px',
                              fontWeight: 'bold'
                            }}>
                              {modelData.prediction === prediction ? '✓' : '✗'}
                            </span>
                          </div>
                          <div style={{
                            display: 'flex',
                            justifyContent: 'space-between',
                            fontSize: '12px'
                          }}>
                            <span style={{color: 'rgba(255, 255, 255, 0.8)'}}>
                              {fighterOne}: {(modelData.fighter1_prob * 100).toFixed(1)}%
                            </span>
                            <span style={{color: 'rgba(255, 255, 255, 0.8)'}}>
                              {fighterTwo}: {(modelData.fighter2_prob * 100).toFixed(1)}%
                            </span>
                          </div>
                          <div style={{
                            textAlign: 'center',
                            marginTop: '8px',
                            padding: '6px',
                            backgroundColor: 'rgba(255, 255, 255, 0.1)',
                            borderRadius: '4px'
                          }}>
                            <span style={{color: 'white', fontSize: '14px', fontWeight: 'bold'}}>
                              Predicted: {modelData.prediction}
                            </span>
                          </div>
                        </div>
                      ))}
                    </div>
                    
                    {/* Ensemble Base Model Contributions - Show if ensemble is available */}
                    {ensemblePrediction && ensemblePrediction.base_predictions && (
                      <div className="ensemble-contributions">
                        <h5 style={{color: 'white', marginBottom: '15px'}}>Ensemble Model Contributions</h5>
                        <div style={{
                          backgroundColor: 'rgba(255, 255, 255, 0.05)',
                          padding: '15px',
                          borderRadius: '8px',
                          border: '1px solid rgba(255, 255, 255, 0.1)'
                        }}>
                          <p style={{color: 'rgba(255, 255, 255, 0.8)', fontSize: '12px', marginBottom: '10px'}}>
                            How each base model contributed to the final ensemble prediction:
                          </p>
                          {Object.entries(ensemblePrediction.base_predictions).map(([modelName, prob]) => (
                            <div key={modelName} style={{
                              display: 'flex',
                              justifyContent: 'space-between',
                              alignItems: 'center',
                              padding: '8px 0',
                              borderBottom: '1px solid rgba(255, 255, 255, 0.1)'
                            }}>
                              <span style={{color: 'white', fontSize: '14px'}}>
                                {modelName.toUpperCase()}
                              </span>
                              <span style={{color: '#4CAF50', fontSize: '14px', fontWeight: 'bold'}}>
                                {(prob * 100).toFixed(1)}%
                              </span>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                )}
                
                {/* Feature Importance for All Models */}
                <AllModelsFeatureImportance />
              </div>
            </div>
            
            <div className="predict-right">
              <RAGPipeline />
            </div>
          </div>
        </section>
        
                 <section className="database-section" id="database">
           <FighterDatabase />
         </section>


      </main>
             <footer id="contact">
         <div className="footer-content">
           <div className="footer-section">
                          <h3>FightMetricsAI</h3>
             <p>AI-Driven ML & RAG Analytics for Smarter UFC Picks</p>
             <p style={{color: '#ccc', fontSize: '0.9rem', marginTop: '10px'}}>By Adam Walid</p>
           </div>
           
           <div className="footer-section">
             <h3>Contact & Connect</h3>
             <div className="contact-links">
               <a 
                 href="https://adam-portfolio-website-git-main-adamwalid64s-projects.vercel.app/" 
                 target="_blank" 
                 rel="noopener noreferrer"
                 className="contact-link"
               >
                 <span className="contact-icon">🌐</span>
                 Portfolio
               </a>
               <a 
                 href="https://www.linkedin.com/in/adamwalid/" 
                 target="_blank" 
                 rel="noopener noreferrer"
                 className="contact-link"
               >
                 <span className="contact-icon">💼</span>
                 LinkedIn
               </a>
                               <a 
                  href="https://github.com/adamwalid64" 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="contact-link"
                >
                  <span className="contact-icon">💻</span>
                  GitHub
                </a>
             </div>
           </div>
           
           <div className="footer-section">
             <h3>About</h3>
             <p>Advanced machine learning models trained on decades of UFC data, combined with real-time sentiment analysis for comprehensive fight predictions.</p>
           </div>
         </div>
       </footer>
    </div>
  );
}

export default App;