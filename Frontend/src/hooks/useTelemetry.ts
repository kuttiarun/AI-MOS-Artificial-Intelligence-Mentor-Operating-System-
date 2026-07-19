import { useEffect, useRef } from "react";

/**
 * AI-MOS Client Interaction Telemetry & Engagement Hook
 * =======================================================
 * Tracks total engagement time and checkpoint validation attempts for the
 * currently active curriculum node. Emits telemetry payloads asynchronously
 * upon unmount, node switches, page hides, or unload events.
 */
export const useTelemetry = (activeNodeId: string) => {
  const startTime = useRef<number>(Date.now());
  const attemptsCount = useRef<number>(0);
  const isPassed = useRef<boolean>(false);

  const incrementAttempts = () => {
    attemptsCount.current += 1;
  };

  const setTelemetryPassed = (passed: boolean) => {
    isPassed.current = passed;
  };

  const sendTelemetryPayload = (
    nodeId: string,
    durationSec: number,
    attempts: number,
    passed: boolean
  ) => {
    if (!nodeId) return;

    const userId = localStorage.getItem("aimos_user_id");
    const url = "http://localhost:8000/api/v1/analytics/log";
    const payload = {
      node_id: nodeId,
      time_spent_seconds: Math.max(0.1, parseFloat(durationSec.toFixed(2))),
      attempts: attempts,
      passed: passed,
    };

    const headers: Record<string, string> = {
      "Content-Type": "application/json",
      ...(userId ? { "X-User-Id": userId } : {}),
    };

    // Use navigator.sendBeacon when page is navigating away/closed
    // wrapped in a Blob to specify application/json content type.
    if (document.visibilityState === "hidden" && navigator.sendBeacon) {
      try {
        const blob = new Blob([JSON.stringify(payload)], { type: "application/json" });
        const queued = navigator.sendBeacon(url, blob);
        if (queued) return;
      } catch (err) {
        // Fall back to standard fetch on error
      }
    }

    // Standard POST fetch with keepalive=true to survive page transitions
    fetch(url, {
      method: "POST",
      headers,
      body: JSON.stringify(payload),
      keepalive: true,
    }).catch(() => {
      // Fail silently to prevent telemetry requests from impacting user experience
    });
  };

  // Trigger telemetry on node exit / switch
  useEffect(() => {
    const currentId = activeNodeId;
    startTime.current = Date.now();
    attemptsCount.current = 0;
    isPassed.current = false;

    return () => {
      const duration = (Date.now() - startTime.current) / 1000;
      // Filter out micro-switches under 200ms to keep telemetry logs clean
      if (duration > 0.2) {
        sendTelemetryPayload(currentId, duration, attemptsCount.current, isPassed.current);
      }
    };
  }, [activeNodeId]);

  // Handle mobile page-hide and browser visibility cycles
  useEffect(() => {
    const handleLifecycle = () => {
      if (document.visibilityState === "hidden") {
        const duration = (Date.now() - startTime.current) / 1000;
        if (duration > 0.2) {
          sendTelemetryPayload(activeNodeId, duration, attemptsCount.current, isPassed.current);
        }
      }
    };

    window.addEventListener("visibilitychange", handleLifecycle);
    window.addEventListener("pagehide", handleLifecycle);

    return () => {
      window.removeEventListener("visibilitychange", handleLifecycle);
      window.removeEventListener("pagehide", handleLifecycle);
    };
  }, [activeNodeId]);

  return {
    incrementAttempts,
    setTelemetryPassed,
  };
};
