import { useEffect } from 'react';
import { Link, Outlet } from 'react-router';

import { HazardStripe, ShiftToggle, StatusLamp } from '@/components';
import { hydrateShift, useAppStore } from '@/store';

import { BAY_SIGNS } from './baySigns';
import { BaySign } from './components';

/**
 * @description The app shell, dressed as the MS deck: a status bar, the bay signs, the
 * current route's page, and a footer with the fan-project disclaimer and source credits.
 */
export function Root() {
  const { appDispatch } = useAppStore();

  useEffect(() => {
    hydrateShift({ dispatch: appDispatch });
  }, [appDispatch]);

  return (
    <div id="app-shell">
      <header className="deck-status-bar">
        <h1>
          <Link to="/">MSG Docking Bay</Link>
        </h1>
        <StatusLamp status="online">Deck online</StatusLamp>
        <ShiftToggle />
      </header>
      <HazardStripe />
      <nav aria-label="Bays" className="bay-signs">
        <ul>
          {BAY_SIGNS.map((baySign) => (
            <li key={baySign.kind}>
              <BaySign {...baySign} />
            </li>
          ))}
        </ul>
      </nav>
      <main>
        <Outlet />
      </main>
      <footer className="deck-footer">
        <p>
          MSG Docking Bay is an unofficial fan project. It is not affiliated with or
          endorsed by Sunrise, Bandai Namco or any holder of the Gundam rights.
        </p>
        <p>
          Catalog facts come from the{' '}
          <a href="https://gundam.fandom.com/" rel="external noreferrer">
            Gundam Wiki
          </a>{' '}
          (CC BY-SA) and Wikidata (CC0); every page credits its own sources.
        </p>
        <p>
          <Link to="/health-check">Deck systems</Link>
        </p>
      </footer>
    </div>
  );
}
