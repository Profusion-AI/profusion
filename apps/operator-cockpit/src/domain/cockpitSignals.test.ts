import { describe, expect, it } from "vitest";
import {
  describeFailureJob,
  getCommandPresentation,
  getQueueHealth,
  getReceiptLifecyclePresentation,
} from "./cockpitSignals";

describe("cockpit M7 contract signals", () => {
  it("counts blocked, failed, and active queue states without mutating API payloads", () => {
    const items = [
      { id: "one", status: "planned" },
      { id: "two", status: "qa_failed" },
      { id: "three", status: "scheduled" },
      { id: "four", status: "published" },
    ];

    expect(getQueueHealth(items)).toEqual({
      active: 2,
      blockedOrFailed: 1,
      publishedOrArchived: 1,
    });
  });

  it("presents approve schedule and publish commands as copyable commands only", () => {
    const approve = getCommandPresentation(
      "uv run profusion approve --item-id item_123",
    );
    const schedule = getCommandPresentation(
      "uv run profusion schedule --item-id item_123 --at <iso-datetime> --target <platform:account-id>",
    );
    const publish = getCommandPresentation("uv run profusion publish-due");
    const retry = getCommandPresentation("uv run profusion retry --render-job-id render_123");
    const receiptDraft = getCommandPresentation("uv run profusion receipt draft --item-id item_123");
    const receiptTransition = getCommandPresentation("uv run profusion receipt transition --receipt-id receipt_123 --to reviewed");

    expect(approve).toEqual({
      command: "uv run profusion approve --item-id item_123",
      isMutation: true,
      buttonLabel: "Copy command",
      warning: "Run this in a terminal after verifying the item state.",
    });
    expect(schedule.isMutation).toBe(true);
    expect(schedule.buttonLabel).toBe("Copy command");
    expect(publish.isMutation).toBe(true);
    expect(publish.buttonLabel).toBe("Copy command");
    expect(retry.isMutation).toBe(true);
    expect(retry.buttonLabel).toBe("Copy command");
    expect(receiptDraft.isMutation).toBe(true);
    expect(receiptDraft.buttonLabel).toBe("Copy command");
    expect(receiptTransition.isMutation).toBe(true);
    expect(receiptTransition.buttonLabel).toBe("Copy command");
  });

  it("presents receipt lifecycle status and the next terminal-only transition", () => {
    expect(
      getReceiptLifecyclePresentation({
        receipt_id: "receipt_123",
        receipt_status: "draft",
      }),
    ).toEqual({
      badgeLabel: "Receipt Draft",
      statusLabel: "draft",
      nextCommand: "uv run profusion receipt transition --receipt-id receipt_123 --to reviewed",
    });

    expect(
      getReceiptLifecyclePresentation({
        receipt_id: "receipt_123",
        receipt_status: "approved_for_packet",
      }),
    ).toEqual({
      badgeLabel: "Packet Approved",
      statusLabel: "approved_for_packet",
      nextCommand: "uv run profusion receipt transition --receipt-id receipt_123 --to delivered",
    });
  });

  it("explains failed jobs with stage, message, code, and retry command", () => {
    const renderJob = {
      id: "render_123456789",
      status: "failed",
      error_code: "TURBO_TIMEOUT",
      last_error: "Timed out waiting for render",
      retry: {
        retryable: true,
        command: "uv run profusion retry --render-job-id render_123456789",
      },
    };

    expect(describeFailureJob("render", renderJob)).toEqual({
      id: "render_123456789",
      stage: "render",
      message: "Timed out waiting for render",
      errorCode: "TURBO_TIMEOUT",
      retryable: true,
      retryCommand: "uv run profusion retry --render-job-id render_123456789",
    });
  });
});
