import { useState, useEffect } from 'react';
import { Bar } from 'react-chartjs-2';
import './AllModelsFeatureImportance.css';
import {
  Chart as ChartJS,
  BarElement,
  CategoryScale,
  LinearScale,
  Title,
  Tooltip,
  Legend
} from 'chart.js';

ChartJS.register(BarElement, CategoryScale, LinearScale, Title, Tooltip, Legend);

function AllModelsFeatureImportance() {
  const [chartData, setChartData] = useState({
    xgboost: { features: [], scores: [] },
    logistic_regression: { features: [], scores: [] },
    catboost: { features: [], scores: [] },
    mlp: { features: [], scores: [] }
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [currentSlide, setCurrentSlide] = useState(1);
  const [isTransitioning, setIsTransitioning] = useState(false);

  useEffect(() => {
    const fetchAllFeatureImportance = async () => {
      try {
        setLoading(true);
        const response = await fetch('http://localhost:5000/feature-importance/all');
        const data = await response.json();
        
        if (response.ok) {
          setChartData({
            xgboost: data.xgboost || { features: [], scores: [] },
            logistic_regression: data.logistic_regression || { features: [], scores: [] },
            catboost: data.catboost || { features: [], scores: [] },
            mlp: data.mlp || { features: [], scores: [] }
          });
          setError(null);
        } else {
          setError('Failed to load feature importance data');
        }
      } catch (err) {
        console.error('Error fetching feature importance:', err);
        setError('Error loading feature importance data');
      } finally {
        setLoading(false);
      }
    };

    fetchAllFeatureImportance();
  }, []);

  const createChartData = (modelData, modelName, color) => {
    return {
      labels: modelData.features || [],
      datasets: [
        {
          label: 'Importance',
          data: modelData.scores || [],
          backgroundColor: color,
          borderColor: color.replace('0.6', '1'),
          borderWidth: 1,
        },
      ],
    };
  };

  const chartOptions = (title) => ({
    indexAxis: 'y',
    responsive: true,
    maintainAspectRatio: false,
    animation: {
      duration: 1000,
    },
    plugins: {
      legend: { 
        display: false 
      },
      title: {
        display: true,
        text: title,
        color: '#fff',
        font: {
          size: 14,
          weight: 'bold'
        }
      },
    },
    scales: {
      x: {
        beginAtZero: true,
        ticks: {
          color: '#ccc',
          font: {
            size: 10
          }
        },
        grid: {
          color: 'rgba(255, 255, 255, 0.1)'
        }
      },
      y: {
        ticks: {
          color: '#ccc',
          font: {
            size: 10
          },
          callback: function(value, index) {
            const label = this.getLabelForValue(value);
            // Shorten feature names for better display
            return label.length > 15 ? label.substring(0, 15) + '...' : label;
          }
        },
        grid: {
          color: 'rgba(255, 255, 255, 0.1)'
        }
      }
    }
  });

  const models = [
    { key: 'logistic_regression', name: 'Logistic Regression', color: 'rgba(40, 167, 69, 0.6)' },
    { key: 'xgboost', name: 'XGBoost', color: 'rgba(0, 123, 255, 0.6)' },
    { key: 'catboost', name: 'CatBoost', color: 'rgba(255, 193, 7, 0.6)' },
    { key: 'mlp', name: 'MLP', color: 'rgba(108, 92, 231, 0.6)' }
  ];

  const goToSlide = (index) => {
    if (isTransitioning || index === currentSlide) return;
    setIsTransitioning(true);
    setCurrentSlide(index);
    setTimeout(() => setIsTransitioning(false), 300);
  };

  if (loading) {
    return (
      <div className="feature-importance-container">
        <h3>Feature Importance Analysis</h3>
        <div className="loading-message">Loading feature importance data...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="feature-importance-container">
        <h3>Feature Importance Analysis</h3>
        <div className="error-message">{error}</div>
      </div>
    );
  }

  return (
    <div className="feature-importance-container">
      <h3>Feature Importance Analysis</h3>
      <p className="feature-explanation">
        These charts show which features each ML model considers most important for predicting fight outcomes.
      </p>
      
      <div className="slideshow-container">
        <div className="slideshow-wrapper">
          <div className={`slide ${isTransitioning ? 'transitioning' : ''}`}>
            <div className="model-chart">
              <div className="chart-wrapper">
                <Bar 
                  data={createChartData(chartData[models[currentSlide].key], models[currentSlide].name, models[currentSlide].color)} 
                  options={chartOptions(`${models[currentSlide].name} Feature Importance`)} 
                />
              </div>
            </div>
          </div>
        </div>
        
        <div className="slideshow-controls">
          <div className="slide-indicators">
            {models.map((model, index) => (
              <button
                key={model.key}
                className={`indicator ${index === currentSlide ? 'active' : ''}`}
                onClick={() => goToSlide(index)}
                disabled={isTransitioning}
                aria-label={`Go to ${model.name} chart`}
                data-model={model.key}
                style={{
                  '--model-color': model.color,
                  '--model-color-solid': model.color.replace('0.6', '1')
                }}
              >
                <span className="indicator-label">{model.name}</span>
              </button>
            ))}
          </div>
        </div>
      </div>
      
      <div className="feature-legend">
        <h4>Feature Definitions:</h4>
        <div className="legend-grid">
          <div className="legend-item">
            <strong>SLpM_diff:</strong> Significant Strikes per Minute difference
          </div>
          <div className="legend-item">
            <strong>SApM_diff:</strong> Significant Strikes Absorbed per Minute difference
          </div>
          <div className="legend-item">
            <strong>sig_str_acc_diff:</strong> Significant Strike Accuracy difference
          </div>
          <div className="legend-item">
            <strong>td_acc_diff:</strong> Takedown Accuracy difference
          </div>
          <div className="legend-item">
            <strong>str_def_diff:</strong> Strike Defense difference
          </div>
          <div className="legend-item">
            <strong>td_def_diff:</strong> Takedown Defense difference
          </div>
          <div className="legend-item">
            <strong>sub_avg_diff:</strong> Submission Average difference
          </div>
          <div className="legend-item">
            <strong>td_avg_diff:</strong> Takedown Average difference
          </div>
          <div className="legend-item">
            <strong>age_diff:</strong> Age difference
          </div>
          <div className="legend-item">
            <strong>height_diff:</strong> Height difference
          </div>
          <div className="legend-item">
            <strong>reach_diff:</strong> Reach difference
          </div>
          <div className="legend-item">
            <strong>wins_diff:</strong> Wins difference
          </div>
          <div className="legend-item">
            <strong>losses_diff:</strong> Losses difference
          </div>
        </div>
      </div>
    </div>
  );
}

export default AllModelsFeatureImportance;
