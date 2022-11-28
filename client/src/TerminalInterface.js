import React from 'react';
import {TextField, Grid, Button, FormControlLabel} from '@mui/material';
import TreeView from '@mui/lab/TreeView';
import TreeItem from '@mui/lab/TreeItem';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import ChevronRightIcon from '@mui/icons-material/ChevronRight';

function NavigationTree(props) {
    const data = props.data;

    const renderTree = (nodes) => (
        <TreeItem key={nodes.id} nodeId={nodes.id} label={nodes.name}>
            {Array.isArray(nodes.children) ? nodes.children.map((node) => renderTree(node)) : null}
        </TreeItem>
    );

    return (
        <div style={{textAlign: "left"}}>
            <label style={{fontSize: "20px"}}>EDFS Navigation Tree</label>
            <TreeView
                defaultCollapseIcon={<ExpandMoreIcon />}
                defaultExpandIcon={<ChevronRightIcon />}
                sx={{ height: 250, flexGrow: 1}}
            >
                {data && renderTree(data)}
            </TreeView>
        </div>
    );
}

export default function TerminalInterface() {
    const [result, setResult] = React.useState(null);
    const [naviData, setNaviData] = React.useState(null);

    const getNaviData = () => {
        fetch('/api/getNaviData')
            .then(response => response.json())
            .then(data => { 
                setNaviData(data); 
            });
    };

    if (!naviData) {
        getNaviData();
    }

    const handleSubmit = () => {
        const command = document.getElementById('command-input').value;
        
        fetch('/api/terminal?' + new URLSearchParams({command: command}))
            .then(response => {return response.json()})
            .then(data => {setResult(data)});
        
        // fetch file structure again every time a command is submitted (update)
        getNaviData();
    }

    return (
        <div>
            <NavigationTree data={naviData} />
            <div style={{textAlign: "left"}}>
                <label style={{fontSize: "20px"}}>EDFS Terminal</label>
            </div>
            <Grid container spacing={2}>
                <Grid item>                    
                    <TextField id="command-input" label="Command" variant="standard" sx={{minWidth: 500}}/>
                </Grid>
                <Grid item alignItems="end" style={{ display: "flex"}}>
                    <Button variant="contained" onClick={handleSubmit}>Submit</Button>
                </Grid>
            </Grid>
            <div style={{marginTop: 10}}>
                <TextField
                    id="edfs-output"
                    multiline
                    rows={10}
                    variant="filled"
                    fullWidth={true}
                    sx={{height: 500}}
                    value={result}
                />
            </div>
        </div>
    );
}