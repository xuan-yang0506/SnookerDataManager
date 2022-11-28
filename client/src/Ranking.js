import React from 'react';
import {useMemo} from 'react';
import {DataGrid} from '@mui/x-data-grid';
import {TextField, Grid, Autocomplete, Button} from '@mui/material';

const years = Array.from({length: 2019 - 1982 + 1}, (_, i) => String(1982 + i));

function RankingTable(props) {
    const columns = [
        { field: "rank", headerName: "Rank"},
        { field: "first_name", headerName: "First Name"},
        { field: "last_name", headerName: "Last Name"},
        { field: "year", headerName: "Year"},
    ];
    const data = props.data;

    const rows = useMemo(() => {
        return props.data.map((player, id) => {
            return {
                id: id,
                rank: player[3],
                first_name: player[1],
                last_name: player[2],
                year: Number(player[0]),
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

export default function Ranking(props) {
    const players = props.players;
    const [name, setName] = React.useState(null);
    const [year, setYear] = React.useState(null);
    const [data, setData] = React.useState(null);

    const rankPlayers = () => {
        fetch('/api/searchRank?' + new URLSearchParams({year: year, name: name}))
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
            <div style={{marginTop: 10}}>
                {data && <RankingTable data={data}/>}
            </div>
        </div>
    );
}