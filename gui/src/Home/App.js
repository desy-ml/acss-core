import React, { useState } from "react";
import Table from "./Table"
import ConfigBox from "./ConfigBox"





function App() {
  const [hostName, setHostName] = useState('');
  return (
    <div style={{ padding: 20 }}>
      <div style={{ padding: 20 }}>
        < ConfigBox
          onHostNameChange={(host) => {
            console.log(`onHostNameChanged:  ${host}`)
            setHostName(host)
          }}
        />
      </div>
      <div style={{ padding: 20 }}>
        < Table
          host={hostName}
        />
      </div>
    </div >
  );
}
export default App;