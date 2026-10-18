import { useEffect } from 'react';

import { fetchHealthCheck, useAppStore, type AppDispatch } from '@/store';
import { sharedLog } from '@/utils';

import './styles.css';

const logger = sharedLog.getLogger('HealthCheck');

export function HealthCheck() {
  const { appState, appDispatch } = useAppStore();
  const { healthCheck, healthCheckErrorMessage, healthCheckRequestInProgress } =
    appState.health;

  useEffect(() => {
    // NOTE: the store outlives this page, so a request still pending after leaving and
    // returning must not overwrite the newer request's result or loading flag.
    let isActive = true;
    const guardedDispatch: AppDispatch = (action) => {
      if (isActive) {
        appDispatch(action);
      }
    };

    void fetchHealthCheck({ dispatch: guardedDispatch }).catch((reason: unknown) =>
      logger.error(reason),
    );

    return () => {
      isActive = false;
    };
  }, [appDispatch]);

  return (
    <section id="health-check" aria-labelledby="health-check-title">
      <h2 id="health-check-title">Health Check</h2>
      {healthCheckRequestInProgress && <p role="status">Checking API health…</p>}
      {healthCheckErrorMessage != null && (
        <p className="health-check-error" role="alert">
          {healthCheckErrorMessage}
        </p>
      )}
      {healthCheck != null && (
        <dl>
          <dt>API status</dt>
          <dd className="health-check-status">{healthCheck.status}</dd>
        </dl>
      )}
    </section>
  );
}
