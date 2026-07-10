import { NavLink } from 'react-router-dom'
import { SKILLS } from '../skills.js'

export default function Sidebar() {
  return (
    <aside className="sidebar">
      <div className="sidebar-brand">Helio Ops Hub</div>
      <div className="sidebar-subtitle">Claude Skills Web Hub</div>
      <nav className="sidebar-nav">
        <NavLink to="/" end className={({ isActive }) => `sidebar-link${isActive ? ' active' : ''}`}>
          <span className="sidebar-emoji">🏠</span> Dashboard
        </NavLink>
        {SKILLS.map((s) => (
          <NavLink key={s.key} to={s.path} className={({ isActive }) => `sidebar-link${isActive ? ' active' : ''}`}>
            <span className="sidebar-emoji">{s.icon}</span> {s.name}
          </NavLink>
        ))}
      </nav>
    </aside>
  )
}
