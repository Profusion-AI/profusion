#!/usr/bin/env python3
"""Seed the static cockpit preview with one M7.5 receipt demo packet."""

from __future__ import annotations

import json

from orchestrator import config
from orchestrator.demo_fixtures import seed_content_video_receipt_demo
from orchestrator.receipts.generator import generate_content_video_receipt, receipts_payload


def main() -> None:
    item_id = seed_content_video_receipt_demo(
        db_path=config.DB_PATH,
        renders_dir=config.RENDERS_DIR,
    )
    existing = receipts_payload(receipts_dir=config.RECEIPTS_DIR, item_id=item_id)
    if existing["receipt_count"] == 0:
        receipt = generate_content_video_receipt(
            db_path=config.DB_PATH,
            logs_dir=config.LOGS_DIR,
            receipts_dir=config.RECEIPTS_DIR,
            item_id=item_id,
        )
        payload = receipt.to_payload()
        payload["created"] = True
    else:
        payload = existing["receipts"][0]
        payload["created"] = False

    print(json.dumps({"item_id": item_id, "receipt": payload}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
