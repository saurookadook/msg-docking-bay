import type { Meta, StoryObj } from '@storybook/react-vite';

import { WorkList } from '.';

const meta = {
  title: 'Pages/WorkList',
  component: WorkList,
  parameters: { route: '/works' },
} satisfies Meta<typeof WorkList>;

export default meta;

type Story = StoryObj<typeof meta>;

export const Default: Story = {};

/** @description One to a page, to show the page links. */
export const Paged: Story = { parameters: { route: '/works?limit=1' } };
