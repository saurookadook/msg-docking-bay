import type { Meta, StoryObj } from '@storybook/react-vite';

import { Pagination } from '.';

const meta = {
  title: 'Components/Pagination',
  component: Pagination,
  args: { meta: { limit: 50, offset: 0, total: 120 } },
} satisfies Meta<typeof Pagination>;

export default meta;

type Story = StoryObj<typeof meta>;

export const FirstPage: Story = {};

export const MiddlePage: Story = {
  args: { meta: { limit: 50, offset: 50, total: 120 } },
  parameters: { route: '/mobile-suits?offset=50' },
};

export const LastPage: Story = {
  args: { meta: { limit: 50, offset: 100, total: 120 } },
  parameters: { route: '/mobile-suits?offset=100' },
};

/** @description A stale URL whose offset is past the last row. */
export const PastTheEnd: Story = {
  args: { meta: { limit: 50, offset: 400, total: 120 } },
  parameters: { route: '/mobile-suits?offset=400' },
};
