import type { Meta, StoryObj } from '@storybook/react-vite';

import { NotFound } from '.';

const meta = {
  title: 'Pages/NotFound',
  component: NotFound,
  parameters: { route: '/no-such-bay' },
} satisfies Meta<typeof NotFound>;

export default meta;

type Story = StoryObj<typeof meta>;

export const Default: Story = {};
