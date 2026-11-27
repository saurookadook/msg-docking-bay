import type { Meta, StoryObj } from '@storybook/react-vite';

import { DeckPanel } from '@/components/DeckPanel';
import { DossierHeader } from '@/components/DossierHeader';
import { DossierStrip } from '@/components/DossierStrip';
import { SpecPlate } from '@/components/SpecPlate';
import { VisualSlot } from '@/components/VisualSlot';

import { DossierLayout } from '.';

const meta = {
  title: 'Components/DossierLayout',
  component: DossierLayout,
  args: {
    children: (
      <>
        <DeckPanel>
          <p>The main column scrolls; the infobox stays pinned beside it.</p>
        </DeckPanel>
        <DeckPanel style={{ minBlockSize: '120vh' }}>
          <p>A tall section, to scroll past.</p>
        </DeckPanel>
      </>
    ),
    header: (
      <DossierHeader
        classLine="TV series · Universal Century"
        eyebrow="Operation log"
        headingID="story-dossier-title"
        name="Mobile Suit Gundam"
        nameJa="機動戦士ガンダム"
      />
    ),
    headingID: 'story-dossier-title',
    id: 'story-dossier',
    infobox: (
      <aside aria-label="Operation data">
        <VisualSlot shape="landscape" subject="Mobile Suit Gundam" />
        <SpecPlate
          isCompact
          items={[
            { label: 'Aired', value: 'Apr 7, 1979 – Jan 26, 1980' },
            { label: 'Studio', value: null },
          ]}
        />
      </aside>
    ),
    strip: <DossierStrip eyebrow="Operation log" name="Mobile Suit Gundam" />,
  },
} satisfies Meta<typeof DossierLayout>;

export default meta;

type Story = StoryObj<typeof meta>;

/** @description Two columns with a sticky infobox; at phone width the strip pins instead. */
export const Default: Story = {};

/** @description A header with no Japanese name, and a strip with no eyebrow. */
export const Sparse: Story = {
  args: {
    header: (
      <DossierHeader
        classLine="Engineering credits"
        eyebrow="Engineering credits"
        headingID="story-dossier-title"
        name="Hajime Katoki"
        nameJa={null}
      />
    ),
    strip: <DossierStrip eyebrow={null} name="Hajime Katoki" />,
  },
};
