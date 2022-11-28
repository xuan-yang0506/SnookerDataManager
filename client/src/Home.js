import React from 'react';
import PropTypes from 'prop-types';
import Typography from '@mui/material/Typography';
import {Container, FormControl, Tabs, Tab, Box} from '@mui/material';
import Players from './Players';
import Games from './Games';
import Tournaments from './Tournaments';
import Ranking from './Ranking';
import TerminalInterface from './TerminalInterface';

function TabPanel(props) {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`simple-tabpanel-${index}`}
      aria-labelledby={`simple-tab-${index}`}
      {...other}
    >
      {value === index && (
        <Box sx={{ p: 3 }}>
          <Typography>{children}</Typography>
        </Box>
      )}
    </div>
  );
}

TabPanel.propTypes = {
    children: PropTypes.node,
    index: PropTypes.number.isRequired,
    value: PropTypes.number.isRequired,
};

function NavTabs() {
  const [value, setValue] = React.useState(0);

  // get tournaments list
  const [tournaments, setTournaments] = React.useState([]);
  const getTournaments = () => {
    fetch('/api/getTournamentsList')
      .then(response => response.json())
      .then(data => {
          setTournaments(data);
      });
  };

  if (!tournaments.length) {
      getTournaments();
  }

  // get countries list
  const [countries, setCountries] = React.useState([]);
  const getCountries = () => {
    fetch('/api/getCountriesList')
      .then(response => response.json())
      .then(data => {
          setCountries(data);
      });
  };

  if (!countries.length) {
    getCountries();
  } 

  // get players list
  const [players, setPlayers] = React.useState([]);
  const getPlayers = () => {
    fetch('/api/getPlayersList')
      .then(response => response.json())
      .then(data => {
        setPlayers(data);
      });
  };
  
  if (!players.length) {
    getPlayers();
  }

  const handleChange = (_, newValue) => {
    setValue(newValue);
  };

  return (
    <div>
      <FormControl sx={{ m: 1, flexGrow: 1}}>
        <Box>
            <Tabs value={value} onChange={handleChange}>
                <Tab label="EDFS" />
                <Tab label="Players" />
                <Tab label="Games" />
                <Tab label="Tournaments" />
                <Tab label="Ranking" />
            </Tabs>
        </Box>
      </FormControl>
      <div>
        <FormControl sx={{ m: 1, flexGrow: 1}}>
          <TabPanel value={value} index={0}> 
            <TerminalInterface />                 
          </TabPanel>
          <TabPanel value={value} index={1}> 
            <Players players={players} countries={countries}/>                 
          </TabPanel>
          <TabPanel value={value} index={2}>
            <Games players={players} tournaments={tournaments}/>
          </TabPanel>
          <TabPanel value={value} index={3}>
            <Tournaments tournaments={tournaments}/>          
          </TabPanel>
          <TabPanel value={value} index={4}>
            <Ranking players={players} />
          </TabPanel>
        </FormControl>
      </div>
    </div>
  );
}


export default class Home extends React.Component {
  render() {
    return (
      <div>
        <Container maxWidth="lg" sx={{ mt: 20}} style={{textAlign: "center"}}>
            <h1>Snooker Data Manager</h1>
            <p>Provide data for players and games.</p>
            <NavTabs />
        </Container>
      </div>
    );
  }
}