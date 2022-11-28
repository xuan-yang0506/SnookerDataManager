import React from 'react';
import { useMemo } from 'react';
import {TextField, Grid, Autocomplete, Button} from '@mui/material';
import {DataGrid} from '@mui/x-data-grid';

function PlayersTable(props) {
    const renderLink = (params) => {
        return (
            <a href={params.row.link} target="_blank">Link</a>
        );
    };

    const columns = [
        { field: "first_name", headerName: "First Name"},
        { field: "last_name", headerName: "Last Name"},
        { field: "country", headerName: "Country"},
        { field: "link", headerName: "Link", renderCell: renderLink},
    ];
    const data = props.data;


    const rows = useMemo(() => {
        return props.data.map((player, id) => {
            return {
                id: id,
                first_name: player[2],
                last_name: player[3],
                country: player[5],
                link: player[0],
            }
        });
    }, [data]);

    return (
        <div style={{ height: 600, width: "100%"}}>
            <DataGrid
                rows={rows}
                columns={columns}
            />
        </div>
    )
}

export default function Players(props) {
    const players = props.players;
    const countries = props.countries;

    const [name, setName] = React.useState('');
    const [country, setCountry] = React.useState('');
    const [data, setData] = React.useState(null);

    const searchPlayers = () => {
        fetch('/api/searchPlayers?' + new URLSearchParams({name: name, country: country}))
            .then(response => {return response.json()})
            .then(data => {setData(data)})
    };

    return (
        <div>
            <Grid container spacing={2}>
                <Grid item>                    
                    <Autocomplete 
                        value={name}
                        onChange={(_, newValue) => {setName(newValue)}}
                        disablePortal
                        options={players}
                        renderInput={(params) => <TextField {...params} label="Name" variant='standard'/>}
                        sx={{ minWidth:200}}
                    />
                </Grid>
                <Grid item>
                    <Autocomplete 
                        value={country}
                        onChange={(_, newValue) => {setCountry(newValue)}}
                        disablePortal
                        options={countries}
                        renderInput={(params) => <TextField {...params} label="Country" variant='standard'/>}
                        sx={{ minWidth:200}}
                    />
                </Grid>
                <Grid item alignItems="end" style={{ display: "flex"}}>
                    <Button variant="contained" onClick={searchPlayers}>Search</Button>
                </Grid>
            </Grid>
            <div style={{marginTop: 10}}>
                {data && <PlayersTable data={data} />}
            </div>
        </div>
    );
}