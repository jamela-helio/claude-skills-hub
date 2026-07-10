export default function StatusCard({ type }) {
  if (type === 'deterministic') {
    return <span className="status-badge deterministic">⚡ Deterministic / Instant</span>
  }
  return <span className="status-badge llm">✨ Requires Claude API</span>
}
