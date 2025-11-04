import { useState } from 'react'
import './App.css'

function App() {
  const [formData, setFormData] = useState({
    ticker_symbol: '',
    risk_appetite: 'Medium',
    investment_experience: 'Intermediate',
    time_horizon: 'Medium-term'
  })
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError(null)
    setResult(null)

    try {
      const response = await fetch('/generate-strategy', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData)
      })

      if (!response.ok) {
        throw new Error('Failed to generate strategy')
      }

      const data = await response.json()
      setResult(data)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    })
  }

  return (
    <div className="app">
      <div className="container">
        <h1>Trading Bot - Investor Assistant</h1>
        <p className="subtitle">Get AI-powered investment recommendations</p>

        <form onSubmit={handleSubmit} className="form">
          <div className="form-group">
            <label htmlFor="ticker_symbol">Ticker Symbol</label>
            <input
              type="text"
              id="ticker_symbol"
              name="ticker_symbol"
              value={formData.ticker_symbol}
              onChange={handleChange}
              placeholder="e.g., AAPL, MSFT"
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="risk_appetite">Risk Appetite</label>
            <select
              id="risk_appetite"
              name="risk_appetite"
              value={formData.risk_appetite}
              onChange={handleChange}
            >
              <option value="Low">Low</option>
              <option value="Medium">Medium</option>
              <option value="High">High</option>
            </select>
          </div>

          <div className="form-group">
            <label htmlFor="investment_experience">Investment Experience</label>
            <select
              id="investment_experience"
              name="investment_experience"
              value={formData.investment_experience}
              onChange={handleChange}
            >
              <option value="Beginner">Beginner</option>
              <option value="Intermediate">Intermediate</option>
              <option value="Expert">Expert</option>
            </select>
          </div>

          <div className="form-group">
            <label htmlFor="time_horizon">Time Horizon</label>
            <select
              id="time_horizon"
              name="time_horizon"
              value={formData.time_horizon}
              onChange={handleChange}
            >
              <option value="Short-term">Short-term</option>
              <option value="Medium-term">Medium-term</option>
              <option value="Long-term">Long-term</option>
            </select>
          </div>

          <button type="submit" className="submit-btn" disabled={loading}>
            {loading ? 'Generating...' : 'Generate Strategy'}
          </button>
        </form>

        {error && (
          <div className="result error">
            <h2>Error</h2>
            <p>{error}</p>
          </div>
        )}

        {result && (
          <div className="result success">
            <h2>Investment Recommendation</h2>
            <div className="action">
              <strong>Suggested Action:</strong> {result.suggested_action}
            </div>
            <div className="reasoning">
              <strong>Reasoning:</strong>
              <p>{result.reasoning}</p>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default App
