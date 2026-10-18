import { Link } from 'react-router';

import './styles.css';

export function Home() {
  return (
    <section id="home" aria-labelledby="home-title">
      <h2 id="home-title">Welcome aboard</h2>
      <p>MSG Docking Bay is under construction.</p>
      <p>
        Check that the API is reachable on the{' '}
        <Link to="/health-check">health check page</Link>.
      </p>
    </section>
  );
}
