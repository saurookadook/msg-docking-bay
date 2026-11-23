import type { Meta, StoryObj } from '@storybook/react-vite';

import { CageNumber } from '.';

const meta = {
  title: 'Components/CageNumber',
  component: CageNumber,
  args: { cage: 7, deck: 2 },
} satisfies Meta<typeof CageNumber>;

export default meta;

type Story = StoryObj<typeof meta>;

export const Default: Story = {};
