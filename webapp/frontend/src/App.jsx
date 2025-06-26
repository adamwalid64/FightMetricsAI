import { useState, useEffect } from 'react';
import './App.css';

function App() {
  const [fighterOne, setFighterOne] = useState('');
  const [fighterTwo, setFighterTwo] = useState('');
  const [inputs, setInputs] = useState('');
  const [prediction, setPrediction] = useState(null);
  const [nameMessage, setNameMessage] = useState('');

  useEffect(() => {
    const canvas = document.getElementById('decision-canvas');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    let animationFrame;

    function resize() {
      canvas.width = canvas.offsetWidth;
      canvas.height = canvas.offsetHeight;
    }

    window.addEventListener('resize', resize);
    resize();

    const titles = [
      'Striking Accuracy',
      'Takedown Defense',
      'KO Rate',
      'SLpM',
      'Reach',
      'Submission Avg',
      'Guard Passing',
      'Ground Control',
    ];

    const shapes = ['circle', 'square', 'triangle'];
    const numNodes = 30;
    const nodes = [];
    const minDistance = 60; // keep nodes spaced so labels don't overlap

    for (let i = 0; i < numNodes; i++) {
      let x, y, attempts = 0;
      do {
        x = Math.random() * canvas.width;
        y = Math.random() * canvas.height;
        attempts++;
      } while (
        attempts < 100 &&
        nodes.some((n) => Math.hypot(n.x - x, n.y - y) < minDistance)
      );

      nodes.push({
        x,
        y,
        value: (50 + Math.random() * 50).toFixed(1),
        title: titles[Math.floor(Math.random() * titles.length)],
        shape: shapes[i % shapes.length],
      });
    }

    const edges = [];
    nodes.forEach((from) => {
      // Slightly reduce the number of edges created between nodes
      const connectionCount = 1 + Math.floor(Math.random() * 3); // 1-3 connections
      for (let i = 0; i < connectionCount; i++) {
        let to = nodes[Math.floor(Math.random() * numNodes)];
        if (to === from) continue;
        edges.push([from, to]);
      }
    });

    let offset = 0;
    const speed = 0.5;

    function drawNetwork(xOffset) {
      edges.forEach(([from, to]) => {
        ctx.beginPath();
        ctx.moveTo(from.x + xOffset, from.y);
        ctx.lineTo(to.x + xOffset, to.y);
        ctx.stroke();
      });

      nodes.forEach((node) => {
        const x = node.x + xOffset;
        ctx.beginPath();
        if (node.shape === 'square') {
          ctx.rect(x - 5, node.y - 5, 10, 10);
        } else if (node.shape === 'triangle') {
          ctx.moveTo(x, node.y - 6);
          ctx.lineTo(x - 5, node.y + 5);
          ctx.lineTo(x + 5, node.y + 5);
          ctx.closePath();
        } else {
          ctx.arc(x, node.y, 5, 0, Math.PI * 2);
        }
        ctx.fill();
        ctx.stroke();
        ctx.fillText(`${node.title} ${node.value}%`, x + 8, node.y + 3);
      });
    }

    function draw() {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      ctx.strokeStyle = 'rgba(255,255,255,0.3)';
      ctx.fillStyle = 'rgba(255,255,255,0.8)';

      offset += speed;
      if (offset > canvas.width) offset = 0;

      drawNetwork(offset);
      drawNetwork(offset - canvas.width);
      drawNetwork(offset + canvas.width);

      animationFrame = requestAnimationFrame(draw);
    }

    draw();

    return () => {
      window.removeEventListener('resize', resize);
      cancelAnimationFrame(animationFrame);
    };
  }, []);

  const handleSubmit = async () => {
    try {
      const res = await fetch('http://localhost:5000/predict', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          fighterOne,
          fighterTwo
        })
      });
      const data = await res.json();
      setPrediction(data.prediction);
    } catch (err) {
      console.error(err);
    }
  };


  return (
    <div className="app">
      <header className="site-header">
        <div className="logo">FightMetricsAI<span className="logo-icon" /></div>
        <nav>
          <ul>
            <li><a href="#features">Features</a></li>
            <li><a href="#predict">Predict</a></li>
            <li><a href="#contact">Contact</a></li>
          </ul>
        </nav>
      </header>
      <main>
        <section className="hero">
          <canvas id="decision-canvas" className="decision-canvas"></canvas>
          <div className="hero-content">
            <h1>Unlock Fight Insights</h1>
            <p>Use AI-driven analytics to analyze UFC stats and predict outcomes.</p>
            <a className="cta-button" href="#predict">Get Started</a>
          </div>
        </section>
        <section className="features" id="features">
          <h2>Features</h2>
          <div className="feature-list">
            <div className="feature">
              <h3>Comprehensive Stats</h3>
              <p>Access detailed fighter statistics scraped from multiple sources.</p>
            </div>
            <div className="feature">
              <h3>Machine Learning</h3>
              <p>Advanced models help forecast fight results based on data.</p>
            </div>
            <div className="feature">
              <h3>Interactive Dashboard</h3>
              <p>Visualize metrics and predictions in a clean dashboard.</p>
            </div>
          </div>
        </section>
        <section className="predict-section" id="predict">
          <h2>Try the Predictor</h2>
          <div className="predict-cards">
            <div className="predict-card left-card">
              <h3>Live Fight Prediction</h3>
              <div className="fighter-selection">
                <div className="fighter-input">
                  <div className="fighter-image"></div>
                  <input
                    list="fighter-options"
                    placeholder="Fighter One"
                    value={fighterOne}
                    onChange={(e) => setFighterOne(e.target.value)}
                  />
                </div>
                <span className="vs">vs</span>
                <div className="fighter-input">
                  <div className="fighter-image"></div>
                  <input
                    list="fighter-options"
                    placeholder="Fighter Two"
                    value={fighterTwo}
                    onChange={(e) => setFighterTwo(e.target.value)}
                  />
                </div>
              </div>
              <button onClick={handleSubmit}>Predict</button>
              {nameMessage && (
                <p className="prediction-result">{nameMessage}</p>
              )}
              <datalist id="fighter-options">
                <option value="Shamil Abdurakhimov" />
                <option value="Papy Abedi" />
                <option value="Ricardo Abreu" />
                <option value="Israel Adesanya" />
                <option value="Mohamed Ado" />
                <option value="Mariya Agapova" />
                <option value="Jessica Aguilar" />
                <option value="Jesus Aguilar" />
                <option value="Nick Aguirre" />
                <option value="Omari Akhmedov" />
                <option value="Yoshihiro Akiyama" />
                <option value="Amir Albazi" />
                <option value="Aleksandra Albu" />
                <option value="Iuri Alcantara" />
                <option value="Ildemar Alcantara" />
                <option value="Irene Aldana" />
                <option value="Jose Aldo" />
                <option value="Irina Alekseeva" />
                <option value="Talita Alencar" />
                <option value="Jim Alers" />
                <option value="John Alessio" />
                <option value="Marcio Alexandre Junior" />
                <option value="Olaf Alfonso" />
                <option value="Bill Algeo" />
                <option value="Ikram Aliskerov" />
                <option value="John Allan" />
                <option value="Arnold Allen" />
                <option value="Brendan Allen" />
                <option value="Asu Almabayev" />
                <option value="Ricardo Almeida" />
                <option value="Jailton Almeida" />
                <option value="Sarah Alpar" />
                <option value="Ali AlQaisi" />
                <option value="Eddie Alvarez" />
                <option value="Thiago Alves" />
                <option value="Warlley Alves" />
                <option value="Rafael Alves" />
                <option value="Sam Alvey" />
                <option value="Jimmy Ambriz" />
                <option value="Makwan Amirkhani" />
                <option value="Eryk Anders" />
                <option value="Megan Anderson" />
                <option value="Jessica Andrade" />
                <option value="Viscardi Andrade" />
                <option value="Dylan Andrews" />
                <option value="Julius Anglickas" />
                <option value="Chad Anheliger" />
                <option value="Shinya Aoki" />
                <option value="Felipe Arantes" />
                <option value="Igor Araujo" />
                <option value="Viviane Araujo" />
                <option value="Julio Arce" />
                <option value="Andrei Arlovski" />
                <option value="Garrett Armfield" />
                <option value="Austin Arnett" />
                <option value="Ricardo Arona" />
                <option value="Chalid Arrab" />
                <option value="Akbarh Arreola" />
                <option value="Matt Arroyo" />
                <option value="Antonio Arroyo" />
                <option value="Askar Askarov" />
                <option value="Cyril Asker" />
                <option value="Tom Aspinall" />
                <option value="Bruno Assis" />
                <option value="Junior Assuncao" />
                <option value="Raphael Assuncao" />
                <option value="Olivier Aubin-Mercier" />
                <option value="Marcus Aurelio" />
                <option value="Blas Avena" />
                <option value="Julia Avila" />
                <option value="Saad Awad" />
                <option value="Niklas Backstrom" />
                <option value="Seth Baczynski" />
                <option value="Ryan Bader" />
                <option value="Miguel Baeza" />
                <option value="Ali Bagautinov" />
                <option value="Siyar Bahadurzada" />
                <option value="Bryan Baker" />
                <option value="Humberto Bandenay" />
                <option value="Tae Hyun Bang" />
                <option value="Antonio Banuelos" />
                <option value="Renan Barao" />
                <option value="Maycee Barber" />
                <option value="Bryan Barberena" />
                <option value="Dione Barbosa" />
                <option value="Edson Barboza" />
                <option value="Raoni Barcelos" />
                <option value="Daniel Barez" />
                <option value="Luke Barnatt" />
                <option value="Josh Barnett" />
                <option value="Phil Baroni" />
                <option value="Marc-Andre Barriault" />
                <option value="Enrique Barzola" />
                <option value="Javid Basharat" />
                <option value="Farid Basharat" />
                <option value="Austin Bashi" />
                <option value="Shayna Baszler" />
                <option value="Bryan Battle" />
                <option value="Mario Bautista" />
                <option value="Chris Beal" />
                <option value="Chase Beebe" />
                <option value="Lyle Beerbohm" />
                <option value="Mirsad Bektic" />
                <option value="Alan Belcher" />
                <option value="Vitor Belfort" />
                <option value="Rodolfo Bellato" />
                <option value="Marco Beltran" />
                <option value="Joseph Benavidez" />
                <option value="Gabriel Benitez" />
                <option value="Ryan Benoit" />
                <option value="Steve Berger" />
                <option value="Bret Bergmark" />
                <option value="Dennis Bermudez" />
                <option value="Talita Bernardo" />
                <option value="Matt Bessette" />
                <option value="Blake Bilder" />
                <option value="Anthony Birchak" />
                <option value="Michael Bisping" />
                <option value="Jan Blachowicz" />
                <option value="Jason Black" />
                <option value="Brad Blackburn" />
                <option value="Da'Mon Blackshear" />
                <option value="Maximo Blanco" />
                <option value="Tereza Bleda" />
                <option value="Mark Bocek" />
                <option value="Tim Boetsch" />
                <option value="Mandy Bohm" />
                <option value="Gabriel Bonfim" />
                <option value="Stephan Bonnar" />
                <option value="Rogerio Bontorin" />
                <option value="Ray Borg" />
                <option value="Caio Borralho" />
                <option value="Brian Bowles" />
                <option value="Roger Bowling" />
                <option value="Sean Brady" />
                <option value="Ramiz Brahimaj" />
                <option value="Diego Brandao" />
                <option value="Jason Brilz" />
                <option value="Joanderson Brito" />
                <option value="Jonathan Brookins" />
                <option value="Will Brooks" />
                <option value="Jarred Brooks" />
                <option value="Matt Brown" />
                <option value="Mike Brown" />
                <option value="Randy Brown" />
                <option value="Damien Brown" />
                <option value="TJ Brown" />
                <option value="Travis Browne" />
                <option value="Cody Brundage" />
                <option value="Steve Bruno" />
                <option value="Fernando Bruno" />
                <option value="Derek Brunson" />
                <option value="Lukasz Brzeski" />
                <option value="Joaquin Buckley" />
                <option value="Dylan Budka" />
                <option value="Mayra Bueno Silva" />
                <option value="Paul Buentello" />
                <option value="Modestas Bukauskas" />
                <option value="Shane Burgos" />
                <option value="Joshua Burkman" />
                <option value="Mads Burnell" />
                <option value="Kevin Burns" />
                <option value="Gilbert Burns" />
                <option value="Herbert Burns" />
                <option value="Yan Cabral" />
                <option value="Alex Caceres" />
                <option value="Darrion Caldwell" />
                <option value="Cynthia Calvillo" />
                <option value="Fabricio Camoes" />
                <option value="Chris Camozzi" />
                <option value="Will Campuzano" />
                <option value="Chico Camus" />
                <option value="Carlos Candelario" />
                <option value="Luiz Cane" />
                <option value="Guido Cannetti" />
                <option value="Steve Cantwell" />
                <option value="Phil Caracappa" />
                <option value="Gina Carano" />
                <option value="Bryan Caraway" />
                <option value="Chris Cariaso" />
                <option value="Antonio Carlos Junior" />
                <option value="Spike Carlyle" />
                <option value="Francis Carmont" />
                <option value="Liz Carmouche" />
                <option value="Roan Carneiro" />
                <option value="Ariane Carnelossi" />
                <option value="Luana Carolina" />
                <option value="Clayton Carpenter" />
                <option value="Johnny Case" />
                <option value="Kevin Casey" />
                <option value="Cortney Casey" />
                <option value="John Castaneda" />
                <option value="Danny Castillo" />
                <option value="Nick Catone" />
                <option value="Gesias Cavalcante" />
                <option value="Rafael Cavalcante" />
                <option value="Magnus Cedenblad" />
                <option value="Henry Cejudo" />
                <option value="Adam Cella" />
                <option value="Katlyn Cerminara" />
                <option value="Donald Cerrone" />
                <option value="Luan Chagas" />
                <option value="Alex Chambers" />
                <option value="Michael Chandler" />
                <option value="Morgan Charriere" />
                <option value="Macy Chiasson" />
                <option value="Giga Chikadze" />
                <option value="Khamzat Chimaev" />
                <option value="Mu Bae Choi" />
                <option value="Dooho Choi" />
                <option value="John Cholish" />
                <option value="Ryo Chonan" />
                <option value="Hannah Cifers" />
                <option value="Logan Clark" />
                <option value="Heather Clark" />
                <option value="Devin Clark" />
                <option value="Jessica-Rose Clark" />
                <option value="Mitch Clarke" />
                <option value="Rich Clementi" />
                <option value="Marloes Coenen" />
                <option value="Mark Coleman" />
                <option value="Clay Collard" />
                <option value="Jamie Colleen" />
                <option value="Jake Collier" />
                <option value="Carlos Condit" />
                <option value="Tristan Connelly" />
                <option value="Amanda Cooper" />
                <option value="Daniel Cormier" />
                <option value="Nora Cornolle" />
                <option value="Waldo Cortes-Acosta" />
                <option value="Tracy Cortez" />
                <option value="Louis Cosce" />
                <option value="Melquizael Costa" />
                <option value="Patrick Cote" />
                <option value="Randy Couture" />
                <option value="Ryan Couture" />
                <option value="Colby Covington" />
                <option value="Paul Craig" />
                <option value="Tim Credeur" />
                <option value="Kevin Croom" />
                <option value="Allen Crowder" />
                <option value="Daron Cruickshank" />
                <option value="Richard Crunkilton" />
                <option value="Jimmy Crute" />
                <option value="Marcio Cruz" />
                <option value="Dominick Cruz" />
                <option value="Zak Cummings" />
                <option value="Patrick Cummins" />
                <option value="Luke Cummo" />
                <option value="Henrique da Silva" />
                <option value="Ariane da Silva" />
                <option value="Alex Da Silva" />
                <option value="Nicolas Dalby" />
                <option value="Aisling Daly" />
                <option value="Rodrigo Damm" />
                <option value="Mac Danzig" />
                <option value="Beneil Dariush" />
                <option value="Kyle Daukaus" />
                <option value="Marcus Davis" />
                <option value="LC Davis" />
                <option value="Phil Davis" />
                <option value="Alexis Davis" />
                <option value="Brandon Davis" />
                <option value="Mike Davis" />
                <option value="Grant Dawson" />
                <option value="Martin Day" />
                <option value="Philip De Fries" />
                <option value="Chris de la Rocha" />
                <option value="Montana De La Rosa" />
                <option value="Mark De La Rosa" />
                <option value="Gloria de Paula" />
                <option value="Reinier de Ridder" />
                <option value="Tom DeBlass" />
                <option value="Shane del Rosario" />
                <option value="Yadier del Valle" />
                <option value="Jack Della Maddalena" />
                <option value="Roland Delorme" />
                <option value="Jon Delos Reyes" />
                <option value="Vanessa Demopoulos" />
                <option value="Thomas Denny" />
                <option value="Mackenzie Dern" />
                <option value="Tony DeSouza" />
                <option value="Rafael Dias" />
                <option value="Hacran Dias" />
                <option value="Nick Diaz" />
                <option value="Nate Diaz" />
                <option value="TJ Dillashaw" />
                <option value="Russell Doane" />
                <option value="Drew Dober" />
                <option value="AJ Dobson" />
                <option value="Joe Doerksen" />
                <option value="Roman Dolidze" />
                <option value="CB Dollaway" />
                <option value="Rafael Dos Anjos" />
                <option value="Junior Dos Santos" />
                <option value="Anderson Dos Santos" />
                <option value="Tiago dos Santos e Silva" />
                <option value="Tomasz Drwal" />
                <option value="Dricus Du Plessis" />
                <option value="Joe Duffy" />
                <option value="Jessamyn Duke" />
                <option value="Sedriques Dumas" />
                <option value="Chris Duncan" />
                <option value="Evan Dunham" />
                <option value="Albert Duraev" />
                <option value="Reuben Duran" />
                <option value="Cody Durden" />
                <option value="Brian Ebersole" />
                <option value="Frankie Edgar" />
                <option value="Johnny Eduardo" />
                <option value="Yves Edwards" />
                <option value="Justin Edwards" />
                <option value="Leon Edwards" />
                <option value="Joselyne Edwards" />
                <option value="Stephanie Egger" />
                <option value="Evan Elder" />
                <option value="Saul Elizondo" />
                <option value="Darren Elkins" />
                <option value="Jake Ellenberger" />
                <option value="Tim Elliott" />
                <option value="Lisa Ellis" />
                <option value="Aaron Ely" />
                <option value="Ramazan Emeev" />
                <option value="Aleksander Emelianenko" />
                <option value="Fedor Emelianenko" />
                <option value="Rob Emerson" />
                <option value="Jamall Emmers" />
                <option value="Josh Emmett" />
                <option value="Steve Erceg" />
                <option value="Julian Erosa" />
                <option value="Efrain Escudero" />
                <option value="Urijah Faber" />
                <option value="Wagnney Fabiano" />
                <option value="Rinat Fakhretdinov" />
                <option value="Maiquel Falcao" />
                <option value="Brodie Farber" />
                <option value="Kalindra Faria" />
                <option value="Paul Felder" />
                <option value="Kevin Ferguson" />
                <option value="Tony Ferguson" />
                <option value="Bibiano Fernandes" />
                <option value="Gabriella Fernandes" />
                <option value="Cezar Ferreira" />
                <option value="Diego Ferreira" />
                <option value="Erisson Ferreira" />
                <option value="Brunno Ferreira" />
                <option value="Drew Fickett" />
                <option value="Deiveson Figueiredo" />
                <option value="Francisco Figueiredo" />
                <option value="Paulo Filho" />
                <option value="Jafel Filho" />
                <option value="Andre Fili" />
                <option value="Mirko Filipovic" />
                <option value="Luigi Fioravanti" />
                <option value="Luiz Firmino" />
                <option value="Spencer Fisher" />
                <option value="Chris Fishgold" />
                <option value="Jon Fitch" />
                <option value="AJ Fletcher" />
                <option value="Nathan Fletcher" />
                <option value="Kenny Florian" />
                <option value="Rob Font" />
                <option value="Jesse Forbes" />
                <option value="Jussier Formiga" />
                <option value="Marcel Fortuna" />
                <option value="Brian Foster" />
                <option value="Hermes Franca" />
                <option value="John Franchi" />
                <option value="Rich Franklin" />
                <option value="Ian Freeman" />
                <option value="Patricio Freire" />
                <option value="Josh Fremd" />
                <option value="Matt Frevola" />
                <option value="Jinh Yu Frey" />
                <option value="Claudia Gadelha" />
                <option value="Mitch Gagnon" />
                <option value="Zelg Galesic" />
                <option value="Mickey Gall" />
                <option value="Marcos Galvao" />
                <option value="Manvel Gamburyan" />
                <option value="Mateusz Gamrot" />
                <option value="Ciryl Gane" />
                <option value="Leonard Garcia" />
                <option value="Edgar Garcia" />
                <option value="Alex Garcia" />
                <option value="Steve Garcia" />
                <option value="Elias Garcia" />
                <option value="Rafa Garcia" />
                <option value="Fernie Garcia" />
                <option value="Pablo Garza" />
                <option value="Kelvin Gastelum" />
                <option value="Melissa Gatto" />
                <option value="Louis Gaudinot" />
                <option value="Shamil Gaziev" />
                <option value="Christos Giagos" />
                <option value="Cody Gibson" />
                <option value="Joseph Gigliotti" />
                <option value="Trevin Giles" />
                <option value="Gregor Gillespie" />
                <option value="Billy Giovanella" />
                <option value="Ricky Glenn" />
                <option value="Loopy Godinez" />
                <option value="Hannah Goldy" />
                <option value="Marcelo Golm" />
                <option value="Denise Gomes" />
                <option value="Frank Gomez" />
                <option value="Takanori Gomi" />
                <option value="William Gomis" />
                <option value="Akihiro Gono" />
                <option value="Gabriel Gonzaga" />
                <option value="Fernando Gonzalez" />
                <option value="Jared Gooden" />
                <option value="Gary Goodridge" />
                <option value="Malcolm Gordon" />
                <option value="Tresean Gore" />
                <option value="Themba Gorimbo" />
                <option value="Jonathan Goulet" />
                <option value="Thibault Gouti" />
                <option value="Wilson Gouveia" />
                <option value="Crosley Gracie" />
                <option value="Renzo Gracie" />
                <option value="Rodrigo Gracie" />
                <option value="Ryan Gracie" />
                <option value="Roger Gracie" />
                <option value="TJ Grant" />
                <option value="Alexa Grasso" />
                <option value="Tony Gravely" />
                <option value="Michael Graves" />
                <option value="King Green" />
                <option value="Gabe Green" />
                <option value="Matt Grice" />
                <option value="Forrest Griffin" />
                <option value="Tyson Griffin" />
                <option value="Max Griffin" />
                <option value="Jordan Griffin" />
                <option value="Josh Grispi" />
                <option value="Vik Grujic" />
                <option value="Mike Grundy" />
                <option value="Shannon Gugerty" />
                <option value="Clay Guida" />
                <option value="Jason Guida" />
                <option value="Melvin Guillard" />
                <option value="John Gunderson" />
                <option value="Jorge Gurgel" />
                <option value="Cody Haddon" />
                <option value="Jake Hadley" />
                <option value="Damir Hadzovic" />
                <option value="Tim Hague" />
                <option value="Uriah Hall" />
                <option value="Dennis Hallman" />
                <option value="Piotr Hallmann" />
                <option value="Brandon Halsey" />
                <option value="James Hammortree" />
                <option value="Joachim Hansen" />
                <option value="Kay Hansen" />
                <option value="Dan Hardy" />
                <option value="Veronica Hardy" />
                <option value="Carlston Harris" />
                <option value="Kayla Harrison" />
                <option value="Dale Hartt" />
                <option value="Clay Harvison" />
                <option value="Justin Haskins" />
                <option value="Daiki Hata" />
                <option value="John Hathaway" />
                <option value="Phil Hawes" />
                <option value="Dustin Hazelett" />
                <option value="James Head" />
                <option value="Pat Healy" />
                <option value="Ryan Healy" />
                <option value="David Heath" />
                <option value="Chris Heatherly" />
                <option value="Ian Heinisch" />
                <option value="Marcin Held" />
                <option value="Dan Henderson" />
                <option value="Benson Henderson" />
                <option value="Johny Hendricks" />
                <option value="Luis Henrique" />
                <option value="Danny Henry" />
                <option value="Victor Henry" />
                <option value="Ed Herman" />
                <option value="Jack Hermansson" />
                <option value="Alexander Hernandez" />
                <option value="Anthony Hernandez" />
                <option value="Carlos Hernandez" />
                <option value="Geane Herrera" />
                <option value="Felice Herrig" />
                <option value="Heath Herring" />
                <option value="Conor Heun" />
                <option value="Marcus Hicks" />
                <option value="Jay Hieron" />
                <option value="Brady Hiestand" />
                <option value="Jason High" />
                <option value="Angela Hill" />
                <option value="Branden Lee Hinkle" />
                <option value="Hatsu Hioki" />
                <option value="Kuniyoshi Hironaka" />
                <option value="Mizuto Hirota" />
                <option value="Sam Hoger" />
                <option value="Andrew Holbrook" />
                <option value="Chris Holdsworth" />
                <option value="Kevin Holland" />
                <option value="Max Holloway" />
                <option value="Gabrielle Holloway" />
                <option value="Holly Holm" />
                <option value="Joseph Holmes" />
                <option value="Kurt Holobaugh" />
                <option value="Paddy Holohan" />
                <option value="Mark Holst" />
                <option value="Scott Holtzman" />
                <option value="Mark Hominick" />
                <option value="Dan Hooker" />
                <option value="Chase Hooper" />
                <option value="Darrell Horcher" />
                <option value="Jeremy Horn" />
                <option value="Chris Horodecki" />
                <option value="Jamey-Lyn Horth" />
                <option value="Matt Horwich" />
                <option value="John Howard" />
                <option value="Austin Hubbard" />
                <option value="Roger Huerta" />
                <option value="Matt Hughes" />
                <option value="Sam Hughes" />
                <option value="Victor Hugo" />
                <option value="Mark Hunt" />
                <option value="Al Iaquinta" />
                <option value="Khadis Ibragimov" />
                <option value="Dan Ige" />
                <option value="Fabiano Iha" />
                <option value="Nassourdine Imavov" />
                <option value="Chris Indich" />
                <option value="Guto Inocente" />
                <option value="Yves Jabouin" />
                <option value="Eugene Jackson" />
                <option value="Quinton Jackson" />
                <option value="Damon Jackson" />
                <option value="Montel Jackson" />
                <option value="Virna Jandiroba" />
                <option value="Dave Jansen" />
                <option value="Keith Jardine" />
                <option value="Rony Jason" />
                <option value="Jasmine Jasudavicius" />
                <option value="Justin Jaynes" />
                <option value="Joanna Jedrzejczyk" />
                <option value="Ryan Jensen" />
                <option value="Baergeng Jieleyisi" />
                <option value="Brett Johns" />
                <option value="Anthony Johnson" />
                <option value="DaMarques Johnson" />
                <option value="Lavar Johnson" />
                <option value="Demetrious Johnson" />
                <option value="Kajan Johnson" />
                <option value="Dashon Johnson" />
                <option value="Jordan Johnson" />
                <option value="Jose Johnson" />
                <option value="Charles Johnson" />
                <option value="Jon Jones" />
                <option value="Justin Jones" />
                <option value="Trevin Jones" />
                <option value="Shawn Jordan" />
                <option value="Saidyokub Kakhramonov" />
                <option value="Kai Kamaka" />
                <option value="Martin Kampmann" />
                <option value="Masanori Kanehara" />
                <option value="Denis Kang" />
                <option value="Kyung Ho Kang" />
                <option value="Manel Kape" />
                <option value="Georgi Karakhanyan" />
                <option value="Alex Karalexis" />
                <option value="Impa Kasanganay" />
                <option value="Nadia Kassem" />
                <option value="Calvin Kattar" />
                <option value="Tatsuya Kawajiri" />
                <option value="Toshiomi Kazama" />
                <option value="Chris Kelades" />
                <option value="Brian Kelleher" />
                <option value="Paul Kelly" />
                <option value="Daniel Kelly" />
                <option value="Tim Kennedy" />
                <option value="Casey Kenney" />
                <option value="Rustam Khabilov" />
                <option value="Sergei Kharitonov" />
                <option value="Aliaskhab Khizriev" />
                <option value="Pannie Kianzad" />
                <option value="Sanae Kikuta" />
                <option value="Jacob Kilburn" />
                <option value="Dong Hyun Kim" />
                <option value="Sangwook Kim" />
                <option value="Rob Kimmons" />
                <option value="Dustin Kimura" />
                <option value="Mike King" />
                <option value="Justine Kish" />
                <option value="Satoru Kitaoka" />
                <option value="Nick Klein" />
                <option value="Jason Knight" />
                <option value="William Knight" />
                <option value="Erik Koch" />
                <option value="Tsuyoshi Kohsaka" />
                <option value="Yuki Kondo" />
                <option value="Cheick Kongo" />
                <option value="Josh Koscheck" />
                <option value="Naoyuki Kotani" />
                <option value="Karolina Kowalkiewicz" />
                <option value="James Krause" />
                <option value="Pascal Krauss" />
                <option value="Kaynan Kruschewsky" />
                <option value="Nikita Krylov" />
                <option value="Anton Kuivanen" />
                <option value="Kiichi Kunimoto" />
                <option value="Leo Kuntz" />
                <option value="Luan Lacerda" />
                <option value="Aspen Ladd" />
                <option value="Ryan LaFlare" />
                <option value="Noad Lahat" />
                <option value="Yohan Lainesse" />
                <option value="Ricardo Lamas" />
                <option value="Jason Lambert" />
                <option value="Jose Landi-Jons" />
                <option value="Nate Landwehr" />
                <option value="Lina Lansberg" />
                <option value="Taylor Lapilus" />
                <option value="Lorenz Larkin" />
                <option value="Brock Larson" />
                <option value="Ilir Latifi" />
                <option value="Jenel Lausa" />
                <option value="Joe Lauzon" />
                <option value="Dan Lauzon" />
                <option value="Tom Lawlor" />
                <option value="Ronnie Lawrence" />
                <option value="Cung Le" />
                <option value="Quang Le" />
                <option value="Jordan Leavitt" />
                <option value="Chris Leben" />
                <option value="Justin Ledet" />
                <option value="Vaughan Lee" />
                <option value="Kevin Lee" />
                <option value="Andrea Lee" />
                <option value="JeongYeong Lee" />
                <option value="ChangHo Lee" />
                <option value="Thales Leites" />
                <option value="Amanda Lemos" />
                <option value="Jesse Lennox" />
                <option value="Nik Lentz" />
                <option value="Valerie Letourneau" />
                <option value="Justin Levens" />
                <option value="Marcus LeVesseur" />
                <option value="Natan Levy" />
                <option value="Liang Na" />
                <option value="Hyun Gyu Lim" />
                <option value="Dhiego Lima" />
                <option value="Andre Lima" />
                <option value="Felipe Lima" />
                <option value="Matt Lindland" />
                <option value="John Lineker" />
                <option value="Lucio Linhares" />
                <option value="Tainara Lisboa" />
                <option value="Dean Lister" />
                <option value="Ryan Loder" />
                <option value="David Loiseau" />
                <option value="Hector Lombard" />
                <option value="Loma Lookboonmee" />
                <option value="Ange Loosa" />
                <option value="Dileno Lopes" />
                <option value="Diego Lopes" />
                <option value="Matthew Lopez" />
                <option value="Gustavo Lopez" />
                <option value="Ian Loveland" />
                <option value="Waylon Lowe" />
                <option value="Lu Kai" />
                <option value="Iasmin Lucindo" />
                <option value="Duane Ludwig" />
                <option value="Vicente Luque" />
                <option value="Travis Lutter" />
                <option value="Jason MacDonald" />
                <option value="Rob MacDonald" />
                <option value="Rory MacDonald" />
                <option value="Ian Machado Garry" />
                <option value="Lyoto Machida" />
                <option value="Reza Madadi" />
                <option value="Don Madge" />
                <option value="Yoshiro Maeda" />
                <option value="Leonardo Mafra" />
                <option value="Vinny Magalhaes" />
                <option value="Caio Magalhaes" />
                <option value="Angela Magana" />
                <option value="Neil Magny" />
                <option value="Rashid Magomedov" />
                <option value="Abus Magomedov" />
                <option value="Zabit Magomedsharipov" />
                <option value="John Maguire" />
                <option value="Demian Maia" />
                <option value="Jennifer Maia" />
                <option value="Islam Makhachev" />
                <option value="Zach Makovsky" />
                <option value="Azat Maksum" />
                <option value="Fabio Maldonado" />
                <option value="Jacob Malkoun" />
                <option value="Mike Malott" />
                <option value="Nate Maness" />
                <option value="Jimi Manuwa" />
                <option value="Cristiano Marcello" />
                <option value="Jose Maria" />
                <option value="Enrique Marin" />
                <option value="Chepe Mariscal" />
                <option value="Ronny Markes" />
                <option value="Randa Markos" />
                <option value="Nate Marquardt" />
                <option value="Carmelo Marrero" />
                <option value="John Marsh" />
                <option value="Eliot Marshall" />
                <option value="Francis Marshall" />
                <option value="Anthony Rocco Martin" />
                <option value="Mallory Martin" />
                <option value="Jonathan Martinez" />
                <option value="Poppies Martinez" />
                <option value="Mana Martinez" />
                <option value="Roque Martinez" />
                <option value="Mike Massenzio" />
                <option value="Jameel Massouh" />
                <option value="Jorge Masvidal" />
                <option value="Daijiro Matsui" />
                <option value="Jean Matsumoto" />
                <option value="Jake Matthews" />
                <option value="Connor Matthews" />
                <option value="Vladimir Matyushenko" />
                <option value="Miranda Maverick" />
                <option value="Nick Maximov" />
                <option value="Gray Maynard" />
                <option value="Gina Mazany" />
                <option value="Sabina Mazo" />
                <option value="Michael McBride" />
                <option value="Molly McCann" />
                <option value="Sean McCorkle" />
                <option value="Danni McCormack" />
                <option value="Tamdan McCrory" />
                <option value="Robert McDaniel" />
                <option value="Michael McDonald" />
                <option value="Drew McFedries" />
                <option value="Court McGee" />
                <option value="Marcus McGhee" />
                <option value="Conor McGregor" />
                <option value="Cory McKenna" />
                <option value="Cody McKenzie" />
                <option value="Terrance McKinney" />
                <option value="Garreth McLellan" />
                <option value="Sara McMann" />
                <option value="James McSweeney" />
                <option value="Tim Means" />
                <option value="Yancy Medeiros" />
                <option value="Emil Meek" />
                <option value="Gerald Meerschaert" />
                <option value="Jordan Mein" />
                <option value="Gilbert Melendez" />
                <option value="Chad Mendes" />
                <option value="Mateus Mendonca" />
                <option value="Alonzo Menifield" />
                <option value="Ivan Menjivar" />
                <option value="Dave Menne" />
                <option value="Yaotzin Meza" />
                <option value="Jonathan Micallef" />
                <option value="David Michaud" />
                <option value="Pat Miletich" />
                <option value="Phillip Miller" />
                <option value="Jason Miller" />
                <option value="Dan Miller" />
                <option value="Jim Miller" />
                <option value="Cole Miller" />
                <option value="Micah Miller" />
                <option value="Juliana Miller" />
                <option value="Darrick Minner" />
                <option value="Ikuhisa Minowa" />
                <option value="Frank Mir" />
                <option value="Vitor Miranda" />
                <option value="Kazuo Misaki" />
                <option value="Dokonjonosuke Mishima" />
                <option value="David Mitchell" />
                <option value="Roman Mitichyan" />
                <option value="Eiji Mitsuoka" />
                <option value="Hiromitsu Miura" />
                <option value="Takeya Mizugaki" />
                <option value="Tatsuya Mizuno" />
                <option value="Roxanne Modafferi" />
                <option value="Bobby Moffett" />
                <option value="Renato Moicano" />
                <option value="Thiago Moises" />
                <option value="Muhammad Mokaev" />
                <option value="Jeff Monson" />
                <option value="Darrell Montague" />
                <option value="Nicco Montano" />
                <option value="Antonio Monteiro" />
                <option value="Sergio Moraes" />
                <option value="Marlon Moraes" />
                <option value="John Moraga" />
                <option value="Albert Morales" />
                <option value="Vince Morales" />
                <option value="Sarah Moras" />
                <option value="Christian Morecraft" />
                <option value="Brandon Moreno" />
                <option value="Dan Moret" />
                <option value="Alex Morono" />
                <option value="Maryna Moroz" />
                <option value="Eduarda Moura" />
                <option value="Gegard Mousasi" />
                <option value="Belal Muhammad" />
                <option value="Jamie Mullarkey" />
                <option value="Pedro Munhoz" />
                <option value="Andre Muniz" />
                <option value="Mark Munoz" />
                <option value="Johnny Munoz" />
                <option value="Makhmud Muradov" />
                <option value="Kanako Murata" />
                <option value="Lauren Murphy" />
                <option value="Lerone Murphy" />
                <option value="Lee Murray" />
                <option value="Josias Musasa" />
                <option value="Nicholas Musoke" />
                <option value="Magomed Mustafaev" />
                <option value="Rin Nakai" />
                <option value="Kazuhiro Nakamura" />
                <option value="Keita Nakamura" />
                <option value="Daisuke Nakamura" />
                <option value="Rinya Nakamura" />
                <option value="Yui Chul Nam" />
                <option value="Rose Namajunas" />
                <option value="Allan Nascimento" />
                <option value="Rodrigo Nascimento" />
                <option value="Bobby Nash" />
                <option value="Rafael Natal" />
                <option value="Ismail Naurdiev" />
                <option value="Geoff Neal" />
                <option value="Josh Neer" />
                <option value="Shane Nelson" />
                <option value="Roy Nelson" />
                <option value="Gunnar Nelson" />
                <option value="Kyle Nelson" />
                <option value="Journey Newson" />
                <option value="Carlos Newton" />
                <option value="Francis Ngannou" />
                <option value="Ben Nguyen" />
                <option value="Bo Nickal" />
                <option value="Matheus Nicolau" />
                <option value="Tom Niinimaki" />
                <option value="Ramsey Nijem" />
                <option value="Mats Nilsson" />
                <option value="Guangyou Ning" />
                <option value="Anthony Njokuani" />
                <option value="Antonio Rodrigo Nogueira" />
                <option value="Rogerio Nogueira" />
                <option value="Kyle Noke" />
                <option value="Tom Nolan" />
                <option value="Sage Northcutt" />
                <option value="Shohei Nose" />
                <option value="Jake O'Brien" />
                <option value="Sean O'Malley" />
                <option value="Casey O'Neill" />
                <option value="Brendan O'Reilly" />
                <option value="Nobuhiro Obiya" />
                <option value="Volkan Oezdemir" />
                <option value="Naoya Ogawa" />
                <option value="Trey Ogden" />
                <option value="Yushin Okami" />
                <option value="Aleksei Oleinik" />
                <option value="Rafaello Oliveira" />
                <option value="Charles Oliveira" />
                <option value="Alex Oliveira" />
                <option value="Saimon Oliveira" />
                <option value="Vinicius Oliveira" />
                <option value="Cameron Olson" />
                <option value="Daniel Omielanczuk" />
                <option value="Michihiro Omigawa" />
                <option value="David Onama" />
                <option value="Myktybek Orolbai" />
                <option value="Brian Ortega" />
                <option value="Tito Ortiz" />
                <option value="Dustin Ortiz" />
                <option value="Kenji Osawa" />
                <option value="Ode Osbourne" />
                <option value="Nick Osipczak" />
                <option value="Nissen Osterneck" />
                <option value="Rachael Ostovich" />
                <option value="Alexander Otsuka" />
                <option value="Zak Ottow" />
                <option value="Nick Pace" />
                <option value="Teemu Packalen" />
                <option value="George Pacurariu" />
                <option value="Chris Padilla" />
                <option value="Damacio Page" />
                <option value="Dustin Pague" />
                <option value="Raulian Paiva" />
                <option value="Fredson Paixao" />
                <option value="Bart Palaszewski" />
                <option value="Alexandre Pantoja" />
                <option value="Josh Parisian" />
                <option value="Karo Parisyan" />
                <option value="JunYong Park" />
                <option value="HyunSung Park" />
                <option value="Mick Parkin" />
                <option value="Jordan Parsons" />
                <option value="Preston Parsons" />
                <option value="Claude Patrick" />
                <option value="Alan Patrick" />
                <option value="Sam Patterson" />
                <option value="Estevan Payan" />
                <option value="Tyson Pedro" />
                <option value="Kurt Pellegrino" />
                <option value="Julianna Pena" />
                <option value="Luis Pena" />
                <option value="Cathal Pendred" />
                <option value="BJ Penn" />
                <option value="Jessica Penne" />
                <option value="Raquel Pennington" />
                <option value="Tecia Pennington" />
                <option value="Godofredo Pepey" />
                <option value="Viviane Pereira" />
                <option value="Michel Pereira" />
                <option value="Alex Pereira" />
                <option value="Erik Perez" />
                <option value="Alejandro Perez" />
                <option value="Frankie Perez" />
                <option value="Alex Perez" />
                <option value="Markus Perez" />
                <option value="Ailin Perez" />
                <option value="Anthony Perosh" />
                <option value="Thomas Petersen" />
                <option value="Steven Peterson" />
                <option value="Vitor Petrino" />
                <option value="Andre Petroski" />
                <option value="Ivana Petrovic" />
                <option value="Seth Petruzelli" />
                <option value="Anthony Pettis" />
                <option value="Sergio Pettis" />
                <option value="Nam Phan" />
                <option value="Constantinos Philippou" />
                <option value="Aaron Phillips" />
                <option value="Kyler Phillips" />
                <option value="Adam Piccolotti" />
                <option value="Vinc Pichel" />
                <option value="Brad Pickett" />
                <option value="Jamie Pickett" />
                <option value="Oskar Piechota" />
                <option value="Mike Pierce" />
                <option value="Sean Pierson" />
                <option value="Domingo Pilarte" />
                <option value="Paddy Pimblett" />
                <option value="Daniel Pineda" />
                <option value="Pingyuan Liu" />
                <option value="Luana Pinheiro" />
                <option value="Maki Pitolo" />
                <option value="Dustin Poirier" />
                <option value="Igor Pokrajac" />
                <option value="Julia Polastri" />
                <option value="Parker Porter" />
                <option value="Ruan Potts" />
                <option value="Francisco Prado" />
                <option value="Carlo Prater" />
                <option value="Michel Prazeres" />
                <option value="Niko Price" />
                <option value="Jiri Prochazka" />
                <option value="Lara Procopio" />
                <option value="Cole Province" />
                <option value="Daniel Puder" />
                <option value="Lucie Pudilova" />
                <option value="Claudio Puelles" />
                <option value="Jens Pulver" />
                <option value="Billy Quarantillo" />
                <option value="Vinicius Queiroz" />
                <option value="Jose Quinonez" />
                <option value="Benji Radach" />
                <option value="Shavkat Rakhmonov" />
                <option value="Aleksandar Rakic" />
                <option value="Hector Ramirez" />
                <option value="Ricardo Ramos" />
                <option value="Davi Ramos" />
                <option value="Kevin Randleman" />
                <option value="Bec Rawlings" />
                <option value="Stevie Ray" />
                <option value="Abdul Razak Alhassan" />
                <option value="Mateusz Rebecki" />
                <option value="Rafael Rebello" />
                <option value="Zachary Reese" />
                <option value="Chad Reiner" />
                <option value="Wilson Reis" />
                <option value="Goran Reljic" />
                <option value="Chance Rencountre" />
                <option value="Marion Reneau" />
                <option value="Dominick Reyes" />
                <option value="Mike Rhodes" />
                <option value="Amanda Ribas" />
                <option value="Vitor Ribeiro" />
                <option value="Will Ribeiro" />
                <option value="Esteban Ribovics" />
                <option value="Tabatha Ricci" />
                <option value="Matthew Riddle" />
                <option value="Joe Riggs" />
                <option value="Aaron Riley" />
                <option value="Jordan Rinaldi" />
                <option value="Diego Rivas" />
                <option value="Jorge Rivera" />
                <option value="Francisco Rivera" />
                <option value="Jimmie Rivera" />
                <option value="Karl Roberson" />
                <option value="Daniel Roberts" />
                <option value="Danny Roberts" />
                <option value="Roosevelt Roberts" />
                <option value="Kenny Robertson" />
                <option value="Gillian Robertson" />
                <option value="Colin Robinson" />
                <option value="Alvin Robinson" />
                <option value="Vagner Rocha" />
                <option value="Luke Rockhold" />
                <option value="Gregory Rodrigues" />
                <option value="Kleydson Rodrigues" />
                <option value="Ricco Rodriguez" />
                <option value="Yair Rodriguez" />
                <option value="Marina Rodriguez" />
                <option value="Daniel Rodriguez" />
                <option value="Ronaldo Rodriguez" />
                <option value="Drako Rodriguez" />
                <option value="Christian Rodriguez" />
                <option value="Marcos Rogerio de Lima" />
                <option value="Brian Rogers" />
                <option value="Shane Roller" />
                <option value="Jared Rollins" />
                <option value="Alexandr Romanov" />
                <option value="Ricardo Romero" />
                <option value="Mara Romero Borella" />
                <option value="Cortavious Romious" />
                <option value=" Rongzhu" />
                <option value="Jesse Ronson" />
                <option value="George Roop" />
                <option value="Aaron Rosa" />
                <option value="Charles Rosa" />
                <option value="Jacob Rosales" />
                <option value="Jared Rosholt" />
                <option value="Ben Rothwell" />
                <option value="Ronda Rousey" />
                <option value="Phil Rowe" />
                <option value="Brandon Royval" />
                <option value="Mauricio Rua" />
                <option value="Murilo Rua" />
                <option value="Montserrat Conejo Ruiz" />
                <option value="Cameron Saaiman" />
                <option value="Danny Sabatello" />
                <option value="Pat Sabatini" />
                <option value="Amir Sadollah" />
                <option value="Nazim Sadykhov" />
                <option value="Frankie Saenz" />
                <option value="Tarec Saffiedine" />
                <option value="Kiru Sahota" />
                <option value="Benoit Saint Denis" />
                <option value="Ovince Saint Preux" />
                <option value="Kazushi Sakuraba" />
                <option value="Hayato Sakurai" />
                <option value="Ivan Salaverry" />
                <option value="Luis Saldana" />
                <option value="Quillan Salkilld" />
                <option value="John Salter" />
                <option value="Josh Samman" />
                <option value="Josh Sampo" />
                <option value="Diego Sanchez" />
                <option value="Emmanuel Sanchez" />
                <option value="Robert Sanchez" />
                <option value="Luke Sanders" />
                <option value="Jerrod Sanders" />
                <option value="Cory Sandhagen" />
                <option value="Hector Sandoval" />
                <option value="Jorge Santiago" />
                <option value="Mike Santiago" />
                <option value="Evangelista Santos" />
                <option value="Leonardo Santos" />
                <option value="Thiago Santos" />
                <option value="Bruno Santos" />
                <option value="Yana Santos" />
                <option value="Taila Santos" />
                <option value="Marilia Santos" />
                <option value="Gabriel Santos" />
                <option value="Luana Santos" />
                <option value="Daniel Sarafian" />
                <option value="Yuta Sasaki" />
                <option value="Paul Sass" />
                <option value="Keisuke Sasu" />
                <option value="Ben Saunders" />
                <option value="Matt Sayles" />
                <option value="Eric Schafer" />
                <option value="Brendan Schaub" />
                <option value="Samy Schiavo" />
                <option value="Matt Schnell" />
                <option value="Justin Scoggins" />
                <option value="Brad Scott" />
                <option value="Neil Seery" />
                <option value="Stefan Sekulic" />
                <option value="Pete Sell" />
                <option value="Matthew Semelsberger" />
                <option value="Andrei Semenov" />
                <option value="Mackens Semerzier" />
                <option value="Matt Serra" />
                <option value="Edmen Shahbazyan" />
                <option value="Don Shainis" />
                <option value="Ken Shamrock" />
                <option value="Frank Shamrock" />
                <option value="Eric Shelton" />
                <option value="Sean Sherk" />
                <option value="Antonina Shevchenko" />
                <option value="Katsuyori Shibata" />
                <option value="Jake Shields" />
                <option value="Akira Shoji" />
                <option value="Jack Shore" />
                <option value="Sam Sicilia" />
                <option value="Serhiy Sidey" />
                <option value="Steven Siler" />
                <option value="Assuerio Silva" />
                <option value="Anderson Silva" />
                <option value="Wanderlei Silva" />
                <option value="Thiago Silva" />
                <option value="Paulo Cesar Silva" />
                <option value="Antonio Silva" />
                <option value="Erick Silva" />
                <option value="Leandro Silva" />
                <option value="Claudio Silva" />
                <option value="Joaquim Silva" />
                <option value="Bruno Silva" />
                <option value="Gabriel Silva" />
                <option value="Maria Silva" />
                <option value="Jean Silva" />
                <option value="Danny Silva" />
                <option value="Douglas Silva de Andrade" />
                <option value="Elias Silverio" />
                <option value="Ricky Simon" />
                <option value="Aaron Simpson" />
                <option value="Tony Sims" />
                <option value="Rory Singer" />
                <option value="Dennis Siver" />
                <option value="Chas Skelly" />
                <option value="Maurice Smith" />
                <option value="Scott Smith" />
                <option value="Anthony Smith" />
                <option value="Colton Smith" />
                <option value="Devonte Smith" />
                <option value="Cole Smith" />
                <option value="Elijah Smith" />
                <option value="Louis Smolka" />
                <option value="Peter Sobotta" />
                <option value="Renato Sobral" />
                <option value="Rameau Thierry Sokoudjou" />
                <option value="Joe Solecki" />
                <option value="Song Yadong" />
                <option value="Chael Sonnen" />
                <option value="Dmitry Sosnovskiy" />
                <option value="Krzysztof Soszynski" />
                <option value="George Sotiropoulos" />
                <option value="Greg Soto" />
                <option value="Joe Soto" />
                <option value="Andre Soukhamthath" />
                <option value="Mario Sousa" />
                <option value="Bobby Southworth" />
                <option value="Jacare Souza" />
                <option value="Livinha Souza" />
                <option value="Ketlen Souza" />
                <option value="Ryan Spann" />
                <option value="Felicia Spencer" />
                <option value="Mario Sperry" />
                <option value="Eric Spicely" />
                <option value="Serghei Spivac" />
                <option value="Austin Springer" />
                <option value="Georges St-Pierre" />
                <option value="Cristina Stanciu" />
                <option value="Brian Stann" />
                <option value="Kalib Starnes" />
                <option value="Damian Stasiak" />
                <option value="Jeremy Stephens" />
                <option value="Joe Stevenson" />
                <option value="Darren Stewart" />
                <option value="Julija Stoliarenko" />
                <option value="Dustin Stoltzfus" />
                <option value="Niklas Stolze" />
                <option value="Ken Stone" />
                <option value="Rick Story" />
                <option value="Sam Stout" />
                <option value="Daniel Straus" />
                <option value="Sean Strickland" />
                <option value="Stefan Struve" />
                <option value="Mike Stumpf" />
                <option value="Tatiana Suarez" />
                <option value="Genki Sudo" />
                <option value="George Sullivan" />
                <option value="Amar Suloev" />
                <option value=" Sumudaerji" />
                <option value="Joe Taimanglo" />
                <option value="Tatsuro Taira" />
                <option value="Daiju Takase" />
                <option value="Makoto Takimoto" />
                <option value="Payton Talbott" />
                <option value="Kiyoshi Tamura" />
                <option value="Michinori Tanaka" />
                <option value="Evan Tanner" />
                <option value="Manny Tapia" />
                <option value="Miesha Tate" />
                <option value="Deividas Taurosevicius" />
                <option value="Thiago Tavares" />
                <option value="Paul Taylor" />
                <option value="Jesse Taylor" />
                <option value="Danielle Taylor" />
                <option value="James Te Huna" />
                <option value="Glover Teixeira" />
                <option value="John Teixeira" />
                <option value="Daniel Teymur" />
                <option value="Brandon Thatch" />
                <option value="Paulo Thiago" />
                <option value="Din Thomas" />
                <option value="Nick Thompson" />
                <option value="James Thompson" />
                <option value="Josh Thomson" />
                <option value="Simeon Thoresen" />
                <option value="Josh Thornburg" />
                <option value="Gleison Tibau" />
                <option value="Chris Tickle" />
                <option value="Hideo Tokoro" />
                <option value="Ilia Topuria" />
                <option value="Ronys Torres" />
                <option value="Manuel Torres" />
                <option value="Frank Trigg" />
                <option value="Francisco Trinaldo" />
                <option value="Michael Trizano" />
                <option value="Antonio Trocoli" />
                <option value="Tor Troeng" />
                <option value="Abel Trujillo" />
                <option value="Rei Tsuruya" />
                <option value="Jon Tuck" />
                <option value="Gavin Tucker" />
                <option value="Jumabieke Tuerxun" />
                <option value="Nyamjargal Tumendemberel" />
                <option value="Tagir Ulanbekov" />
                <option value="Carlos Ulberg" />
                <option value="Caol Uno" />
                <option value="Kengo Ura" />
                <option value="Kamaru Usman" />
                <option value="Darren Uyenoyama" />
                <option value="Richie Vaculik" />
                <option value="Genaro Valdez" />
                <option value="Charlie Valencia" />
                <option value="Timur Valiev" />
                <option value="Austin Vanderford" />
                <option value="Lando Vannata" />
                <option value="Paige VanZant" />
                <option value="Kazula Vargas" />
                <option value="Jamie Varner" />
                <option value="Javier Vazquez" />
                <option value="Matt Veach" />
                <option value="Cain Velasquez" />
                <option value="Bojan Velickovic" />
                <option value="Karlos Vemola" />
                <option value="Luigi Vendramini" />
                <option value="Brandon Vera" />
                <option value="Marlon Vera" />
                <option value="Renato Verissimo" />
                <option value="Marvin Vettori" />
                <option value="Polyana Viana" />
                <option value="James Vick" />
                <option value="Milton Vieira" />
                <option value="Reginaldo Vieira" />
                <option value="Ketlen Vieira" />
                <option value="Rodolfo Vieira" />
                <option value="Chris Wade" />
                <option value="TJ Waldburger" />
                <option value="Johnny Walker" />
                <option value="Rodney Wallace" />
                <option value="Richard Walsh" />
                <option value="Patrick Walsh" />
                <option value="Wang Cong" />
                <option value="Ron Waterman" />
                <option value="Trey Waters" />
                <option value="Michelle Waterson-Gomez" />
                <option value="Brok Weaver" />
                <option value="Jonavin Webb" />
                <option value="Chris Weidman" />
                <option value="Mark Weir" />
                <option value="Christian Wellisch" />
                <option value="Jeremiah Wells" />
                <option value="Fabricio Werdum" />
                <option value="Coty Wheeler" />
                <option value="Alex White" />
                <option value="Mike Whitehead" />
                <option value="Emily Whitmire" />
                <option value="Adam Wieczorek" />
                <option value="Mike Wilkinson" />
                <option value="James Wilks" />
                <option value="Pete Williams" />
                <option value="Patrick Williams" />
                <option value="Chris Wilson" />
                <option value="Westin Wilson" />
                <option value="Matt Wiman" />
                <option value="Eddie Wineland" />
                <option value="Keith Wisniewski" />
                <option value="Jason Witt" />
                <option value="Travis Wiuff" />
                <option value="Karolina Wojcik" />
                <option value="Joanne Wood" />
                <option value="Nathaniel Wood" />
                <option value="Rani Yahya" />
                <option value="Mohammad Yahya" />
                <option value="Alexander Yakovlev" />
                <option value="Yoshihisa Yamamoto" />
                <option value="Petr Yan" />
                <option value="Dongi Yang" />
                <option value=" Yizha" />
                <option value="Ashley Yoder" />
                <option value="Hirotaka Yokoi" />
                <option value="SangHoon Yoo" />
                <option value="Dong Sik Yoon" />
                <option value="Yoshiyuki Yoshida" />
                <option value="Hidehiko Yoshida" />
                <option value="SuYoung You" />
                <option value="Youssef Zalal" />
                <option value="Elizeu Zaleski dos Santos" />
                <option value="David Zawada" />
                <option value="Joao Zeferino" />
                <option value="Daniel Zellhuber" />
                <option value="Roman Zentsov" />
                <option value="Zhang Tiequan" />
                <option value="Zhang Lipeng" />
                <option value="Zhang Weili" />
                <option value="Daermisi Zhawupasi" />
              </datalist>
            </div>
            <div className="predict-card">
              <h3>Analytics</h3>
              <div className="analytics-placeholder">Charts Coming Soon</div>
            </div>
          </div>

          
        </section>
      </main>
      <footer id="contact">
        <p>&copy; {new Date().getFullYear()} FightMetricsAI - All rights reserved.</p>
      </footer>
    </div>
  );
}

export default App;