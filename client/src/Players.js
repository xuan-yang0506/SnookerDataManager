import React from 'react';
import {FormControl, TextField, Grid, Autocomplete, Button} from '@mui/material';

const years = Array.from({length: 2019 - 1982 + 1}, (_, i) => String(1982 + i));

export default function Players() {
    const [name, setName] = React.useState('');
    const [year, setYear] = React.useState(null);
    const [data, setData] = React.useState(null);

    const searchPlayers = () => {
        fetch('/api/searchPlayers',{
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({name: name, year: year}),
        })
        .then(response => {return response.json()})
        .then(data => {alert(data);setData(data)})
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
                            value={year}
                            onChange={(event, newValue) => {setYear(newValue)}}
                            disablePortal
                            options={years}
                            renderInput={(params) => <TextField {...params} label="Year" variant='standard'/>}
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