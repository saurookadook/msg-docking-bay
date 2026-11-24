import { useId, useRef } from 'react';
import { useSearchParams } from 'react-router';

import { DeckPanel, SpecPlate } from '@/components';

import type { Cite } from '../../utils/citations';
import { formatMeasurement, MEASUREMENTS } from '../../utils/format';
import type { SpecSheetSelection } from '../../utils/hooks';
import { SPEC_PARAM, type SpecSheetEntry } from '../../utils/specSheets';
import { HeightLineup } from '../HeightLineup';
import { SuitParts } from '../SuitParts';

import './styles.css';

// NOTE: `Object.keys` types its result as string[]; these are MEASUREMENTS' own keys.
const MEASUREMENT_FIELDS = Object.keys(MEASUREMENTS) as (keyof typeof MEASUREMENTS)[];

/** @description One sheet's name, measurements and parts. */
function SheetContents({
  cite,
  entry: { label, sheet },
  name,
}: {
  cite: Cite;
  entry: SpecSheetEntry;
  name: string;
}) {
  return (
    <>
      <h4 className="spec-sheet-name stencil-label">
        {label}
        {cite(sheet.source)}
      </h4>
      <SpecPlate
        aria-label="Measurements"
        items={MEASUREMENT_FIELDS.map((field) => ({
          isInherited: sheet.inherited_fields.includes(field),
          label: MEASUREMENTS[field].label,
          value: formatMeasurement({ field, value: sheet[field] }),
        }))}
      />
      <HeightLineup name={name} sheet={sheet} />
      <SuitParts sheet={sheet} />
    </>
  );
}

export type SpecSheetTabsProps = {
  cite: Cite;
  /** @description The suit's name, for the height lineup. */
  name: string;
  selection: SpecSheetSelection;
};

/**
 * @description The suit's spec sheets as configuration tabs (ARIA tabs: arrows, Home and
 * End move between them). The picked sheet is the URL's `?spec=`, replaced on each pick,
 * so the infobox follows it and a link opens it.
 * @note One sheet shows no tabs; none shows "DATA PENDING".
 */
export function SpecSheetTabs({ cite, name, selection }: SpecSheetTabsProps) {
  const [, setSearchParams] = useSearchParams();
  const idPrefix = useId();
  const headingID = `${idPrefix}-heading`;
  const tabRefs = useRef<(HTMLButtonElement | null)[]>([]);
  const { entries, index, selected } = selection;

  function selectSheet(nextIndex: number) {
    const key = entries[nextIndex]?.key;
    setSearchParams(
      (previous) => {
        const nextSearchParams = new URLSearchParams(previous);
        // NOTE: no `spec` is the first sheet, and so is a place with no sheet.
        if (nextIndex === 0 || key == null) nextSearchParams.delete(SPEC_PARAM);
        else nextSearchParams.set(SPEC_PARAM, key);
        return nextSearchParams;
      },
      { replace: true, preventScrollReset: true },
    );
  }

  function handleKeyDown(event: React.KeyboardEvent<HTMLDivElement>) {
    const nextIndex = (function () {
      switch (event.key) {
        case 'ArrowRight':
          return (index + 1) % entries.length;
        case 'ArrowLeft':
          return (index - 1 + entries.length) % entries.length;
        case 'Home':
          return 0;
        case 'End':
          return entries.length - 1;
        default:
          return null;
      }
    })();
    if (nextIndex == null) return;
    event.preventDefault();
    selectSheet(nextIndex);
    tabRefs.current[nextIndex]?.focus();
  }

  return (
    <section aria-labelledby={headingID} className="spec-sheet-tabs">
      <h3 className="stencil-label" id={headingID}>
        Specifications
      </h3>
      {selected == null && (
        <DeckPanel>
          <p className="stencil-label">DATA PENDING</p>
        </DeckPanel>
      )}
      {selected != null && entries.length === 1 && (
        <div className="spec-sheet-panel">
          <SheetContents cite={cite} entry={selected} name={name} />
        </div>
      )}
      {selected != null && entries.length > 1 && (
        <>
          <div
            aria-label="Spec sheets"
            className="spec-sheet-tablist"
            onKeyDown={handleKeyDown}
            role="tablist"
          >
            {entries.map(({ key, label }, tabIndex) => (
              <button
                aria-controls={`${idPrefix}-panel`}
                aria-selected={tabIndex === index}
                className="stencil-label"
                id={`${idPrefix}-tab-${key}`}
                key={key}
                onClick={() => selectSheet(tabIndex)}
                ref={(element) => {
                  tabRefs.current[tabIndex] = element;
                }}
                role="tab"
                tabIndex={tabIndex === index ? 0 : -1}
                type="button"
              >
                {label}
              </button>
            ))}
          </div>
          <div
            aria-labelledby={`${idPrefix}-tab-${selected.key}`}
            className="spec-sheet-panel"
            id={`${idPrefix}-panel`}
            role="tabpanel"
            tabIndex={0}
          >
            <SheetContents cite={cite} entry={selected} name={name} />
          </div>
        </>
      )}
    </section>
  );
}
