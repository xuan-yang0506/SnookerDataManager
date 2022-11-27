import React from 'react';
import {TextField, Grid, Autocomplete, Button} from '@mui/material';
import {DataGrid} from '@mui/x-data-grid';

function PlayersTable(props) {
    const columns = [
        { field: 'first_name', headerName: 'First Name', width: 70 },
        { field: 'last_name', headerName: 'Last Name', width: 70 },
        { field: 'country', headerName: 'Country', width: 70 },
    ];

    const rows = props.data.map((player) => {
        return {
            first_name: player[2],
            last_name: player[3],
            country: player[5],
        }
    });

    alert(rows);

    return (
        <div style={{ maxHeight: 600}}>
            <DataGrid
                rows={rows}
                columns={columns}
            />
        </div>
    )
}

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
        fetch('/api/searchPlayers?' + new URLSearchParams({name: name, country: country}))
            .then(response => {return response.json()})
            .then(data => {setData(data)})
    };

    const handleNameChange = (event) => {
        setName(event.target.value);
    };

    return (
        <div>
            <Grid container spacing={2}>
                <Grid item>
                    <TextField id="outlined-basic" label="Name" variant="standard" onChange={handleNameChange} />
                </Grid>
                <Grid item>
                    <Autocomplete 
                        value={country}
                        onChange={(_, newValue) => {setCountry(newValue)}}
                        disablePortal
                        options={countries}
                        renderInput={(params) => <TextField {...params} label="Country" variant='standard'/>}
                    />
                </Grid>
                <Grid item alignItems="end" style={{ display: "flex"}}>
                    <Button variant="contained" onClick={searchPlayers}>Search</Button>
                </Grid>
            </Grid>
            {data && <PlayersTable data={data} />}
        </div>
    );
}