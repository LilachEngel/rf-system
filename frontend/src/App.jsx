import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css';

const API_BASE_URL = 'http://localhost:8000'; // כתובת ה-API שלך

function App() {
  const [samples, setSamples] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);

  // פונקציה לשליפת הנתונים מה-API
  const fetchData = async () => {
    try {
      // שליפת דגימות מ-PostgreSQL דרך ה-API
      const samplesRes = await axios.get(`${API_BASE_URL}/samples`);
      setSamples(samplesRes.data.samples || []);

      // שליפת התראות מ-MongoDB דרך ה-API (נניח ויצרת נקודת קצה /alerts)
      const alertsRes = await axios.get(`${API_BASE_URL}/alerts`);
      setAlerts(alertsRes.data.alerts || []);
      
      setLoading(false);
    } catch (error) {
      console.error("Error fetching data from API:", error);
    }
  };

  // מנגנון Polling - עדכון אוטומטי כל 3 שניות
  useEffect(() => {
    fetchData(); // קריאה ראשונית
    const interval = setInterval(fetchData, 3000);
    return () => clearInterval(interval); // ניקוי ה-interval בסגירת הקומפוננטה
  }, []);

  return (
    <div style={{ padding: '20px', fontFamily: 'Arial, sans-serif', backgroundColor: '#f4f6f9', minHeight: '100vh' }}>
      <header style={{ textAlign: 'center', marginBottom: '30px' }}>
        <h1 style={{ color: '#333' }}>📡 RF Monitoring Dashboard</h1>
        <p style={{ color: '#666' }}>Real-time telemetry and alerts control panel</p>
      </header>

      {loading ? (
        <p style={{ textAlign: 'center' }}>Loading data from API...</p>
      ) : (
        <div style={{ display: 'flex', gap: '20px', flexWrap: 'wrap' }}>
          
          {/* טבלת הדגימות מ-PostgreSQL */}
          <div style={{ flex: 1, minWidth: '450px', background: 'white', padding: '20px', borderRadius: '8px', boxShadow: '0 2px 4px rgba(0,0,0,0.1)' }}>
            <h2 style={{ color: '#007bff', borderBottom: '2px solid #007bff', paddingBottom: '10px' }}>📊 Recent Samples (PostgreSQL)</h2>
            <table style={{ width: '100%', borderCollapse: 'collapse', marginTop: '10px' }}>
              <thead>
                <tr style={{ background: '#f8f9fa', textAlign: 'left' }}>
                  <th style={{ padding: '10px', borderBottom: '1年生 solid #ddd' }}>ID</th>
                  <th style={{ padding: '10px', borderBottom: '1px solid #ddd' }}>Frequency</th>
                  <th style={{ padding: '10px', borderBottom: '1px solid #ddd' }}>Timestamp</th>
                </tr>
              </thead>
              <tbody>
                {samples.map((sample) => (
                  <tr key={sample.id} style={{ borderBottom: '1px solid #eee' }}>
                    <td style={{ padding: '10px', fontSize: '12px', fontFamily: 'monospace' }}>{sample.id}</td>
                    <td style={{ padding: '10px' }}>{sample.frequency} MHz</td>
                    <td style={{ padding: '10px', fontSize: '12px' }}>{new Date(sample.timestamp).toLocaleTimeString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* רשימת ההתראות מ-MongoDB */}
          <div style={{ flex: 1, minWidth: '450px', background: 'white', padding: '20px', borderRadius: '8px', boxShadow: '0 2px 4px rgba(0,0,0,0.1)' }}>
            <h2 style={{ color: '#dc3545', borderBottom: '2px solid #dc3545', paddingBottom: '10px' }}>🚨 Anomalies & Alerts (MongoDB)</h2>
            {alerts.length === 0 ? (
              <p style={{ color: '#666', marginTop: '20px' }}>No alerts detected yet.</p>
            ) : (
              <ul style={{ listStyle: 'none', padding: 0, marginTop: '10px' }}>
                {alerts.map((alert, index) => (
                  <li key={index} style={{ background: '#fff5f5', borderLeft: '5px solid #dc3545', padding: '12px', marginBottom: '10px', borderRadius: '4px' }}>
                    <strong>Packet ID:</strong> <span style={{ fontFamily: 'monospace', fontSize: '12px' }}>{alert.packet_id}</span><br />
                    <strong>Average RSSI:</strong> {alert.average} dBm<br />
                    <span style={{ fontSize: '11px', color: '#999' }}>Time: {alert.timestamp}</span>
                  </li>
                ))}
              </ul>
            )}
          </div>

        </div>
      )}
    </div>
  );
}

export default App;
