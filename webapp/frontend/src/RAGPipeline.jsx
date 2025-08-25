import { useState } from 'react';
import './RAGPipeline.css';
import redroboNews from '../img/redrobo-news.png';
import blueroboNews from '../img/bluerobo-news.png';
import scrapeGif from '../img/scrape_gif.webm';
import twitterIcon from '../img/media_icons/twitter.svg';
import redditIcon from '../img/media_icons/reddit.svg';
import tiktokIcon from '../img/media_icons/tik-tok.svg';
import yahooIcon from '../img/media_icons/yahoo.svg';
import { apiFetch } from './api';

function RAGPipeline() {
  const [response, setResponse] = useState('');
  const [loading, setLoading] = useState(false);
  const [fighter1, setFighter1] = useState('');
  const [fighter2, setFighter2] = useState('');
  const [progress, setProgress] = useState(0);
  const [currentStep, setCurrentStep] = useState('');
  const [currentMessage, setCurrentMessage] = useState('');
  const [progressSteps] = useState([
    { id: 'scraping', label: 'Scraping news articles', description: 'Searching for recent news about the fighters (0-50%)' },
    { id: 'loading', label: 'Loading sentiment data', description: 'Processing and organizing scraped articles (50-75%)' },
    { id: 'analysis', label: 'Running RAG analysis', description: 'Generating expert fight predictions (75-100%)' }
  ]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!fighter1.trim() || !fighter2.trim()) {
      setResponse('Please enter both fighter names.');
      return;
    }

    setLoading(true);
    setProgress(0);
    setCurrentStep('scraping');
    setCurrentMessage('');
    setResponse('');

    try {
      // Use fetch with streaming for real-time progress updates
      const response = await apiFetch('/rag-query-progress', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          fighter1: fighter1,
          fighter2: fighter2
        }),
      });

      if (response.ok) {
        const reader = response.body.getReader();
        const decoder = new TextDecoder();

        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          const chunk = decoder.decode(value);
          const lines = chunk.split('\n');

          for (const line of lines) {
            if (line.startsWith('data: ')) {
              try {
                const data = JSON.parse(line.slice(6));
                
                // Update progress, current step, and message
                setProgress(data.progress);
                setCurrentStep(data.step);
                if (data.message) {
                  setCurrentMessage(data.message);
                }
                
                // If we have a final response, set it
                if (data.response) {
                  setResponse(data.response);
                  setLoading(false);
                  setProgress(0);
                  setCurrentStep('');
                  setCurrentMessage('');
                  return;
                }
              } catch (error) {
                console.error('Error parsing SSE data:', error);
              }
            }
          }
        }
      } else {
        const errorText = await response.text();
        setResponse(`Error: ${response.status} - ${errorText}`);
      }
    } catch (error) {
      setResponse(`Error: Connection failed - ${error.message}`);
    } finally {
      setLoading(false);
      setProgress(0);
      setCurrentStep('');
      setCurrentMessage('');
    }
  };

  return (
         <div className="rag-pipeline">
       <div className="title-section">
         <div className="icon-container">
           <video 
             src={scrapeGif} 
             autoPlay 
             loop 
             muted 
             id="rag-prediction-icon"
             title="Data Scraping Process Demo"
           />
         </div>
         <h3>RAG Fight Analysis</h3>
       </div>
      <p className="tool-description">
      Skip hours of research—instantly analyze the latest news and fighter sentiment with Retrieval-Augmented Generation (RAG), then pair it with an ensemble of advanced machine learning models trained on decades of UFC stats to deliver context-aware fight predictions
      </p>
      
      <form onSubmit={handleSubmit} className="rag-form">
        <div className="fighter-selection">
          <div className="fighter-input">
            <div className="fighter-image">
              <img src={redroboNews} alt="Redrobo News" className="robofighter-image" />
            </div>
            <input
              list="fighter-options-rag"
              placeholder="Fighter One"
              value={fighter1}
              onChange={(e) => setFighter1(e.target.value)}
            />
          </div>
          <span className="vs">vs</span>
          <div className="fighter-input">
            <div className="fighter-image">
              <img src={blueroboNews} alt="Bluerobo News" className="robofighter-image" />
            </div>
            <input
              list="fighter-options-rag"
              placeholder="Fighter Two"
              value={fighter2}
              onChange={(e) => setFighter2(e.target.value)}
            />
          </div>
        </div>
        
        {!loading && (
          <button type="submit" disabled={!fighter1.trim() || !fighter2.trim()}>
            Analyze
          </button>
        )}
        
        {/* RAG Analysis Result - positioned right after analyze button */}
        {response && !loading && (
          <div className="rag-response">
            <h4>Analysis Result:</h4>
            <div className="response-content">
              {response}
            </div>
          </div>
        )}
        
                 <datalist id="fighter-options-rag">
           <option value="Enter fighter names manually" />
         </datalist>
       </form>

       {/* Loading bar and progress - positioned above RAG Workflow */}
       {loading && (
         <div className="loading-container">
           <div className="loading-header">Processing RAG Analysis</div>
           <div className="progress-bar">
             <div className="progress-fill" style={{ width: `${progress}%` }}></div>
           </div>
           <div className="progress-text">{Math.round(progress)}% Complete</div>
           
           {/* Current detailed message */}
           {currentMessage && (
             <div className="progress-message">
               <div className="current-operation">{currentMessage}</div>
             </div>
           )}
           
           <div className="progress-steps">
              {progressSteps.map((step) => {
                let isCompleted = false;
                let isCurrent = false;
                let isPending = false;
                
                // Determine step status based on progress and current step
                if (step.id === 'scraping') {
                  isCompleted = progress > 50;
                  isCurrent = currentStep === 'scraping' && progress <= 50;
                  isPending = progress < 0;
                } else if (step.id === 'loading') {
                  isCompleted = progress > 75;
                  isCurrent = currentStep === 'loading' && progress > 50 && progress <= 75;
                  isPending = progress <= 50;
                } else if (step.id === 'analysis') {
                  isCompleted = progress === 100;
                  isCurrent = currentStep === 'analysis' && progress > 75 && progress < 100;
                  isPending = progress <= 75;
                }
                
                return (
                  <div 
                    key={step.id} 
                    className={`progress-step ${isCompleted ? 'completed' : isCurrent ? 'current' : 'pending'}`}
                  >
                    <div className={`step-indicator ${isCompleted ? 'completed' : isCurrent ? 'current' : ''}`}></div>
                    <div>
                      <div>{step.label}</div>
                      <div style={{ fontSize: '0.7rem', opacity: 0.7 }}>
                        {isCurrent ? step.description : ''}
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
         </div>
       )}

                <div className="pipeline-info">
           <h4>RAG Workflow:</h4>
           <div className="workflow-grid">
             <div className="workflow-item">
               <strong>1. Fighter Input:</strong> Enter two fighter names for analysis
             </div>
             <div className="workflow-item">
               <strong>2. Data Scraping:</strong> Automatically scrapes news articles about the upcoming fight
             </div>
             <div className="workflow-item">
               <strong>3. Data Processing:</strong> Loads and chunks the scraped sentiment data
             </div>
             <div className="workflow-item">
               <strong>4. RAG Analysis:</strong> Runs expert analysis using LLM with retrieved documents
             </div>
           </div>
                  </div>

                  <div className="sources-info">
                    <h4>Frequently Scraped Sources:</h4>
                    <div className="sources-grid">
                                             <div className="source-category">
                         <h5>Official Sources</h5>
                         <div className="source-list">
                           <div className="source-item">
                             <span className="source-icon">🏆</span>
                             <span className="source-name">UFC.com</span>
                           </div>
                           <div className="source-item">
                             <span className="source-icon">📺</span>
                             <span className="source-name">ESPN</span>
                           </div>
                           <div className="source-item">
                             <span className="source-icon">📰</span>
                             <span className="source-name">Sports Illustrated</span>
                           </div>
                           <div className="source-item">
                             <span className="source-icon">📺</span>
                             <span className="source-name">CBS News</span>
                           </div>
                           <div className="source-item">
                             <span className="source-icon">📰</span>
                             <span className="source-name">Yahoo Sports</span>
                           </div>
                         </div>
                       </div>
                      
                                             <div className="source-category">
                         <h5>Fan Websites & Media</h5>
                         <div className="source-list">
                           <div className="source-item">
                             <span className="source-icon">🥊</span>
                             <span className="source-name">Bloody Elbow</span>
                           </div>
                           <div className="source-item">
                             <span className="source-icon">📊</span>
                             <span className="source-name">Tapology</span>
                           </div>
                           <div className="source-item">
                             <span className="source-icon">🔥</span>
                             <span className="source-name">MMA Mania</span>
                           </div>
                           <div className="source-item">
                             <span className="source-icon">🎯</span>
                             <span className="source-name">Outkick</span>
                           </div>
                           <div className="source-item">
                             <span className="source-icon">📰</span>
                             <span className="source-name">MMA Junkie</span>
                           </div>
                         </div>
                       </div>
                      
                                            
                      <div className="source-category">
                         <h5>Social Media</h5>
                         <div className="source-list">
                           <div className="source-item">
                             <span className="source-icon">🐦</span>
                             <span className="source-name">Twitter</span>
                           </div>
                           <div className="source-item">
                             <span className="source-icon">🎵</span>
                             <span className="source-name">TikTok</span>
                           </div>
                         </div>
                       </div>
                      
                      <div className="source-category">
                         <h5>Content & Community</h5>
                         <div className="source-list">
                           <div className="source-item">
                             <span className="source-icon">📹</span>
                             <span className="source-name">YouTube</span>
                           </div>
                           <div className="source-item">
                             <span className="source-icon">💬</span>
                             <span className="source-name">Reddit</span>
                           </div>
                         </div>
                       </div>
                    </div>
                    
                    <div className="sources-note">
                      <p>
                        <strong>Note:</strong> Our automated scraping system continuously monitors these sources to gather the latest news, 
                        fighter statements, expert predictions, and community sentiment for comprehensive fight analysis.
                      </p>
                    </div>
                  </div>
    </div>
  );
}

export default RAGPipeline; 