import React from 'react';
import {FormControl, TextField, Grid, Autocomplete, Button, Box} from '@mui/material';

const years = Array.from({length: 2019 - 1982 + 1}, (_, i) => String(1982 + i));

export default function Tournaments() {
    const [tournaments, setTournaments] = React.useState([]);
    const [tournament, setTournament] = React.useState('');
    const [year, setYear] = React.useState(null);
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

    const searchTournaments = () => {
        fetch('/api/searchTournaments',{
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({year: year, tournament: tournament}),
        })
            .then(response => {return response.json()})
            .then(data => {setData(data)})
    };

    return (
        <div>
            <Grid container spacing={2}>
                <Grid item>
                    <Autocomplete 
                        value={tournament}
                        onChange={(_, newValue) => {setTournament(newValue)}}
                        options={tournaments}
                        renderInput={(params) => <TextField {...params} label="Tournament" variant='standard'/>}
                        sx={{ minWidth:150}}
                    />
                </Grid>
                <Grid item>
                    <Autocomplete 
                        value={year}
                        onChange={(_, newValue) => {setYear(newValue)}}
                        disablePortal
                        options={years}
                        renderInput={(params) => <TextField {...params} label="Year" variant='standard'/>}
                        sx={{ minWidth:100}}
                    />
                </Grid>
                <Grid item alignItems="end" style={{ display: "flex"}}>
                    <Button variant="contained" onClick={searchTournaments}>Search</Button>
                </Grid>
            </Grid>
            {data && 'TODO: Display the data'}
        </div>
    );
}