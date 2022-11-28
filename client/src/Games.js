import React from 'react';
import { useMemo } from 'react';
import {TextField, Grid, Autocomplete, Button} from '@mui/material';
import {DataGrid} from '@mui/x-data-grid';
import {DataGridPro} from '@mui/x-data-grid-pro';

const years = Array.from({length: 2019 - 1982 + 1}, (_, i) => String(1982 + i));

function GamesTable(props) {
    const columns = [
        { field: 'year', headerName: 'Year', width:70},
        { field: "tournament", headerName: "Tournament", width: 200},
        { field: "stage", headerName: "Stage", width: 70},
        { field: "player1", headerName: "Player 1", width: 120},
        { field: "score", headerName: "Score", width: 70},
        { field: "player2", headerName: "Player 2", width: 120},
        { field: "frame_scores", headerName: "Frame Scores", width: 300},
    ];
    const data = props.data;

    const rows = useMemo(() => {
        return props.data.map((match, id) => {
            return {
                id: Number(match[1]),
                year: match[15],
                tournament: match[16],
                stage: match[3],
                player1: match[5],
                score: match[9] + ' : ' + match[10],
                player2: match[7],
                frame_scores: match[11],
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

export default function Games() {
    const [player1, setPlayer1] = React.useState('');
    const [player2, setPlayer2] = React.useState('');
    const [year, setYear] = React.useState('');
    const [tournaments, setTournaments] = React.useState([]);
    const [tournament, setTournament] = React.useState('');
    const [data, setData] = React.useState(null);

    const getTournaments = () => {
        fetch('/api/getTournamentsList')
            .then(response => response.json())
            .then(data => {
                setTournaments(data);
            });
    }

    if (!tournaments.length) {
        getTournaments();
    }

    const searchGames = () => {
        fetch('/api/searchGames?' + new URLSearchParams({player1: player1, player2: player2, year: year, tournament: tournament}))
            .then(response => {return response.json()})
            .then(data => {alert(data);setData(data)})
    };


    return (
        <div>
            <Grid container spacing={2}>
                <Grid item>
                    <TextField id="outlined-basic" label="Player1" variant="standard" onChange={(e) => {setPlayer1(e.target.value)}} />
                </Grid>
                <Grid item>
                    <TextField id="outlined-basic" label="Player2" variant="standard" onChange={(e) => {setPlayer2(e.target.value)}} />
                </Grid>
                <Grid item>
                    <Autocomplete 
                        value={tournament}
                        onChange={(_, newValue) => {setTournament(newValue)}}
                        disablePortal
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
                    <Button variant="contained" onClick={searchGames}>Search</Button>
                </Grid>
            </Grid>
            <div style={{marginTop: 10}}>
                {data && <GamesTable data={data}/>}
            </div>
        </div>
    );
}