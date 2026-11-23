import type { Meta, StoryObj } from '@storybook/react-vite';

import { HazardStripe } from '.';

const meta = {
  title: 'Components/HazardStripe',
  component: HazardStripe,
} satisfies Meta<typeof HazardStripe>;

export default meta;

type Story = StoryObj<typeof meta>;

/** @description Hover to make the stripe crawl (when motion is allowed). */
export const Thin: Story = {};

export const Thick: Story = { args: { thick: true } };

export const Crawling: Story = { args: { crawling: true, thick: true } };
