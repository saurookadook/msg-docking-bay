import type { Meta, StoryObj } from '@storybook/react-vite';

import { SpecPlate } from '.';

const meta = {
  title: 'Components/SpecPlate',
  component: SpecPlate,
  args: {
    items: [
      { label: 'Model number', value: 'RX-78-2' },
      { label: 'Overall height', value: '18.0 m' },
      {
        label: 'Powerplant',
        value: 'Minovsky ultracompact fusion reactor',
        isInherited: true,
      },
      { label: 'Weight', value: null },
    ],
  },
} satisfies Meta<typeof SpecPlate>;

export default meta;

type Story = StoryObj<typeof meta>;

export const Default: Story = {};

/** @description Every value missing, as on a suit the catalog barely knows. */
export const AllPending: Story = {
  args: {
    items: [
      { label: 'Overall height', value: null },
      { label: 'Weight', value: null },
    ],
  },
};
