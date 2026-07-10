import { useNavigate } from 'react-router-dom'
import StatusCard from '../components/StatusCard.jsx'
import { SKILLS } from '../skills.js'

export default function Dashboard() {
  const navigate = useNavigate()
  return (
    <div>
      <div className="page-header">
        <h1>Helio Specialist Operations Hub</h1>
        <p>Six Claude Skills, exposed as interactive web tools — from deterministic GWA calculations to LLM-assisted report assembly.</p>
      </div>
      <div className="skill-grid">
        {SKILLS.map((s) => (
          <div key={s.key} className="glass-card skill-card" onClick={() => navigate(s.path)}>
            <div className="skill-icon">{s.icon}</div>
            <h3>{s.name}</h3>
            <p>{s.description}</p>
            <StatusCard type={s.type} />
            <button className="btn launch-btn" type="button">
              Launch Tool →
            </button>
          </div>
        ))}
      </div>
    </div>
  )
}
