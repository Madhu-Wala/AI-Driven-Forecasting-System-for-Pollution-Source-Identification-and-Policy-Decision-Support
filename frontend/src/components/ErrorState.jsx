export default function ErrorState({ message, onRetry }) {
  return <div className="error-state"><span>{message}</span>{onRetry && <button className="button button-quiet" onClick={onRetry}>Retry</button>}</div>
}
