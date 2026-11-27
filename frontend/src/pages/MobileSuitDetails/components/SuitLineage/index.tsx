import classNames from 'classnames';
import { useId } from 'react';

import type { MobileSuitDetailEntity } from '@/api';
import { EntityLink, type Cite } from '@/components';

import { buildLineage, type LineageGroup } from '../../utils/lineage';
import { ModelNumber } from '../ModelNumber';

import './styles.css';

/** @description One tier of the dev-tree: its labelled groups of related suits. */
function LineageTierGroups({
  cite,
  className,
  groups,
}: {
  cite: Cite;
  className: string;
  groups: LineageGroup[];
}) {
  return (
    <div className={classNames('suit-lineage-groups', className)}>
      {groups.map(({ key, label, relations }) => (
        <div className="suit-lineage-group" key={key}>
          <h4 className="stencil-label">{label}</h4>
          <ul aria-label={label} className="plain-list">
            {relations.map(({ direction, mobile_suit, relation_type, source }) => (
              <li
                className="tier-node"
                key={`${relation_type}-${direction}-${mobile_suit.slug}`}
              >
                <ModelNumber
                  className="suit-lineage-model"
                  modelNumber={mobile_suit.model_number}
                />
                <EntityLink kind="mobileSuit" slug={mobile_suit.slug}>
                  {mobile_suit.name}
                </EntityLink>
                {cite(source)}
              </li>
            ))}
          </ul>
        </div>
      ))}
    </div>
  );
}

export type SuitLineageProps = {
  cite: Cite;
  suit: MobileSuitDetailEntity;
};

/**
 * @description The suit's direct relations as a small dev-tree: what it came from above,
 * what came from it below, and its alternate versions beside it.
 * @returns nothing when the catalog lists no relation
 */
export function SuitLineage({ cite, suit }: SuitLineageProps) {
  const headingID = useId();
  const { ancestors, alternates, descendants } = buildLineage(suit.relations);

  if (suit.relations.length === 0) return null;

  return (
    <section aria-labelledby={headingID} className="suit-lineage">
      <h3 className="stencil-label" id={headingID}>
        Variants &amp; lineage
      </h3>
      <div className="tier-tree">
        {ancestors.length > 0 && (
          <LineageTierGroups
            cite={cite}
            className="suit-lineage-ancestors"
            groups={ancestors}
          />
        )}
        <div className="suit-lineage-current">
          <p aria-current="page" className="tier-node">
            <ModelNumber
              className="suit-lineage-model"
              modelNumber={suit.model_number}
            />
            <span>{suit.name}</span>
          </p>
          {alternates.length > 0 && (
            <LineageTierGroups
              cite={cite}
              className="suit-lineage-alternates"
              groups={alternates}
            />
          )}
        </div>
        {descendants.length > 0 && (
          <LineageTierGroups
            cite={cite}
            className="suit-lineage-descendants"
            groups={descendants}
          />
        )}
      </div>
    </section>
  );
}
