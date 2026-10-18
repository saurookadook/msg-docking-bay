import { NavLink, Outlet } from 'react-router';

/** @description The app shell: top navigation, then the current route's page. */
export function Root() {
  return (
    <div id="app-shell">
      <header className="top-nav-bar">
        <h1>MSG Docking Bay</h1>
        <nav aria-label="Main">
          <NavLink to="/" end>
            Home
          </NavLink>
          <NavLink to="/health-check">Health check</NavLink>
        </nav>
      </header>
      <main>
        <Outlet />
      </main>
    </div>
  );
}
