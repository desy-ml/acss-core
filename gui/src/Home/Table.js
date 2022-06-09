import React, { useState, useEffect } from "react";
import { DataGrid } from '@mui/x-data-grid';
import Button from '@mui/material/Button';
import Stack from '@mui/material/Stack';

const fetchRunningServices = async (host) => {
    return await fetch(`http://${host}:5002/services`).then(res => res.json()).then(data => {
        return {
            data: data.services,
            errorMessage: ""
        }
    }).catch(err => {
        return {
            data: [],
            errorMessage: err.message
        }
    })
}

export const stopService = async (host, name) => {
    await fetch(`http://${host}:5002/stop/${name}`)
}

const getRunningServices = async (host) => {
    const servicesFromServer = await fetchRunningServices(host)
    const new_service_list = []
    const serviceNameValArr = Object.entries(servicesFromServer.data)
    if (serviceNameValArr.length > 0) {
        let count = 0
        for (const [key, value] of serviceNameValArr) {
            new_service_list.push({ id: count, name: key, type: value.type })
            count++
        }
    }
    return {
        data: new_service_list,
        errorMessage: servicesFromServer.errorMessage
    }
}

function Table({ host }) {
    const [rows, setRows] = useState([]);
    const [selectedRows, setSelectedRows] = useState([]);
    console.log(`Table:  ${host}`)
    useEffect(() => {
        const interval = setInterval(async () => {
            console.log(`interval ${host}`)
            const new_services = await getRunningServices(host)

            // only update if service removed or added
            const service_names_in_table = new Set(rows.map(function (value, index) { return value.name; }))
            for (const service of new_services.data) {
                if (!service_names_in_table.has(service)) {
                    setRows(new_services.data);
                    break;
                }
            }
            if (new_services.data.length < rows.length) {
                setRows(new_services.data)
            }

        }, 2000)
        return () => clearInterval(interval);
    }, [rows, host])

    const columns = [
        { field: 'id', headerName: 'ID', width: 70 },
        { field: 'name', headerName: 'name', width: 200 },
        { field: 'type', headerName: 'type', width: 200 },
    ];


    return (
        <div>
            <div style={{ height: 600, width: '100%' }}>
                <DataGrid
                    rows={rows}
                    columns={columns}
                    pageSize={15}
                    rowsPerPageOptions={[15]}
                    checkboxSelection
                    onSelectionModelChange={(selectionModel, details) => {
                        setSelectedRows(selectionModel)
                    }}
                />
            </div>
            <div style={{ padding: 20 }}>
                <Stack spacing={2} direction="row">
                    <Button
                        variant="contained"
                        onClick={() => {
                            for (const idx of selectedRows) {
                                console.log(rows[idx].name)
                                stopService(host, rows[idx].name)
                            }
                        }}

                    >Stop</Button>
                </Stack>
            </div>
        </div >
    );
}

export default Table;