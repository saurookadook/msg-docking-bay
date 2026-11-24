import { useId, useRef } from 'react';
import { useSearchParams } from 'react-router';

import type { MobileSuitSpecSheetEntity } from '@/api';
import { DeckPanel, SpecPlate } from '@/components';

import type { Cite } from '../../utils/citations';
import { formatMeasurement, MEASUREMENTS } from '../../utils/format';
import type { SelectedSpecSheet } from '../../utils/hooks';
import { SPEC_PARAM } from '../../utils/specSheets';
import { SuitParts } from '../SuitParts';

import './styles.css';

// NOTE: `Object.keys` types its result as string[]; these are MEASUREMENTS' own keys.
const MEASUREMENT_FIELDS = Object.keys(MEASUREMENTS) as (keyof typeof MEASUREMENTS)[];

/** @description One sheet's name, measurements and parts. */
function SheetContents({
  cite,
  label,
  sheet,
}: {
  cite: Cite;
  label: string;
  sheet: MobileSuitSpecSheetEntity;
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
      <SuitParts sheet={sheet} />
    </>
  );
}

export type SpecSheetTabsProps = {
  cite: Cite;
  selected: SelectedSpecSheet;
  sheets: MobileSuitSpecSheetEntity[];
};

/**
 * @description The suit's spec sheets as configuration tabs (ARIA tabs: arrows, Home and
 * End move between them). The picked sheet is the URL's `?spec=`, replaced on each pick,
 * so the infobox follows it and a link opens it.
 * @note One sheet shows no tabs; none shows "DATA PENDING".
 */
export function SpecSheetTabs({ cite, selected, sheets }: SpecSheetTabsProps) {
  const [, setSearchParams] = useSearchParams();
  const idPrefix = useId();
  const headingID = `${idPrefix}-heading`;
  const tabRefs = useRef<(HTMLButtonElement | null)[]>([]);
  const { index, keys, labels, sheet } = selected;

  function selectSheet(nextIndex: number) {
    setSearchParams(
      (previous) => {
        const nextSearchParams = new URLSearchParams(previous);
        if (nextIndex === 0) nextSearchParams.delete(SPEC_PARAM);
        else nextSearchParams.set(SPEC_PARAM, keys[nextIndex]!);
        return nextSearchParams;
      },
      { replace: true, preventScrollReset: true },
    );
  }

  function handleKeyDown(event: React.KeyboardEvent<HTMLDivElement>) {
    const nextIndex = (function () {
      switch (event.key) {
        case 'ArrowRight':
          return (index + 1) % sheets.length;
        case 'ArrowLeft':
          return (index - 1 + sheets.length) % sheets.length;
        case 'Home':
          return 0;
        case 'End':
          return sheets.length - 1;
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
      {sheet == null && (
        <DeckPanel>
          <p className="stencil-label">DATA PENDING</p>
        </DeckPanel>
      )}
      {sheet != null && sheets.length === 1 && (
        <div className="spec-sheet-panel">
          <SheetContents cite={cite} label={labels[0]!} sheet={sheet} />
        </div>
      )}
      {sheet != null && sheets.length > 1 && (
        <>
          <div
            aria-label="Spec sheets"
            className="spec-sheet-tablist"
            onKeyDown={handleKeyDown}
            role="tablist"
          >
            {keys.map((key, tabIndex) => (
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
                {labels[tabIndex]}
              </button>
            ))}
          </div>
          <div
            aria-labelledby={`${idPrefix}-tab-${keys[index]}`}
            className="spec-sheet-panel"
            id={`${idPrefix}-panel`}
            role="tabpanel"
            tabIndex={0}
          >
            <SheetContents cite={cite} label={labels[index]!} sheet={sheet} />
          </div>
        </>
      )}
    </section>
  );
}
