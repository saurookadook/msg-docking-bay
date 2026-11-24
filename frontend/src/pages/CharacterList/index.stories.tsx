import type { Meta, StoryObj } from '@storybook/react-vite';

import { CharacterList } from '.';

const meta = {
  title: 'Pages/CharacterList',
  component: CharacterList,
  parameters: { route: '/characters' },
} satisfies Meta<typeof CharacterList>;

export default meta;

type Story = StoryObj<typeof meta>;

export const Default: Story = {};

/** @description One to a page, to show the page links. */
export const Paged: Story = { parameters: { route: '/characters?limit=1' } };
