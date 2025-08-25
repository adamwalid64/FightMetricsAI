import { useState, useEffect } from 'react';
import './FighterDatabase.css';
import { apiFetch } from './api';

function FighterDatabase() {
  const [fighters, setFighters] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const [fightersPerPage] = useState(25);
  const [error, setError] = useState(null);


  useEffect(() => {
    const fetchFighters = async () => {
      try {
        console.log('Fetching fighter database from backend...');
        const response = await apiFetch('/fighter-data', {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
          },
          mode: 'cors',
        });
        
        console.log('Response status:', response.status);
        console.log('Response headers:', response.headers);
        
        if (response.ok) {
          const data = await response.json();
          console.log('Fighter database loaded:', data.length, 'fighters');
          console.log('Sample fighters:', data.slice(0, 3));
          setFighters(data);
          setError(null);
        } else {
          console.error('Failed to fetch fighter database. Status:', response.status);
          const errorText = await response.text();
          console.error('Error response:', errorText);
          setError(`Failed to load fighter data: ${response.status}`);
        }
      } catch (error) {
        console.error('Error fetching fighter database:', error);
        console.error('Error details:', error.message);
        setError(`Error connecting to server: ${error.message}`);
      } finally {
        setLoading(false);
      }
    };

    fetchFighters();
  }, []);

  // Filter fighters based on search term
  const filteredFighters = fighters.filter(fighter =>
    fighter.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    (fighter.nickname && fighter.nickname.toLowerCase().includes(searchTerm.toLowerCase()))
  );

  // Pagination
  const indexOfLastFighter = currentPage * fightersPerPage;
  const indexOfFirstFighter = indexOfLastFighter - fightersPerPage;
  const currentFighters = filteredFighters.slice(indexOfFirstFighter, indexOfLastFighter);
  const totalPages = Math.ceil(filteredFighters.length / fightersPerPage);

  const handlePageChange = (pageNumber) => {
    setCurrentPage(pageNumber);
  };



  return (
    <div className="fighter-database">
      {loading && (
        <div className="loading">Loading UFC Fighter Database...</div>
      )}
      
      {error && (
        <div className="error">Error: {error}</div>
      )}
      
      {!loading && !error && (
        <>
          <div className="database-header">
            <h2>UFC Fighter Database</h2>
            <p>Complete database of {fighters.length} UFC fighters with detailed statistics</p>
            
            <div className="search-container">
              <input
                type="text"
                placeholder="Search fighters by name or nickname..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="search-input"
              />
              <span className="search-results">
                Showing {filteredFighters.length} of {fighters.length} fighters
              </span>
            </div>
          </div>

          <div className="table-container">
        <table className="fighter-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Name</th>
              <th>Nickname</th>
              <th>Age</th>
              <th>Height</th>
              <th>Weight</th>
              <th>Reach</th>
              <th>Stance</th>
              <th>Record</th>
              <th>SLpM</th>
              <th>Str Acc</th>
              <th>SApM</th>
              <th>Str Def</th>
              <th>TD Avg</th>
              <th>TD Acc</th>
              <th>TD Def</th>
              <th>Sub Avg</th>
            </tr>
          </thead>
          <tbody>
            {currentFighters.map((fighter) => (
              <tr key={fighter.id} className="fighter-row">
                <td>{fighter.id}</td>
                <td className="fighter-name">{fighter.name}</td>
                <td className="fighter-nickname">{fighter.nickname || '-'}</td>
                <td>{fighter.age || '-'}</td>
                <td>{fighter.height || '-'}</td>
                <td>{fighter.weight || '-'}</td>
                <td>{fighter.reach ? `${fighter.reach}"` : '-'}</td>
                <td>{fighter.stance || '-'}</td>
                <td className="fighter-record">
                  {fighter.wins}-{fighter.losses}-{fighter.draws}
                </td>
                <td>{fighter.SLpM ? fighter.SLpM.toFixed(2) : '-'}</td>
                <td>{fighter.Str_Acc ? `${fighter.Str_Acc}%` : '-'}</td>
                <td>{fighter.SApM ? fighter.SApM.toFixed(2) : '-'}</td>
                <td>{fighter.Str_Def ? `${fighter.Str_Def}%` : '-'}</td>
                <td>{fighter.TD_Avg ? fighter.TD_Avg.toFixed(2) : '-'}</td>
                <td>{fighter.TD_Acc ? `${fighter.TD_Acc}%` : '-'}</td>
                <td>{fighter.TD_Def ? `${fighter.TD_Def}%` : '-'}</td>
                <td>{fighter.Sub_Avg ? fighter.Sub_Avg.toFixed(2) : '-'}</td>
              </tr>
            ))}
          </tbody>
        </table>
          </div>

          {totalPages > 1 && (
            <div className="pagination">
              <div className="page-info">
                <div className="page-summary">
                  Page {currentPage} of {totalPages}
                </div>
                <div className="fighters-summary">
                  Showing {((currentPage - 1) * fightersPerPage) + 1}-{Math.min(currentPage * fightersPerPage, filteredFighters.length)} of {filteredFighters.length} fighters
                </div>
              </div>
              

              
              <div className="pagination-controls">
                <button
                  onClick={() => handlePageChange(1)}
                  disabled={currentPage === 1}
                  className="page-btn"
                  title="First page"
                >
                  First
                </button>
                
                <button
                  onClick={() => handlePageChange(currentPage - 1)}
                  disabled={currentPage === 1}
                  className="page-btn"
                >
                  Previous
                </button>
                
                {/* First page */}
                {currentPage > 3 && (
                  <>
                    <button
                      onClick={() => handlePageChange(1)}
                      className="page-btn"
                    >
                      1
                    </button>
                    {currentPage > 4 && <span className="page-ellipsis">...</span>}
                  </>
                )}
                
                {/* Page numbers around current page */}
                {Array.from({ length: Math.min(7, totalPages) }, (_, i) => {
                  const pageNumber = Math.max(1, Math.min(totalPages - 6, currentPage - 3)) + i;
                  if (pageNumber > 0 && pageNumber <= totalPages) {
                    return (
                      <button
                        key={pageNumber}
                        onClick={() => handlePageChange(pageNumber)}
                        className={`page-btn ${currentPage === pageNumber ? 'active' : ''}`}
                      >
                        {pageNumber}
                      </button>
                    );
                  }
                  return null;
                })}
                
                {/* Last page */}
                {currentPage < totalPages - 2 && (
                  <>
                    {currentPage < totalPages - 3 && <span className="page-ellipsis">...</span>}
                    <button
                      onClick={() => handlePageChange(totalPages)}
                      className="page-btn"
                    >
                      {totalPages}
                    </button>
                  </>
                )}
                
                <button
                  onClick={() => handlePageChange(currentPage + 1)}
                  disabled={currentPage === totalPages}
                  className="page-btn"
                >
                  Next
                </button>
                
                <button
                  onClick={() => handlePageChange(totalPages)}
                  disabled={currentPage === totalPages}
                  className="page-btn"
                  title="Last page"
                >
                  Last
                </button>
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
}

export default FighterDatabase; 