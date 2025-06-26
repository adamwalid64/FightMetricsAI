import { useState, useEffect } from 'react';
import { Bar } from 'react-chartjs-2';
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

function FeatureImportanceChart() {
  const [chartData, setChartData] = useState({ labels: [], values: [] });

  useEffect(() => {
    fetch('http://localhost:5000/feature-importance')
      .then((res) => res.json())
      .then((data) => {
        setChartData({ labels: data.features, values: data.scores });
      });
  }, []);

  const data = {
    labels: chartData.labels,
    datasets: [
      {
        label: 'Importance',
        data: chartData.values,
        backgroundColor: 'rgba(58,71,80,0.6)',
      },
    ],
  };

  const options = {
    indexAxis: 'y',
    responsive: true,
    animation: {
      duration: 1000,
    },
    plugins: {
      legend: { display: false },
      title: {
        display: true,
        text: 'XGBoost Feature Importance',
      },
    },
  };

  return <Bar data={data} options={options} />;
}

export default FeatureImportanceChart;
