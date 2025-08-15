import React, { useState, useRef, useEffect } from 'react';
import './FighterDropdown.css';

const FighterDropdown = ({ 
  fighters, 
  value, 
  onChange, 
  placeholder, 
  fighterImage,
  altText 
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [filteredFighters, setFilteredFighters] = useState(fighters);
  const dropdownRef = useRef(null);

  useEffect(() => {
    setFilteredFighters(fighters);
  }, [fighters]);

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setIsOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleSearch = (searchValue) => {
    setSearchTerm(searchValue);
    if (searchValue.trim() === '') {
      setFilteredFighters(fighters);
    } else {
      const filtered = fighters.filter(fighter =>
        fighter.toLowerCase().includes(searchValue.toLowerCase())
      );
      setFilteredFighters(filtered);
    }
  };

  const handleFighterSelect = (fighter) => {
    onChange(fighter);
    setSearchTerm('');
    setFilteredFighters(fighters);
    setIsOpen(false);
  };

  const handleInputClick = () => {
    setIsOpen(true);
    setSearchTerm('');
    setFilteredFighters(fighters);
  };

  const handleInputFocus = () => {
    setIsOpen(true);
    setSearchTerm('');
    setFilteredFighters(fighters);
  };

  return (
    <div className="fighter-dropdown" ref={dropdownRef}>
      <div className="fighter-input">
        <div className="fighter-image">
          <img src={fighterImage} alt={altText} className="robofighter-image" />
        </div>
        <input
          type="text"
          placeholder={placeholder}
          value={value || ''}
          onChange={(e) => onChange(e.target.value)}
          onClick={handleInputClick}
          onFocus={handleInputFocus}
          readOnly
          className="fighter-search-input"
        />
      </div>
      
      {isOpen && (
        <div className="dropdown-menu">
          <div className="custom-search-container">
            <input
              type="text"
              placeholder="Search fighters..."
              value={searchTerm}
              onChange={(e) => handleSearch(e.target.value)}
              className="custom-search-input"
              autoFocus
            />
          </div>
          <div className="dropdown-options">
            {filteredFighters.length > 0 ? (
              filteredFighters.map((fighter, index) => (
                <div
                  key={index}
                  className="dropdown-option"
                  onClick={() => handleFighterSelect(fighter)}
                >
                  {fighter}
                </div>
              ))
            ) : (
              <div className="no-results">No fighters found</div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default FighterDropdown;
