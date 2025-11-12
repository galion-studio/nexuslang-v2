import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './Compensation.css';

function Compensation({ workspaceId }) {
  const [summary, setSummary] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (workspaceId) {
      fetchSummary();
    } else {
      setLoading(false);
    }
  }, [workspaceId]);

  const fetchSummary = async () => {
    try {
      const res = await axios.get(`/api/analytics/compensation?workspace_id=${workspaceId}`);
      setSummary(res.data);
      setLoading(false);
    } catch (err) {
      setError('Failed to load compensation data');
      setLoading(false);
    }
  };

  if (!workspaceId) {
    return (
      <div className="empty-state">
        <h2>Select a workspace</h2>
        <p>Go to Tasks to select a workspace first</p>
      </div>
    );
  }

  if (loading) {
    return <div className="loading">Loading...</div>;
  }

  const grandTotal = summary.reduce((sum, user) => sum + user.total_amount, 0);
  const totalHours = summary.reduce((sum, user) => sum + user.total_hours, 0);

  return (
    <div className="compensation-container">
      {error && (
        <div className="error">
          {error}
          <button onClick={() => setError(null)}>✕</button>
        </div>
      )}

      <div className="compensation-header">
        <div>
          <h2>Compensation Ledger</h2>
          <p className="subtitle">Radical transparency: everyone sees everyone's pay</p>
        </div>
        <div className="header-stats">
          <div className="stat">
            <span className="stat-label">Total Hours</span>
            <span className="stat-value">{totalHours.toFixed(1)}h</span>
          </div>
          <div className="stat">
            <span className="stat-label">Total Paid</span>
            <span className="stat-value highlight">${grandTotal.toLocaleString()}</span>
          </div>
        </div>
      </div>

      {summary.length === 0 ? (
        <div className="empty-compensation">
          <h3>No compensation data yet</h3>
          <p>Start logging time to see compensation breakdown</p>
        </div>
      ) : (
        <>
          <div className="compensation-cards">
            {summary.map((user, index) => (
              <CompensationCard key={user.user_id} user={user} rank={index + 1} />
            ))}
          </div>

          <div className="compensation-table-container">
            <table className="compensation-table">
              <thead>
                <tr>
                  <th>Rank</th>
                  <th>Team Member</th>
                  <th>Hourly Rate</th>
                  <th>Hours Worked</th>
                  <th>Total Earned</th>
                  <th>% of Total</th>
                </tr>
              </thead>
              <tbody>
                {summary.map((user, index) => {
                  const percentage = ((user.total_amount / grandTotal) * 100).toFixed(1);
                  return (
                    <tr key={user.user_id}>
                      <td className="rank-cell">
                        {index === 0 && '🥇'}
                        {index === 1 && '🥈'}
                        {index === 2 && '🥉'}
                        {index > 2 && `#${index + 1}`}
                      </td>
                      <td className="name-cell">{user.user_name}</td>
                      <td>${user.hourly_rate}/h</td>
                      <td>{user.total_hours.toFixed(1)}h</td>
                      <td className="amount-cell">${user.total_amount.toLocaleString()}</td>
                      <td className="percentage-cell">
                        <div className="percentage-bar-container">
                          <div 
                            className="percentage-bar" 
                            style={{width: `${percentage}%`}}
                          />
                          <span className="percentage-text">{percentage}%</span>
                        </div>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
              <tfoot>
                <tr>
                  <td colSpan="3"><strong>Total</strong></td>
                  <td><strong>{totalHours.toFixed(1)}h</strong></td>
                  <td className="amount-cell"><strong>${grandTotal.toLocaleString()}</strong></td>
                  <td><strong>100%</strong></td>
                </tr>
              </tfoot>
            </table>
          </div>
        </>
      )}

      <div className="transparency-note">
        <h4>💡 Why Transparency?</h4>
        <p>
          At GALION, we believe fair compensation comes from transparency, not secrecy. 
          When everyone knows what everyone makes, pay is based on value and skills, 
          not negotiation tactics. This creates trust, reduces unfairness, and helps 
          everyone understand their worth.
        </p>
      </div>
    </div>
  );
}

function CompensationCard({ user, rank }) {
  return (
    <div className="comp-card">
      <div className="comp-card-header">
        <div className="rank-badge">
          {rank === 1 && '🥇'}
          {rank === 2 && '🥈'}
          {rank === 3 && '🥉'}
          {rank > 3 && `#${rank}`}
        </div>
        <h3>{user.user_name}</h3>
      </div>
      
      <div className="comp-card-stats">
        <div className="comp-stat">
          <span className="comp-stat-label">Rate</span>
          <span className="comp-stat-value">${user.hourly_rate}/h</span>
        </div>
        <div className="comp-stat">
          <span className="comp-stat-label">Hours</span>
          <span className="comp-stat-value">{user.total_hours.toFixed(1)}h</span>
        </div>
      </div>

      <div className="comp-card-total">
        <span>Total Earned</span>
        <span className="total-amount">${user.total_amount.toLocaleString()}</span>
      </div>
    </div>
  );
}

export default Compensation;

