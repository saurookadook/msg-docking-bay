import type { Meta, StoryObj } from '@storybook/react-vite';

import { mockMobileSuits } from '@/__mocks__/mobileSuitMocks';
import type { MobileSuitCardEntity } from '@/api';
import { UNIT_TYPE_LABELS } from '@/constants';

import { RosterTable } from '.';
import { rosterColumnHelper } from './rosterColumns';

const helper = rosterColumnHelper<MobileSuitCardEntity>();
const columns = helper.columns([
  helper.accessor('model_number', { header: 'Model number' }),
  helper.accessor('name', { header: 'Name' }),
  helper.accessor('unit_type', {
    cell: ({ getValue }) => UNIT_TYPE_LABELS[getValue()],
    header: 'Unit type',
  }),
  helper.accessor((suit) => suit.continuity?.name ?? '—', {
    header: 'Continuity',
    id: 'continuity',
  }),
]);

const meta = {
  title: 'Components/RosterTable',
  component: RosterTable<MobileSuitCardEntity>,
  args: {
    caption: 'Cage roster',
    columns,
    rowHeaderColumnID: 'name',
    rows: mockMobileSuits,
  },
} satisfies Meta<typeof RosterTable<MobileSuitCardEntity>>;

export default meta;

type Story = StoryObj<typeof meta>;

export const Default: Story = {};

/** @description No rows: the frame around it shows the empty state. */
export const Empty: Story = { args: { rows: [] } };
