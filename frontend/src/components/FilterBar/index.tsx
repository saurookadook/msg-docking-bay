import classNames from 'classnames';
import { useId } from 'react';
import { useSearchParams } from 'react-router';

import { MAX_SEARCH_LENGTH } from '@/constants';
import { withoutSearchParams, withSearchParam } from '@/utils';

import { useDebouncedSearch } from './utils/hooks';

import './styles.css';

export type FilterBarSelect = {
  label: string;
  options: readonly { label: string; value: string }[];
  /** @description The URL (and API) param the select sets. */
  param: string;
};

export type FilterBarChip = {
  label: string;
  param: string;
  /** @description What the param's value names, such as a work's title. */
  valueLabel: string;
};

export type FilterBarProps = Omit<
  React.FormHTMLAttributes<HTMLFormElement>,
  'onSubmit'
> & {
  /** @description Filters set only through the URL, shown while their param is set. */
  chips?: readonly FilterBarChip[];
  searchLabel: string;
  selects?: readonly FilterBarSelect[];
};

/**
 * @description A roster's search box and filters. Everything lives in the URL's search
 * params: the box writes `q` as typing pauses, a select applies on change, and a chip's
 * button removes its param. Each change starts again from the first page.
 */
export function FilterBar({
  chips = [],
  className,
  searchLabel,
  selects = [],
  ...props
}: FilterBarProps) {
  const [searchParams, setSearchParams] = useSearchParams();
  const { draft, flushDraft, handleBlur, handleDraftChange } = useDebouncedSearch();
  const fieldID = useId();
  const shownChips = chips.filter(({ param }) => searchParams.has(param));
  const filterParams = [
    'q',
    ...selects.map(({ param }) => param),
    ...chips.map(({ param }) => param),
  ];
  const hasActiveFilter = filterParams.some((param) => searchParams.has(param));

  function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    flushDraft();
  }

  function handleSelectChange(param: string, value: string) {
    setSearchParams(withSearchParam({ name: param, searchParams, value }));
  }

  function handleChipRemoveClick(param: string) {
    setSearchParams(withoutSearchParams({ names: [param], searchParams }));
  }

  function handleClearClick() {
    setSearchParams(withoutSearchParams({ names: filterParams, searchParams }));
  }

  return (
    <form
      className={classNames('filter-bar', className)}
      onSubmit={handleSubmit}
      role="search"
      {...props}
    >
      <div className="filter-bar-field">
        <label className="stencil-label" htmlFor={`${fieldID}-q`}>
          {searchLabel}
        </label>
        <input
          id={`${fieldID}-q`}
          maxLength={MAX_SEARCH_LENGTH}
          onBlur={handleBlur}
          onChange={(event) => handleDraftChange(event.target.value)}
          type="search"
          value={draft}
        />
      </div>
      {selects.map(({ label, options, param }) => (
        <div className="filter-bar-field" key={param}>
          <label className="stencil-label" htmlFor={`${fieldID}-${param}`}>
            {label}
          </label>
          <select
            id={`${fieldID}-${param}`}
            onChange={(event) => handleSelectChange(param, event.target.value)}
            value={searchParams.get(param) ?? ''}
          >
            <option value="">All</option>
            {options.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        </div>
      ))}
      {shownChips.length > 0 && (
        <ul aria-label="Active filters" className="filter-bar-chips">
          {shownChips.map(({ label, param, valueLabel }) => (
            <li className="filter-bar-chip" key={param}>
              <span>
                <span className="stencil-label">{label}:</span> {valueLabel}
              </span>
              <button
                aria-label={`Remove the ${label.toLowerCase()} filter: ${valueLabel}`}
                onClick={() => handleChipRemoveClick(param)}
                type="button"
              >
                ×
              </button>
            </li>
          ))}
        </ul>
      )}
      {hasActiveFilter && (
        <button className="filter-bar-clear" onClick={handleClearClick} type="button">
          Clear filters
        </button>
      )}
    </form>
  );
}
