import { useState } from 'react'
import './App.css'

function App() {
  const [formData, setFormData] = useState({
    ticker_symbol: '',
    risk_appetite: 'Medium',
    time_horizon: 'Medium-term'
  })
  const [apiKeys, setApiKeys] = useState({
    tavily_api_key: '',
    openai_api_key: '',
    alpha_vantage_api_key: ''
  })
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [showWorkflow, setShowWorkflow] = useState(false)
  const [showSettings, setShowSettings] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError(null)
    setResult(null)

    try {
      // Combine form data with API keys, only including non-empty keys
      const requestData = {
        ...formData,
        ...(apiKeys.tavily_api_key && { tavily_api_key: apiKeys.tavily_api_key }),
        ...(apiKeys.openai_api_key && { openai_api_key: apiKeys.openai_api_key }),
        ...(apiKeys.alpha_vantage_api_key && { alpha_vantage_api_key: apiKeys.alpha_vantage_api_key })
      }

      const response = await fetch('/generate-strategy', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestData)
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

  const handleApiKeyChange = (e) => {
    setApiKeys({
      ...apiKeys,
      [e.target.name]: e.target.value
    })
  }

  return (
    <div className="app">
      <div className="container">
        <h1>Trading Bot - Educational Stock Analysis</h1>
        <p className="subtitle">Learn about stock analysis with AI-powered insights</p>

        <div className="settings-section">
          <button
            type="button"
            className="settings-toggle"
            onClick={() => setShowSettings(!showSettings)}
          >
            {showSettings ? '▼' : '▶'} API Settings
          </button>

          {showSettings && (
            <div className="settings-panel">
              <p className="settings-description">
                Configure your API keys below. If left empty, the application will use server-side keys (if available).
              </p>

              <div className="form-group">
                <label htmlFor="tavily_api_key">
                  Tavily API Key
                  <span className="field-help">For web search capabilities</span>
                </label>
                <input
                  type="password"
                  id="tavily_api_key"
                  name="tavily_api_key"
                  value={apiKeys.tavily_api_key}
                  onChange={handleApiKeyChange}
                  placeholder="Enter your Tavily API key (optional)"
                />
                <a
                  href="https://tavily.com/"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="api-link"
                >
                  Get Tavily API Key →
                </a>
              </div>

              <div className="form-group">
                <label htmlFor="openai_api_key">
                  OpenAI API Key
                  <span className="field-help">For AI-powered analysis</span>
                </label>
                <input
                  type="password"
                  id="openai_api_key"
                  name="openai_api_key"
                  value={apiKeys.openai_api_key}
                  onChange={handleApiKeyChange}
                  placeholder="Enter your OpenAI API key (optional)"
                />
                <a
                  href="https://platform.openai.com/api-keys"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="api-link"
                >
                  Get OpenAI API Key →
                </a>
              </div>

              <div className="form-group">
                <label htmlFor="alpha_vantage_api_key">
                  Alpha Vantage API Key
                  <span className="field-help">For financial data access</span>
                </label>
                <input
                  type="password"
                  id="alpha_vantage_api_key"
                  name="alpha_vantage_api_key"
                  value={apiKeys.alpha_vantage_api_key}
                  onChange={handleApiKeyChange}
                  placeholder="Enter your Alpha Vantage API key (optional)"
                />
                <a
                  href="https://www.alphavantage.co/support/#api-key"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="api-link"
                >
                  Get Alpha Vantage API Key →
                </a>
              </div>
            </div>
          )}
        </div>

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
            <label htmlFor="risk_appetite">
              Risk Tolerance Scenario
              <span className="field-help">For educational comparison</span>
            </label>
            <select
              id="risk_appetite"
              name="risk_appetite"
              value={formData.risk_appetite}
              onChange={handleChange}
            >
              <option value="Low">Conservative (Low Volatility Tolerance)</option>
              <option value="Medium">Moderate (Medium Volatility Tolerance)</option>
              <option value="High">Aggressive (High Volatility Tolerance)</option>
            </select>
          </div>

          <div className="form-group">
            <label htmlFor="time_horizon">
              Investment Timeline Scenario
              <span className="field-help">For educational comparison</span>
            </label>
            <select
              id="time_horizon"
              name="time_horizon"
              value={formData.time_horizon}
              onChange={handleChange}
            >
              <option value="Short-term">Short-term (Under 1 year)</option>
              <option value="Medium-term">Medium-term (1-5 years)</option>
              <option value="Long-term">Long-term (5+ years)</option>
            </select>
          </div>

          <div className="scenario-info">
            💡 <strong>About These Scenarios:</strong> These parameters help you explore how different
            investment profiles might evaluate this stock. This is for educational purposes to help you
            understand different analytical perspectives.
          </div>

          <button type="submit" className="submit-btn" disabled={loading}>
            {loading ? 'Analyzing...' : 'Generate Educational Analysis'}
          </button>
        </form>

        <div className="workflow-section">
          <button
            className="workflow-toggle"
            onClick={() => setShowWorkflow(!showWorkflow)}
          >
            {showWorkflow ? '▼' : '▶'} View Workflow Graph
          </button>

          {showWorkflow && (
            <div className="workflow-graph">
              <img
                src="/workflow-graph"
                alt="Workflow Graph"
                className="graph-image"
              />
            </div>
          )}
        </div>

        {error && (
          <div className="result error">
            <h2>Error</h2>
            <p>{error}</p>
          </div>
        )}

        {result && (
          <div className="result success">
            <h2>Stock Analysis Result</h2>
            <div className="action">
              <strong>Analysis Suggestion:</strong> {result.suggested_action}
            </div>
            <div className="reasoning">
              <strong>Educational Reasoning:</strong>
              <p>{result.reasoning}</p>
            </div>
            {result.sources && result.sources.length > 0 && (
              <div className="sources">
                <strong>Sources:</strong>
                <ul>
                  {result.sources.map((source, index) => (
                    <li key={index}>
                      <a href={source.url} target="_blank" rel="noopener noreferrer">
                        {source.title}
                      </a>
                    </li>
                  ))}
                </ul>
              </div>
            )}
            <div className="result-warning">
              <strong>⚠️ Remember:</strong> This is educational content only. Consult a licensed financial adviser before making any investment decisions.
            </div>
          </div>
        )}

        <footer className="footer">
          <div className="footer-disclaimer">
            <p className="footer-disclaimer-text">
              <strong>Legal Disclaimer:</strong> This application provides educational information only and is not intended
              to be investment advice. The creators and operators are not licensed financial advisers, brokers, or investment
              professionals. All stock analysis and suggestions are for educational and informational purposes only.
              Users should conduct their own research and consult with qualified financial professionals before making any
              investment decisions. We make no representations or warranties regarding the accuracy or completeness of the
              information provided. Use of this tool is at your own risk.
            </p>
          </div>
          <p>
            View the source code on{' '}
            <a
              href="https://github.com/miguel-vila/ai-problem-first-capstone?tab=readme-ov-file#trading-bot---ai-powered-investor-assistant"
              target="_blank"
              rel="noopener noreferrer"
            >
              GitHub
            </a>
          </p>
        </footer>
      </div>
    </div>
  )
}

export default App
