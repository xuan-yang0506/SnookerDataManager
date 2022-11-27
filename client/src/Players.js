import React from 'react';
import {FormControl, TextField, Grid, Autocomplete, Button} from '@mui/material';

export default function Players() {
    const [name, setName] = React.useState('');
    const [country, setCountry] = React.useState('');
    const [countries, setCountries] = React.useState([]);
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

    const searchPlayers = () => {
        fetch('/api/searchPlayers',{
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({name: name, country: country}),
        })
            .then(response => {return response.json()})
            .then(data => {setData(data)})
    };

    const handleNameChange = (event) => {
        setName(event.target.value);
    };

    return (
        <div>
            <FormControl sx={{ m: 1, flexGrow: 1}}>
                <Grid container spacing={2}>
                    <Grid item xs={12} sm={5}>
                        <TextField id="outlined-basic" label="Name" variant="standard" onChange={handleNameChange} />
                    </Grid>
                    <Grid item xs={12} sm={4}>
                        <Autocomplete 
                            value={country}
                            onChange={(_, newValue) => {setCountry(newValue)}}
                            disablePortal
                            options={countries}
                            renderInput={(params) => <TextField {...params} label="Country" variant='standard'/>}
                        />
                    </Grid>
                    <Grid item xs={12} sm={3} alignItems="end" style={{ display: "flex"}}>
                        <Button variant="contained" onClick={searchPlayers}>Search</Button>
                    </Grid>
                </Grid>
            </FormControl>
            {data && 'test'}
        </div>
    );
}