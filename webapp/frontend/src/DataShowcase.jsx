import { useState, useEffect } from 'react';
import './DataShowcase.css';

const DataShowcase = () => {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [currentPage, setCurrentPage] = useState(1);
  const [searchTerm, setSearchTerm] = useState('');
  const [sortField, setSortField] = useState('name');
  const [sortDirection, setSortDirection] = useState('asc');
  const [filteredData, setFilteredData] = useState([]);
  const itemsPerPage = 20;

  useEffect(() => {
    fetchData();
  }, []);

  useEffect(() => {
    filterAndSortData();
  }, [data, searchTerm, sortField, sortDirection]);

  const fetchData = async () => {
    try {
      const response = await fetch('http://localhost:5000/fighter-data');
      if (response.ok) {
        const jsonData = await response.json();
        setData(jsonData);
      } else {
        console.error('Failed to fetch data');
      }
    } catch (error) {
      console.error('Error fetching data:', error);
    } finally {
      setLoading(false);
    }
  };

  const filterAndSortData = () => {
    let filtered = data.filter(fighter => 
      fighter.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      fighter.nickname.toLowerCase().includes(searchTerm.toLowerCase())
    );

    filtered.sort((a, b) => {
      let aValue = a[sortField];
      let bValue = b[sortField];
      
      // Handle numeric values
      if (typeof aValue === 'number' && typeof bValue === 'number') {
        return sortDirection === 'asc' ? aValue - bValue : bValue - aValue;
      }
      
      // Handle string values
      aValue = String(aValue || '').toLowerCase();
      bValue = String(bValue || '').toLowerCase();
      
      if (sortDirection === 'asc') {
        return aValue.localeCompare(bValue);
      } else {
        return bValue.localeCompare(aValue);
      }
    });

    setFilteredData(filtered);
    setCurrentPage(1);
  };

  const handleSort = (field) => {
    if (sortField === field) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortDirection('asc');
    }
  };

  const getPageData = () => {
    const startIndex = (currentPage - 1) * itemsPerPage;
    const endIndex = startIndex + itemsPerPage;
    return filteredData.slice(startIndex, endIndex);
  };

  const totalPages = Math.ceil(filteredData.length / itemsPerPage);

  const formatValue = (value) => {
    if (value === null || value === undefined || value === '') {
      return 'N/A';
    }
    if (typeof value === 'number') {
      return value.toFixed(2);
    }
    return value;
  };

  if (loading) {
    return (
      <div className="data-showcase">
        <div className="loading">Loading fighter data...</div>
      </div>
    );
  }

  return (
    <div className="data-showcase">
      <div className="data-header">
        <h2>UFC Fighter Database</h2>
        <p>Browse through {filteredData.length} fighters with detailed statistics</p>
        
        <div className="search-controls">
          <input
            type="text"
            placeholder="Search fighters by name or nickname..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="search-input"
          />
        </div>
      </div>

      <div className="table-container">
        <table className="fighter-table">
          <thead>
            <tr>
              <th onClick={() => handleSort('name')} className="sortable">
                Name {sortField === 'name' && (sortDirection === 'asc' ? '↑' : '↓')}
              </th>
              <th onClick={() => handleSort('nickname')} className="sortable">
                Nickname {sortField === 'nickname' && (sortDirection === 'asc' ? '↑' : '↓')}
              </th>
              <th onClick={() => handleSort('age')} className="sortable">
                Age {sortField === 'age' && (sortDirection === 'asc' ? '↑' : '↓')}
              </th>
              <th onClick={() => handleSort('height')} className="sortable">
                Height {sortField === 'height' && (sortDirection === 'asc' ? '↑' : '↓')}
              </th>
              <th onClick={() => handleSort('weight')} className="sortable">
                Weight {sortField === 'weight' && (sortDirection === 'asc' ? '↑' : '↓')}
              </th>
              <th onClick={() => handleSort('reach')} className="sortable">
                Reach {sortField === 'reach' && (sortDirection === 'asc' ? '↑' : '↓')}
              </th>
              <th onClick={() => handleSort('wins')} className="sortable">
                Wins {sortField === 'wins' && (sortDirection === 'asc' ? '↑' : '↓')}
              </th>
              <th onClick={() => handleSort('losses')} className="sortable">
                Losses {sortField === 'losses' && (sortDirection === 'asc' ? '↑' : '↓')}
              </th>
              <th onClick={() => handleSort('SLpM')} className="sortable">
                SLpM {sortField === 'SLpM' && (sortDirection === 'asc' ? '↑' : '↓')}
              </th>
              <th onClick={() => handleSort('Str_Acc')} className="sortable">
                Str Acc % {sortField === 'Str_Acc' && (sortDirection === 'asc' ? '↑' : '↓')}
              </th>
              <th onClick={() => handleSort('Str_Def')} className="sortable">
                Str Def % {sortField === 'Str_Def' && (sortDirection === 'asc' ? '↑' : '↓')}
              </th>
              <th onClick={() => handleSort('TD_Avg')} className="sortable">
                TD Avg {sortField === 'TD_Avg' && (sortDirection === 'asc' ? '↑' : '↓')}
              </th>
              <th onClick={() => handleSort('Sub_Avg')} className="sortable">
                Sub Avg {sortField === 'Sub_Avg' && (sortDirection === 'asc' ? '↑' : '↓')}
              </th>
            </tr>
          </thead>
          <tbody>
            {getPageData().map((fighter, index) => (
              <tr key={fighter.id || index}>
                <td>{fighter.name || 'N/A'}</td>
                <td>{fighter.nickname || 'N/A'}</td>
                <td>{formatValue(fighter.age)}</td>
                <td>{fighter.height || 'N/A'}</td>
                <td>{formatValue(fighter.weight)}</td>
                <td>{formatValue(fighter.reach)}</td>
                <td>{formatValue(fighter.wins)}</td>
                <td>{formatValue(fighter.losses)}</td>
                <td>{formatValue(fighter.SLpM)}</td>
                <td>{formatValue(fighter.Str_Acc)}%</td>
                <td>{formatValue(fighter.Str_Def)}%</td>
                <td>{formatValue(fighter.TD_Avg)}</td>
                <td>{formatValue(fighter.Sub_Avg)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="pagination">
        <button 
          onClick={() => setCurrentPage(Math.max(1, currentPage - 1))}
          disabled={currentPage === 1}
          className="page-btn"
        >
          Previous
        </button>
        
        <span className="page-info">
          Page {currentPage} of {totalPages} ({filteredData.length} fighters)
        </span>
        
        <button 
          onClick={() => setCurrentPage(Math.min(totalPages, currentPage + 1))}
          disabled={currentPage === totalPages}
          className="page-btn"
        >
          Next
        </button>
      </div>

      <div className="data-info">
        <h3>Data Fields Explained:</h3>
        <ul>
          <li><strong>SLpM:</strong> Significant Strikes Landed per Minute</li>
          <li><strong>Str Acc:</strong> Striking Accuracy Percentage</li>
          <li><strong>Str Def:</strong> Striking Defense Percentage</li>
          <li><strong>TD Avg:</strong> Average Takedowns per 15 minutes</li>
          <li><strong>Sub Avg:</strong> Average Submissions Attempted per 15 minutes</li>
        </ul>
      </div>
    </div>
  );
};

export default DataShowcase; 