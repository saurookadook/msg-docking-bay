import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';

import App from '@/app/App';
import { sharedLog } from '@/utils';

import './index.css';

sharedLog.setLevel(import.meta.env.LOG_LEVEL, false);

const rootElement = document.getElementById('root');
if (rootElement == null) {
  throw new Error("[main] : Missing the '#root' element in index.html");
}

createRoot(rootElement).render(
  <StrictMode>
    <App />
  </StrictMode>,
);
