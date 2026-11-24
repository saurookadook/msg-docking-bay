import type { Meta, StoryObj } from '@storybook/react-vite';

import { DesignerList } from '.';

const meta = {
  title: 'Pages/DesignerList',
  component: DesignerList,
  parameters: { route: '/mechanical-designers' },
} satisfies Meta<typeof DesignerList>;

export default meta;

type Story = StoryObj<typeof meta>;

export const Default: Story = {};

/** @description One to a page, to show the page links. */
export const Paged: Story = { parameters: { route: '/mechanical-designers?limit=1' } };
