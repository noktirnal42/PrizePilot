from __future__ import annotations

import json
import os
from pathlib import Path
from uuid import uuid4

from .models import Opportunity, OpportunityCreate

ROOT = Path(__file__).resolve().parents[2]
FIXTURE_PATH = ROOT / "fixtures" / "opportunities.json"
LOCAL_PATH = ROOT / "data" / "opportunities.local.json"


class OpportunityStore:
    def __init__(self) -> None:
        self.use_firestore = os.getenv("USE_FIRESTORE", "false").lower() == "true"
        self.collection = os.getenv("FIRESTORE_COLLECTION", "opportunities")
        self._firestore = None
        if self.use_firestore:
            try:
                from google.cloud import firestore

                self._firestore = firestore.Client(project=os.getenv("GOOGLE_CLOUD_PROJECT") or None)
            except Exception:
                self._firestore = None
        self._items = self._load_local()

    @property
    def mode(self) -> str:
        return "firestore" if self._firestore else "local-json"

    def _load_local(self) -> dict[str, Opportunity]:
        path = LOCAL_PATH if LOCAL_PATH.exists() else FIXTURE_PATH
        if not path.exists():
            return {}
        raw = json.loads(path.read_text())
        return {item["id"]: Opportunity.model_validate(item) for item in raw}

    def _save_local(self) -> None:
        LOCAL_PATH.parent.mkdir(parents=True, exist_ok=True)
        data = [item.model_dump(mode="json") for item in self._items.values()]
        LOCAL_PATH.write_text(json.dumps(data, indent=2) + "\n")

    def list(self) -> list[Opportunity]:
        if self._firestore:
            docs = self._firestore.collection(self.collection).stream()
            items = [Opportunity.model_validate({"id": doc.id, **doc.to_dict()}) for doc in docs]
            if items:
                return items
        return list(self._items.values())

    def get(self, opportunity_id: str) -> Opportunity | None:
        if self._firestore:
            doc = self._firestore.collection(self.collection).document(opportunity_id).get()
            if doc.exists:
                return Opportunity.model_validate({"id": doc.id, **doc.to_dict()})
        return self._items.get(opportunity_id)

    def upsert(self, opportunity: Opportunity) -> Opportunity:
        if self._firestore:
            payload = opportunity.model_dump(mode="json", exclude={"id"})
            self._firestore.collection(self.collection).document(opportunity.id).set(payload)
            return opportunity
        self._items[opportunity.id] = opportunity
        self._save_local()
        return opportunity

    def create(self, payload: OpportunityCreate) -> Opportunity:
        opportunity = Opportunity(id=str(uuid4()), **payload.model_dump())
        return self.upsert(opportunity)

