import React from 'react';
import NumberPlateSearch from './components/NumberPlateSearch';

const App: React.FC = () => {
  return (
    <div className="App">
      <header>
        <nav>
          <div className="logo">UK Number Plate Search</div>
          <ul>
            <li><a href="#home">Home</a></li>
            <li><a href="#search">Search Plates</a></li>
            <li><a href="#about">About Us</a></li>
            <li><a href="#contact">Contact Us</a></li>
          </ul>
        </nav>
      </header>
      <main>
        <section id="home">
          <h1>Welcome to the UK Number Plate Search</h1>
          <p>Search and display different styles of UK number plates.</p>
        </section>
        <section id="search">
          <NumberPlateSearch />
        </section>
      </main>
      <footer>
        <p>&copy; 2024 UK Number Plate Search. All rights reserved.</p>
      </footer>
    </div>
  );
};

export default App;
