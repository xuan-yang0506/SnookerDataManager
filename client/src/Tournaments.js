import React from 'react';
import {useMemo} from 'react';
import {TextField, Grid, Autocomplete, Button} from '@mui/material';
import {DataGrid} from '@mui/x-data-grid';

const years = Array.from({length: 2019 - 1982 + 1}, (_, i) => String(1982 + i));

function TournamentsTable(props) {
    const columns = [
        { field: "year", headerName: "Year"},
        { field: "name", headerName: "Tournament"},
        { field: "country", headerName: "Country"},
        { field: "category", headerName: "Category"},
        { field: "prize", headerName: "Prize"},
    ];
    const data = props.data;

    const rows = useMemo(() => {
        return data.map((tournament, id) => {
            return {
                id: id,
                year: tournament[2],
                name: tournament[3],
                country: tournament[9],
                category: tournament[7],
                prize: tournament[8],
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

export default function Tournaments(props) {
    const tournaments = props.tournaments;
    const [tournament, setTournament] = React.useState('');
    const [year, setYear] = React.useState(null);
    const [data, setData] = React.useState(null);

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
                        sx={{ minWidth:200}}
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
            {data && (<div style={{marginTop: 10}}><TournamentsTable data={data}/></div>)}
        </div>
    );
}