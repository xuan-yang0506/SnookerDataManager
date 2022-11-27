import React from 'react';
import {FormControl, TextField, Grid, Autocomplete, Button} from '@mui/material';

const years = Array.from({length: 2019 - 1982 + 1}, (_, i) => String(1982 + i));

export default function Ranking() {
    const [country, setCountry] = React.useState('');
    const [countries, setCountries] = React.useState([]);
    const [year, setYear] = React.useState(null);
    const [data, setData] = React.useState(null);

    const getCountries = () => {
        fetch('/api/getCountries')
            .then(response => response.json())
            .then(data => {
                setCountries(data);
            });
    }

    if (!countries.length) {
        getCountries();
    }

    const rankPlayers = () => {
        fetch('/api/rankPlayers',{
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({year: year, country: country}),
        })
            .then(response => {return response.json()})
            .then(data => {setData(data)})
    };

    return (
        <div>
            <Grid container spacing={2}>
                <Grid item>
                    <Autocomplete 
                        value={country}
                        onChange={(_, newValue) => {setCountry(newValue)}}
                        disablePortal
                        options={countries}
                        renderInput={(params) => <TextField {...params} label="Country" variant='standard'/>}
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
                    <Button variant="contained" onClick={rankPlayers}>Rank</Button>
                </Grid>
            </Grid>
            {data && 'TODO: Display the data'}
        </div>
    );
}