import type { Meta, StoryObj } from '@storybook/react-vite';

import { mockSources, mockWikidataSource } from '@/__mocks__/catalogMocks';

import { SourceCitations } from '.';

const meta = {
  title: 'Components/SourceCitations',
  component: SourceCitations,
  args: { citations: [mockSources.rx782Gundam] },
} satisfies Meta<typeof SourceCitations>;

export default meta;

type Story = StoryObj<typeof meta>;

export const GundamWiki: Story = {};

export const SeveralSources: Story = {
  args: {
    citations: [mockSources.rx782Gundam, mockWikidataSource],
    idPrefix: 'story-source',
  },
};
