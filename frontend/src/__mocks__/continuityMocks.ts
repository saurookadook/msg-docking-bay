// Read from the 2026-11-15 Gundam Wiki dump; `backend/scripts/seed_dev.py` holds the
// other copy (see `catalogMocks.ts`).
import type { ContinuitiesListResponse, ContinuityCardEntity } from '@/api';

import { mockNow, mockUniversalCenturyRef } from './catalogMocks';

export const mockUniversalCentury: ContinuityCardEntity = {
  ...mockUniversalCenturyRef,
  created_at: mockNow,
  parent_continuity: null,
  updated_at: mockNow,
};

export const mockContinuitiesListResponse: ContinuitiesListResponse = {
  data: [mockUniversalCentury],
};
