import loglevel from 'loglevel';

/**
 * @description The app's root logger. Modules create a named child with
 * `sharedLog.getLogger('<ModuleName>')` (LOG-1).
 * @todo Move to `@app/shared` once the shared workspace exists.
 */
export const sharedLog = loglevel;
