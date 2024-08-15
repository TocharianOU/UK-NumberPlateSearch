import React, { useState } from 'react';

interface KeywordSearchProps {
    onSearch: (keyword: string) => void;
}

const KeywordSearch: React.FC<KeywordSearchProps> = ({ onSearch }) => {
    const [keyword, setKeyword] = useState('');

    const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        setKeyword(e.target.value.toUpperCase()); // 强制将输入转换为大写
    };

    const handleSearchClick = () => {
        onSearch(keyword);
    };

    return (
        <div className="keyword-search">
            <h2>Keyword Search</h2>
            <input
                type="text"
                value={keyword}
                onChange={handleInputChange}
                placeholder="Enter keyword..."
            />
            <button onClick={handleSearchClick}>Search</button>
        </div>
    );
};

export default KeywordSearch;
