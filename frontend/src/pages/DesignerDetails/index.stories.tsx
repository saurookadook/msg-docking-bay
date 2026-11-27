import type { Meta, StoryObj } from '@storybook/react-vite';
import { Response as MirageResponse, type Server } from 'miragejs';

import { DesignerDetails } from '.';

const meta = {
  title: 'Pages/DesignerDetails',
  component: DesignerDetails,
  parameters: {
    path: '/mechanical-designers/:mechanicalDesignerSlug',
    route: '/mechanical-designers/kunio-okawara',
  },
} satisfies Meta<typeof DesignerDetails>;

export default meta;

type Story = StoryObj<typeof meta>;

/** @description Kunio Okawara: three designed units, each credited by its own page. */
export const Default: Story = {};

/** @description One credit per page, to show the pager and the page's sources. */
export const Paged: Story = {
  parameters: { route: '/mechanical-designers/kunio-okawara?limit=1' },
};

/** @description Masaki Kawahara: no Japanese name on file, one unit. */
export const Sparse: Story = {
  parameters: { route: '/mechanical-designers/masaki-kawahara' },
};

/** @description An old slug: the page swaps it for the current one. */
export const OldSlug: Story = {
  parameters: { route: '/mechanical-designers/katoki-hajime' },
};

export const NotFound: Story = {
  parameters: { route: '/mechanical-designers/yoshikazu-yasuhiko' },
};

/** @description The credits fail; the designer still shows. */
export const CreditsFailed: Story = {
  parameters: {
    mirage: (server: Server) => {
      server.get(
        '/mechanical-designers/:mechanical_designer_slug/mobile-suits',
        () => new MirageResponse(503, {}, { detail: 'Deck offline' }),
      );
    },
  },
};
