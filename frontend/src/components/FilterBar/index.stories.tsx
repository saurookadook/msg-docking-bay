import type { Meta, StoryObj } from '@storybook/react-vite';

import { UNIT_TYPE_LABELS } from '@/constants';

import { FilterBar } from '.';

const meta = {
  title: 'Components/FilterBar',
  component: FilterBar,
  args: {
    searchLabel: 'Search mobile suits',
    selects: [
      {
        label: 'Continuity',
        options: [{ label: 'Universal Century', value: 'universal-century' }],
        param: 'continuity',
      },
      {
        label: 'Unit type',
        options: Object.entries(UNIT_TYPE_LABELS).map(([value, label]) => ({
          label,
          value,
        })),
        param: 'unit_type',
      },
    ],
    chips: [{ label: 'Work', param: 'work', valueLabel: 'Mobile Suit Gundam' }],
  },
} satisfies Meta<typeof FilterBar>;

export default meta;

type Story = StoryObj<typeof meta>;

export const Default: Story = {};

/** @description Only a search box, as on the designers roster. */
export const SearchOnly: Story = { args: { chips: [], selects: [] } };
