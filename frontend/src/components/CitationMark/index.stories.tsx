import type { Meta, StoryObj } from '@storybook/react-vite';

import { mockSources } from '@/__mocks__/catalogMocks';
import { SourceCitations } from '@/components/SourceCitations';

import { CitationMark } from '.';

const meta = {
  title: 'Components/CitationMark',
  component: CitationMark,
  args: { idPrefix: 'story-source', number: 1 },
} satisfies Meta<typeof CitationMark>;

export default meta;

type Story = StoryObj<typeof meta>;

/** @description Marks in running text, with the list they point at. */
export const WithSources: Story = {
  render: (args) => (
    <>
      <p>
        Piloted by Amuro Ray
        <CitationMark {...args} />, manufactured by the Earth Federation
        <CitationMark {...args} number={2} />.
      </p>
      <SourceCitations
        citations={[mockSources.rx782Gundam, mockSources.earthFederation]}
        idPrefix={args.idPrefix}
      />
    </>
  ),
};
