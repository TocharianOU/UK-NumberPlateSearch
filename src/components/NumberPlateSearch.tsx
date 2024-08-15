import React, { useState } from 'react';
import SearchModule from './SearchModule';
import KeywordSearch from './KeywordSearch';

const sampleData = {
    prefix: [
        { plate: 'A1 ABC', price: '£1,000', type: '1num' },
        { plate: 'B2 DEF', price: '£2,000', type: '1num' },
        { plate: 'C3 GHI', price: '£3,000', type: '1num' },
        { plate: 'D12 JKL', price: '£4,000', type: '2num' },
        { plate: 'E34 MNO', price: '£5,000', type: '2num' },
        { plate: 'F56 PQR', price: '£6,000', type: '2num' },
        { plate: 'G123 STU', price: '£7,000', type: '3num' },
        { plate: 'H456 VWX', price: '£8,000', type: '3num' },
        { plate: 'I789 YZ', price: '£9,000', type: '3num' },
        { plate: 'J1 KLM', price: '£10,000', type: '1num' },
        { plate: 'K2 NOP', price: '£11,000', type: '1num' },
        { plate: 'L3 QRS', price: '£12,000', type: '1num' }
    ],
    newStyle: [
        { plate: 'AB12 XYZ', price: '£4,299', type: '1num' },
        { plate: 'CD34 HIJ', price: '£9,999', type: '2num' },
        { plate: 'EF56 KLM', price: '£15,499', type: '3num' },
        { plate: 'GH78 NOP', price: '£20,299', type: '1num' },
        { plate: 'IJ90 QRS', price: '£25,999', type: '2num' },
        { plate: 'KL12 TUV', price: '£30,499', type: '3num' },
        { plate: 'MN34 WXY', price: '£35,199', type: '1num' },
        { plate: 'OP56 ZAB', price: '£40,299', type: '2num' },
        { plate: 'QR78 CDE', price: '£45,399', type: '3num' }
    ],
    suffix: [
        { plate: 'ABC 1D', price: '£10,000', type: '1num' },
        { plate: 'DEF 2G', price: '£11,000', type: '1num' },
        { plate: 'GHI 3J', price: '£12,000', type: '1num' },
        { plate: 'JKL 45K', price: '£13,000', type: '2num' },
        { plate: 'MNO 67L', price: '£14,000', type: '2num' },
        { plate: 'PQR 89M', price: '£15,000', type: '2num' },
        { plate: 'STU 123N', price: '£16,000', type: '3num' },
        { plate: 'VWX 456O', price: '£17,000', type: '3num' },
        { plate: 'YZ 789P', price: '£18,000', type: '3num' },
        { plate: 'ABC 4D', price: '£19,000', type: '1num' },
        { plate: 'DEF 5G', price: '£20,000', type: '1num' },
        { plate: 'GHI 6J', price: '£21,000', type: '1num' }
    ]
};

const NumberPlateSearch: React.FC = () => {
    const [prefixPattern, setPrefixPattern] = useState<string[]>(new Array(7).fill(''));
    const [newStylePattern, setNewStylePattern] = useState<string[]>(new Array(7).fill(''));
    const [suffixPattern, setSuffixPattern] = useState<string[]>(new Array(7).fill(''));
    const [keyword, setKeyword] = useState<string>('');
    const [searchResults, setSearchResults] = useState({
        prefix: sampleData.prefix,
        newStyle: sampleData.newStyle,
        suffix: sampleData.suffix
    });

    const handleSearch = (e: React.ChangeEvent<HTMLSelectElement>, index: number, setPattern: React.Dispatch<React.SetStateAction<string[]>>) => {
        const newPattern = [...prefixPattern];
        newPattern[index] = e.target.value;
        setPattern(newPattern);
    };

    const handleKeywordSearch = (keyword: string) => {
        setKeyword(keyword);
        const filteredResults = {
            prefix: sampleData.prefix.filter(item => item.plate.includes(keyword.toUpperCase())),
            newStyle: sampleData.newStyle.filter(item => item.plate.includes(keyword.toUpperCase())),
            suffix: sampleData.suffix.filter(item => item.plate.includes(keyword.toUpperCase()))
        };
        setSearchResults(filteredResults);
    };

    const renderThreeColumnsInBox = (title: string, data: { plate: string, price: string, type: string }[]) => {
        const columns = ['1num', '2num', '3num'].map(type => data.filter(item => item.type === type));
        const hasData = columns.map(column => column.length > 0);

        return (
            <div className="result-section">
                <h3>{title}</h3>
                <SearchModule
                    title={`${title} Search`}
                    description={`Search by specific characters in ${title.toLowerCase()}.`}
                    pattern={prefixPattern}
                    onSearch={(e, index) => handleSearch(e, index, setPrefixPattern)}
                />
                <div className="results-three-column">
                    {columns.map((column, index) => hasData[index] && (
                        <div key={index} className="column">
                            {column.map((result, resultIndex) => (
                                <div key={resultIndex} className="result-item">
                                    <div className="plate">{result.plate}</div>
                                    <div className="price">{result.price}</div>
                                    <button className="view-plate">View Plate</button>
                                </div>
                            ))}
                        </div>
                    ))}
                </div>
            </div>
        );
    };

    return (
        <div className="number-plate-search">
            <KeywordSearch onSearch={handleKeywordSearch} />
            <div className="search-results">
                {renderThreeColumnsInBox('Prefix Style', searchResults.prefix)}
                {renderThreeColumnsInBox('New Style', searchResults.newStyle)}
                {renderThreeColumnsInBox('Suffix Style', searchResults.suffix)}
            </div>
            <div className="bottom-filler"></div>
        </div>
    );
};

export default NumberPlateSearch;
