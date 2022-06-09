import * as React from 'react';
import Box from '@mui/material/Box'

import TextField from '@mui/material/TextField'

export default function FormPropsTextFields({ onHostNameChange }) {
    return (
        <div style={{ padding: 20 }}>
            <TextField
                required
                id="url"
                label="url"
                defaultValue=""
                variant="outlined"
                onKeyDown={(e) => {
                    if (e.key === 'Enter') {
                        onHostNameChange(e.target.value)
                    }
                }}
            />
        </div>
    );
}