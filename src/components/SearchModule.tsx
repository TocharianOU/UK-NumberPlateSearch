import React from 'react';

interface SearchModuleProps {
    title: string;
    description: string;
    pattern: string[];
    onSearch: (e: React.ChangeEvent<HTMLSelectElement>, index: number) => void;
}

const SearchModule: React.FC<SearchModuleProps> = ({ title, description, pattern, onSearch }) => {
    const letters = ['', '*', ...'ABCDEFGHIJKLMNOPQRSTUVWXYZ'];
    const numbers = ['', '*', '-', ...'0123456789'];

    return (
        <div className="search-module">
            <h2>{title}</h2>
            <p>{description}</p>
            <div className="pattern-input">
                {pattern.map((item, index) => (
                    <select key={index} onChange={(e) => onSearch(e, index)}>
                        {index === 0 ? letters.map((char) => (
                            <option key={char} value={char}>
                                {char}
                            </option>
                        )) : (index >= 1 && index <= 3) ? numbers.map((num) => (
                            <option key={num} value={num}>
                                {num}
                            </option>
                        )) : letters.map((char) => (
                            <option key={char} value={char}>
                                {char}
                            </option>
                        ))}
                    </select>
                ))}
            </div>
            <button onClick={() => onSearch({} as React.ChangeEvent<HTMLSelectElement>, 0)}>Search</button>
        </div>
    );
};

export default SearchModule;
