import type { Meta, StoryObj } from '@storybook/react-vite';

import { mockMobileSuits } from '@/__mocks__/mobileSuitMocks';
import type { MobileSuitCardEntity } from '@/api';
import { FilterBar, rosterColumnHelper } from '@/components';
import { createInitialListState } from '@/store';

import { CatalogRoster } from '.';

const columnHelper = rosterColumnHelper<MobileSuitCardEntity>();
const columns = columnHelper.columns([
  columnHelper.accessor('model_number', { header: 'Model number' }),
  columnHelper.accessor('name', { header: 'Name' }),
]);

const mockLoadedList = {
  ...createInitialListState<MobileSuitCardEntity>(),
  items: [...mockMobileSuits],
  meta: { limit: 50, offset: 0, total: mockMobileSuits.length },
  search: '',
};

const meta = {
  title: 'Components/CatalogRoster',
  component: CatalogRoster<MobileSuitCardEntity>,
  args: {
    caption: 'Mobile suits in their cages',
    columns,
    eyebrow: 'MS DECK 01',
    filterBar: <FilterBar searchLabel="Search mobile suits" />,
    heading: 'Mobile Suits',
    id: 'mobile-suits',
    list: mockLoadedList,
    rowHeaderColumnID: 'name',
  },
} satisfies Meta<typeof CatalogRoster<MobileSuitCardEntity>>;

export default meta;

type Story = StoryObj<typeof meta>;

export const Default: Story = {};

/** @description The first request is still in flight. */
export const Loading: Story = {
  args: {
    list: {
      ...createInitialListState<MobileSuitCardEntity>(),
      requestInProgress: true,
    },
  },
};

/** @description Nothing matches the filters, with a way to clear them. */
export const Empty: Story = {
  args: {
    list: {
      ...mockLoadedList,
      items: [],
      meta: { limit: 50, offset: 0, total: 0 },
    },
  },
};

/** @description The API refused the request, and its message is shown. */
export const Failed: Story = {
  args: {
    list: {
      ...createInitialListState<MobileSuitCardEntity>(),
      errorMessage: "unit_type: Input should be 'suit'",
    },
  },
};
