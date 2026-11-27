import type { Meta, StoryObj } from '@storybook/react-vite';
import { Response as MirageResponse, type Server } from 'miragejs';

import { mockNow, mockSources } from '@/__mocks__/catalogMocks';
import {
  findWorkMock,
  mockTheOrigin,
  mockTheOriginAdvent,
} from '@/__mocks__/workMocks';
import type { WorkDetailEntity, WorkResponse } from '@/api';

import { WorkDetails } from '.';

/** @description A work fixture, or a clear error if it was renamed or removed. */
function mockWork(slug: string): WorkDetailEntity {
  const work = findWorkMock(slug);
  if (work == null) throw new Error(`[mockWork] : no work mock '${slug}'`);
  return work;
}

const meta = {
  title: 'Pages/WorkDetails',
  component: WorkDetails,
  parameters: { path: '/works/:workSlug', route: '/works/mobile-suit-gundam' },
} satisfies Meta<typeof WorkDetails>;

export default meta;

type Story = StoryObj<typeof meta>;

/** @description Mobile Suit Gundam: a compilation, and two suits that debut in it. */
export const Default: Story = {};

/** @description A film: its run reads "Released", and it compiles the series. */
export const Film: Story = { parameters: { route: '/works/mobile-suit-gundam-i' } };

/** @description Every relation group at once, which the seed data has one type of. */
export const ManyRelations: Story = {
  parameters: {
    mirage: (server: Server) => {
      const source = mockSources.mobileSuitGundamI;
      server.get('/works/:work_slug', (): WorkResponse => ({
        data: {
          ...mockWork('mobile-suit-gundam'),
          relations: [
            {
              created_at: mockNow,
              direction: 'incoming',
              relation_type: 'sequel_of',
              source,
              work: mockTheOrigin,
            },
            {
              created_at: mockNow,
              direction: 'incoming',
              relation_type: 'remake_of',
              source,
              work: mockTheOrigin,
            },
            {
              created_at: mockNow,
              direction: 'incoming',
              relation_type: 'side_story_of',
              source,
              work: mockTheOriginAdvent,
            },
            {
              created_at: mockNow,
              direction: 'outgoing',
              relation_type: 'adaptation_of',
              source,
              work: mockTheOriginAdvent,
            },
          ],
        },
      }));
    },
  },
};

/** @description A documentary with no continuity and no relations. */
export const Sparse: Story = {
  parameters: { route: '/works/it-moves-gundam-follow-your-dreams' },
};

/** @description An old slug, on the second page of suits: the swap keeps the page. */
export const OldSlug: Story = { parameters: { route: '/works/msg?limit=1&offset=1' } };

export const NotFound: Story = { parameters: { route: '/works/turn-a-gundam' } };

/** @description The suit list fails; the log itself still shows. */
export const SuitsFailed: Story = {
  parameters: {
    mirage: (server: Server) => {
      server.get(
        '/works/:work_slug/mobile-suits',
        () => new MirageResponse(503, {}, { detail: 'Deck offline' }),
      );
    },
  },
};
