import type { Meta, StoryObj } from '@storybook/react-vite';

import { mockMobileSuits } from '@/__mocks__/mobileSuitMocks';
import type { MobileSuitCardEntity } from '@/api';

import { RosterTable } from '.';
import { rosterColumnHelper } from './rosterColumns';

// NOTE: plain columns of its own: the suits roster's cells belong to MobileSuitList.
const columnHelper = rosterColumnHelper<MobileSuitCardEntity>();
const columns = columnHelper.columns([
  columnHelper.accessor('model_number', { header: 'Model number' }),
  columnHelper.accessor('name', { header: 'Name', meta: { isRowHeader: true } }),
  columnHelper.accessor('name_ja', { header: 'Japanese name' }),
]);

const meta = {
  title: 'Components/RosterTable',
  component: RosterTable<MobileSuitCardEntity>,
  args: {
    caption: 'Cage roster',
    columns,
    rows: mockMobileSuits,
  },
} satisfies Meta<typeof RosterTable<MobileSuitCardEntity>>;

export default meta;

type Story = StoryObj<typeof meta>;

export const Default: Story = {};

/** @description No rows: the frame around it shows the empty state. */
export const Empty: Story = { args: { rows: [] } };
