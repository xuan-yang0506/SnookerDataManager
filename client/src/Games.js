import React from 'react';
import {FormControl, TextField, Grid, Autocomplete, Button} from '@mui/material';

const years = Array.from({length: 2019 - 1982 + 1}, (_, i) => String(1982 + i));

export default function Games() {
    const [player1, setPlayer1] = React.useState('');
    const [player2, setPlayer2] = React.useState('');
    const [year, setYear] = React.useState(null);
    const [tournaments, setTournaments] = React.useState([]);
    const [tournament, setTournament] = React.useState('');
    const [data, setData] = React.useState(null);

    const getTournaments = () => {
        fetch('/api/getTournaments')
            .then(response => response.json())
            .then(data => {
                setTournaments(data);
            });
    }

    if (!tournaments.length) {
        getTournaments();
    }

    const searchGames = () => {
        fetch('/api/searchGames',{
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({player1: player1, player2: player2, year: year, tournament: tournament}),
        })
            .then(response => {return response.json()})
            .then(data => {setData(data)})
    };


    return (
        <div>
            <FormControl sx={{ m: 1, flexGrow: 1}}>
                <Grid container spacing={2}>
                    <Grid item xs={12} sm={2}>
                        <TextField id="outlined-basic" label="Player1" variant="standard" onChange={(e) => {setPlayer1(e.target.value)}} />
                    </Grid>
                    <Grid item xs={12} sm={2}>
                        <TextField id="outlined-basic" label="Player2" variant="standard" onChange={(e) => {setPlayer2(e.target.value)}} />
                    </Grid>
                    <Grid item xs={12} sm={2}>
                        <Autocomplete 
                            value={year}
                            onChange={(_, newValue) => {setYear(newValue)}}
                            disablePortal
                            options={years}
                            renderInput={(params) => <TextField {...params} label="Year" variant='standard'/>}
                        />
                    </Grid>
                    <Grid item xs={12} sm={4}>
                        <Autocomplete 
                            value={tournament}
                            onChange={(_, newValue) => {setTournament(newValue)}}
                            disablePortal
                            options={tournaments}
                            renderInput={(params) => <TextField {...params} label="Tournament" variant='standard'/>}
                        />
                    </Grid>
                    <Grid item xs={12} sm={2} alignItems="end" style={{ display: "flex"}}>
                        <Button variant="contained" onClick={searchGames}>Search</Button>
                    </Grid>
                </Grid>
            </FormControl>
        </div>
    );
}