import './App.css';
import BaseStage from './BaseStage.jsx';
import 'bootstrap/dist/css/bootstrap.min.css';
import React, { useState } from 'react';

function App() {

  const connections = {
    C1: {
      type: 'VNC', 
      token: 'eyJpdiI6IlhKM1ZUb01BQW1rRW5kQlRxSjM0WWc9PSIsInZhbHVlIjoiaitNKzFJMUlmd3dqRk9NZTl0WG9LUGNSRWxvc0M4bjRtOUJlc2ZXejNmWVhmSk91VVh6QnpRNHRRZmE5SUMzRVc0bk9uNm1KeVIza21pTVFJSGdENWVDZTRwMjc4a2NxaXpkVml6VTBRcXZ2ei9scndBUGJYd1Y4SjMzS2ltejRCYWRQOHYxU2Q2QXpvMTZyY0JvNDVXQS9VYTg1ZjhoNGRYM3MvR2JlSEZwTDR0dlpTOUJoYzJ4N3Y3YzBsVExMSmFUK3JnR1dnUEx2bmt5RTBVQ1ZmM2Z3SHoxMjlYaUFaV1Y2RE9CS2hETzkzVzEvbnNZekhZZEVheEZhaWpDekNoUlYxL2o1U1JuZzNQWFZXTWVOS3c9PSJ9', 
      address: '192.168.178.28',
      os: 'Linux Mint'
    },
    C2: {
      type: 'RDP', 
      //token: 'eyJpdiI6InY1YVhSSjlhOTVSZDl3Ti9jVDg5QXc9PSIsInZhbHVlIjoidkR4VitybXBiRUVqNVRvM1MySzJnU01YL3ovQ3o4NG1QaHRmUTJDVlNjeStyZlI5WitzdUJPQ0VTUjRjaUJVVnU4clN1WDlHK1dsazBiT0FpT0t5TUEzQnV2bXNDOWFFdnkyTW1Qb2t1LzlqeXRySVRzeWlxMFlzejFIQ3BSZmxzU1hPSkNOc3d5T2tHQ1FQVm94N1NIb3ZIZ0VkK0UxSHpqVWVNS1Z1WHhaMGhUN0VXZ2pSVUh3Y1JSVzQ1d2ZLL0VBSE1lNkdBTThJRU9CVVFtVEpMK1IzNEQwUWkyZ1ZkMmtpbDZIeUtvVEo0QjBkMW9FUDJVMk9tbXRRUXhnMzd4K2F3MnYvVVhGVEZUMndnZkp5cW8xYnhiRTRaNGVuRTRjN2krRGJsRzRjYW93TWhZSjkzWnBYbXBMMHlYYzIrTEp1bVo2eEtmc0VuVUhZdmZuOEFYNXlmL0VHbTg0Z0N0VUZNWWZtVmMxR2lKbExKU0lxMlp3SGlOWk9TWkhzMU9Vcm0rV1Q3c25BYUFaTnhsVUxYTWs2d20rdkZYcFduWTN3cytrbHNrS3o5U21FUEVaQmVTTSttcGVDWldNNiJ9',
      token: 'eyJpdiI6IkxhRWo0RWUxWEVQRmNvWmtobW5PR0E9PSIsInZhbHVlIjoidEErd0c4eS9zb0tIQWJhakZLNStwTFA5UkZuSEswd1V0NFVpc2FhWnQ4azBKeFduK0QxZW5uWk1FTmxPa29nMnpjVUVZc2NZaUpnb3Z2bVhHOXphSm55QzhXdUp0WDEyVXlMVkx2NWp3YlArMzJIb1RWekV2MExWUFVpVlU2WEJQYWFKbkljUjJtRnIzQmVDcWpzVTNjQU92ZkxCa0ZRdldNTUR3OWhjc1dGQ2V1VTBWSU5BdUd0Q1M2Z3k3cUpya1NxMnVjL1lFNzhsMXpxditQMTZ2RFY0UVJXS2k2MldpWk5NK0FxcGgreTJHZnpLQnpoaXloNldhZ3kvNXNHQmQ1ZU9vUFE1Tmd6UEhJSmI3VVY4ZUIyblZ3TVpkSll0R3g5Mm52em4xOVB4TGtsYlJVMDVPVE9CSzVOQlJNZEJ1VVNFcmc2MFZhMmNqWndnbG52eEdhZEJhaW43aXFwZVhxcDBwbDBVN2QwcnR5Ymp5alVBWEZSWUJ2d1N0d2JZRlkrNkJOTzBYQ0hJQ3p0TE1RZDF1UUxvNXUvNzJrWTRoZzFkbkZud09LQUYxVXpuR1hzSFB6Z0JpN3pndUtiRiJ9',
      address: '192.168.178.30',
      os: 'Windows 10 Pro'
    }
};

  const [selectedOption, setSelectedOption] = useState('C1');

  const handleSelectChange = (event) => { 
    setSelectedOption(event.target.value);
  };


  return (
    <div className='App'>
      <div className='d-flex-column justify-content-center align-items-center' >
        <h1 className="mb-4">Desktop As A Service - Prototype</h1>
        <div className="d-flex justify-content-center align-items-baseline" >
          <span className="me-4">Please select a connection:</span>
          <select className="form-select w-auto mb-4" value={selectedOption} onChange={handleSelectChange}>     
            <option value="C1">Linux Mint - VNC</option>
            <option value="C2">Windows 10 - RDP</option>
          </select>
        </div> 
        <div className="d-flex justify-content-center">
          <BaseStage connection={connections[selectedOption]} key={selectedOption}></BaseStage>
        </div>
      </div>  
    </div>
  );

}

export default App;


