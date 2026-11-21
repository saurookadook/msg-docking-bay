"""Entities for ``work_relations`` (PYD-2, PYD-3, PYD-4)."""

import uuid
from typing import Literal

from constants.catalog import WorkRelationType
from models.base.entity import BaseEntityModel
from models.mixins.entity import CreatedAtEntityMixin


class WorkRelationEntity(BaseEntityModel, CreatedAtEntityMixin):
    """A relation row, as stored: "``from`` is a type of ``to``"."""

    from_work_id: uuid.UUID
    relation_type: WorkRelationType
    source_id: uuid.UUID
    to_work_id: uuid.UUID


type RelationDirection = Literal["incoming", "outgoing"]
"""Which end of an edge the viewed row is on (D5).

``outgoing``: the viewed row is ``<relation_type>`` the other one.
``incoming``: the other one is ``<relation_type>`` the viewed row.
"""
