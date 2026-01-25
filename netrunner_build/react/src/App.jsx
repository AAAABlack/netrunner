import { useState } from 'react'
import './App.css'
import logo from './assets/images/netrunnerlogo.png'
import bgImage from './assets/images/backgroundimage.jpg'

function App() {
  const [host, setHost] = useState('')
  const [loading, setLoading] = useState(false)
  const [results, setResults] = useState(null)
  const [error, setError] = useState('')

  const handleScan = async (e) => {
    e.preventDefault()
    if (!host) return

    setLoading(true)
    setError('')
    setResults(null)

    try {
      const response = await fetch('/api/scan', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ host }),
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || `Error: ${response.status}`)
      }

      const data = await response.json()
      setResults(data)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const handleRescan = async () => {
    if (!host) return

    setLoading(true)
    setError('')

    try {
      const response = await fetch('/api/scan', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ host, force_rescan: true }),
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || `Error: ${response.status}`)
      }

      const data = await response.json()
      setResults(data)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="app">
      {/* Top Header */}
      <header className="top-header">
        <div className="header-content">
          <div className="header-brand">
            <span className="brand-icon"><img src={logo} alt="NETRUNNER Logo" /></span>
            <span className="brand-text">NETRUNNER</span>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <div className="hero-section">
        <div className="hero-content">
          <h1 className="hero-title">Network Recon</h1>
          <p className="hero-subtitle">Discover open ports, protocols, services, and vulnerabilities</p>
        </div>
      </div>

      {/* Main Container */}
      <div className="main-container">
        {/* Scanner Panel */}
        <div className="scanner-panel">
          <div className="panel-header">
            <h2 className="panel-title">Port Scanner</h2>
            <p className="panel-description">Enter a target IP address or hostname</p>
          </div>

          <form className="scan-form" onSubmit={handleScan}>
            <div className="form-group">
              <label htmlFor="host" className="form-label">Target Host</label>
              <div className="input-wrapper">
                <input
                  type="text"
                  id="host"
                  className="host-input"
                  placeholder="e.g, 8.8.8.8 / example.com"
                  value={host}
                  onChange={(e) => setHost(e.target.value)}
                  required
                />
                <button type="submit" className="scan-button" disabled={loading}>
                  <span className="button-text">{loading ? 'Scanning...' : 'Scan'}</span>
                </button>
              </div>
            </div>
          </form>

          {/* Loading Indicator */}
          {loading && (
            <div className="loading-indicator">
              <div className="spinner"></div>
              <p>Scanning target... This may take a moment.</p>
            </div>
          )}
        </div>

        {/* Results Panel */}
        <div className="results-panel">
          <div id="scanResult" className="scan-result">
            {error && <p style={{ color: 'red' }}>{error}</p>}
            {results && (
              <div>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
                  <h3>Scan Results for {host}</h3>
                  <button 
                    onClick={handleRescan}
                    disabled={loading}
                    style={{
                      padding: '0.5rem 1rem',
                      backgroundColor: '#007bff',
                      color: 'white',
                      border: 'none',
                      borderRadius: '4px',
                      cursor: loading ? 'not-allowed' : 'pointer',
                      fontSize: '0.9rem'
                    }}
                  >
                    {loading ? 'Re-scanning...' : 'Re-scan'}
                  </button>
                </div>
                
                {results.cached && (
                  <div style={{ 
                    backgroundColor: '#fff3cd', 
                    padding: '0.75rem', 
                    borderRadius: '4px', 
                    marginBottom: '1rem',
                    border: '1px solid #ffc107',
                    color: '#856404'
                  }}>
                    ℹ️ <strong>Cached Results:</strong> This data was retrieved from the database. Click "Re-scan" for fresh data.
                  </div>
                )}
                
                {results.scan_metadata && results.scan_metadata.scan_timestamp && (
                  <div style={{ marginBottom: '1rem', color: '#666', fontSize: '0.9rem' }}>
                    <strong>Last scanned:</strong> {new Date(results.scan_metadata.scan_timestamp).toLocaleString()}
                  </div>
                )}
                
                {/* Target Information */}
                {results.target && (
                  <div className="result-section">
                    <h4>Target Information</h4>
                    <p><strong>IP:</strong> {results.target.ip}</p>
                    {results.target.hostnames && results.target.hostnames.length > 0 && (
                      <p><strong>Hostnames:</strong> {results.target.hostnames.join(', ')}</p>
                    )}
                  </div>
                )}

                {/* Attribution */}
                {results.attribution && (
                  <div className="result-section">
                    <h4>Attribution</h4>
                    <p><strong>Organization:</strong> {results.attribution.organization}</p>
                    <p><strong>ISP:</strong> {results.attribution.isp}</p>
                    <p><strong>ASN:</strong> {results.attribution.asn}</p>
                  </div>
                )}

                {/* Geo-location */}
                {results.geolocation && (
                  <div className="result-section">
                    <h4>Geolocation</h4>
                    <p><strong>Country:</strong> {results.geolocation.country}</p>
                    <p><strong>Region:</strong> {results.geolocation.region}</p>
                    <p><strong>City:</strong> {results.geolocation.city}</p>
                  </div>
                )}

                {/* System */}
                {results.system && (
                  <div className="result-section">
                    <h4>System</h4>
                    <p><strong>OS:</strong> {results.system.os}</p>
                  </div>
                )}

                {/* Summary */}
                {results.summary && (
                  <div className="result-section">
                    <h4>Summary</h4>
                    <p><strong>Total Exposed Ports:</strong> {results.summary.total_ports}</p>
                    <p><strong>Total Protocols:</strong> {results.summary.total_services}</p>
                    <p><strong>Identified Services:</strong> {results.summary.identified_products}</p>
                    <p><strong>Vulnerability Count:</strong> {results.summary.vulnerability_count}</p>
                  </div>
                )}

                {/* The Network Exposure section*/}
                {results.network_exposure && (
                  <div className="result-section">
                    <h4>Network Exposure</h4>
                    {results.network_exposure.ports && results.network_exposure.ports.length > 0 && (
                      <p><strong>Open Ports:</strong> {results.network_exposure.ports.join(', ')}</p>
                    )}
                    {results.network_exposure.services && results.network_exposure.services.length > 0 && (
                      <div>
                        <h5>Services & Protocols:</h5>
                        <ul>
                          {results.network_exposure.services.map((service, index) => (
                            <li key={index}>
                              <strong>{service.port}/{service.transport}</strong>: {service.service} ({service.product} {service.version})
                              {service.banner && <br />}<small>{service.banner}</small>
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                )}

                {/* Security interests */}
                {results.security_context && (
                  <div className="result-section">
                    <h4>Security</h4>
                    {results.security_context.tags && results.security_context.tags.length > 0 && (
                      <p><strong>Tags:</strong> {results.security_context.tags.join(', ')}</p>
                    )}
                    <p><strong>Vulnerabilities Present:</strong> {results.security_context.vulns_present ? 'Yes' : 'No'}</p>
                    {results.security_context.vulnerabilities && results.security_context.vulnerabilities.length > 0 && (
                      <div>
                        <h5>Vulnerabilities:</h5>
                        <ul>
                          {results.security_context.vulnerabilities.map((vuln, index) => (
                            <li key={index}>
                              <strong>{vuln.cve}</strong> <br />
                              {vuln.summary}
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* footer, way below */}
      <footer className="footer">
        <p>Netrunner &copy; 2026 | NETRUNNER </p>
      </footer>
    </div>
  )
}

export default App
