import type { Meta, StoryObj } from '@storybook/react-vite';

import { OrganizationList } from '.';

const meta = {
  title: 'Pages/OrganizationList',
  component: OrganizationList,
  parameters: { route: '/organizations' },
} satisfies Meta<typeof OrganizationList>;

export default meta;

type Story = StoryObj<typeof meta>;

export const Default: Story = {};

/** @description One to a page, to show the page links. */
export const Paged: Story = { parameters: { route: '/organizations?limit=1' } };
