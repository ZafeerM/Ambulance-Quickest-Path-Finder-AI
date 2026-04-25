import { useState, useEffect, useRef, useCallback } from 'react';
import { WS_URL } from '../config/api';
import { gridToPayload } from '../utils/gridUtils';

// Milliseconds between each auto-advance step
const SPEEDS = { slow: 600, normal: 250, fast: 80 };

/**
 * Manages a WebSocket connection AND client-side step playback.
 *
 * The WS streams frames into a buffer (framesRef). A separate
 * setTimeout loop drives which frame is currently displayed,
 * allowing pause / resume / step-by-step control independent
 * of network speed.
 *
 * Returns:
 *   status         – 'idle' | 'connecting' | 'receiving' | 'done' | 'error'
 *   currentGrid    – the grid for the currently displayed frame
 *   messages       – log entries up to the current frame
 *   playIndex      – currently displayed frame index (0-based)
 *   totalFrames    – total frames buffered so far
 *   isPlaying      – whether auto-advance is running
 *   speed          – 'slow' | 'normal' | 'fast'
 *   errorMsg
 *   startRun(grid, rows, cols, algorithm, algoParams)
 *   play()
 *   pause()
 *   stepForward()
 *   stepBackward()
 *   changeSpeed(s)
 */
export function usePathfinder() {
  const wsRef        = useRef(null);
  const framesRef    = useRef([]);   // { grid, type, message }[]
  const statusRef    = useRef('idle');
  const hasErrorRef  = useRef(false);

  const [status,      setStatus]      = useState('idle');
  const [totalFrames, setTotalFrames] = useState(0);
  const [playIndex,   setPlayIndex]   = useState(-1);
  const [isPlaying,   setIsPlaying]   = useState(false);
  const [speed,       setSpeed]       = useState('normal');
  const [errorMsg,    setErrorMsg]    = useState(null);

  useEffect(() => {
    statusRef.current = status;
  }, [status]);

  // ── Playback loop (setTimeout-based so speed changes take effect immediately) ──
  useEffect(() => {
    if (!isPlaying) return;

    const atEnd = playIndex >= totalFrames - 1;

    // Caught up and WS is finished → stop
    if (atEnd && (status === 'done' || status === 'error')) {
      setIsPlaying(false);
      return;
    }

    // Caught up but WS still sending → wait for the next totalFrames tick
    if (atEnd) return;

    const timer = setTimeout(
      () => setPlayIndex((p) => Math.min(p + 1, framesRef.current.length - 1)),
      SPEEDS[speed],
    );
    return () => clearTimeout(timer);
  }, [isPlaying, playIndex, totalFrames, status, speed]);

  // ── Cleanup on unmount ──
  useEffect(() => {
    return () => {
      wsRef.current?.close();
    };
  }, []);

  // ── Controls ──
  const play = useCallback(() => setIsPlaying(true), []);
  const pause = useCallback(() => setIsPlaying(false), []);

  const stepForward = useCallback(() => {
    setIsPlaying(false);
    setPlayIndex((p) => (p < framesRef.current.length - 1 ? p + 1 : p));
  }, []);

  const stepBackward = useCallback(() => {
    setIsPlaying(false);
    setPlayIndex((p) => (p > 0 ? p - 1 : p));
  }, []);

  const changeSpeed = useCallback((s) => setSpeed(s), []);

  const goToStep = useCallback((idx) => {
    setIsPlaying(false);
    setPlayIndex(() => {
      const last = framesRef.current.length - 1;
      if (last < 0) return -1;
      return Math.max(0, Math.min(idx, last));
    });
  }, []);

  // ── Start a new run ──
  const startRun = useCallback(
    (grid, rows, cols, algorithm, algoParams) => {
      // Tear down any previous run
      if (wsRef.current) {
        wsRef.current.onmessage = null;
        wsRef.current.close();
      }
      framesRef.current = [];

      setStatus('connecting');
      setTotalFrames(0);
      setPlayIndex(-1);
      setIsPlaying(false);
      setErrorMsg(null);
      hasErrorRef.current = false;

      const ws = new WebSocket(WS_URL);
      wsRef.current = ws;

      ws.onopen = () => {
        setStatus('receiving');
        const payload = gridToPayload(grid, rows, cols, algorithm, algoParams);
        ws.send(JSON.stringify(payload));
      };

      ws.onmessage = (event) => {
        let data;
        try { data = JSON.parse(event.data); } catch { return; }

        const { type, grid: updatedGrid, message } = data;
        if (!updatedGrid || updatedGrid.length === 0) return;

        framesRef.current.push({ grid: updatedGrid, type, message });
        const newTotal = framesRef.current.length;
        setTotalFrames(newTotal);

        // Auto-start playback when the very first frame arrives
        if (newTotal === 1) {
          setPlayIndex(0);
          setIsPlaying(true);
        }

        if (type === 'done') {
          setStatus('done');
          ws.close();
        } else if (type === 'error') {
          setStatus('error');
          hasErrorRef.current = true;
          setErrorMsg(message);
          ws.close();
        }
      };

      ws.onerror = () => {
        hasErrorRef.current = true;
        setStatus('error');
        setErrorMsg(
          'Could not connect to the server. Make sure the backend is running on port 8000.',
        );
      };

      ws.onclose = () => {
        // If server closes without an explicit done/error frame,
        // finalize gracefully instead of staying stuck in "receiving".
        if (!hasErrorRef.current && statusRef.current === 'receiving') {
          setStatus('done');
        }
      };
    },
    [],
  );

  // ── Derive display values from current playIndex ──
  const frame       = playIndex >= 0 ? framesRef.current[playIndex] : null;
  const currentGrid = frame?.grid ?? null;
  const messages    = framesRef.current
    .slice(0, playIndex + 1)
    .map((f) => ({ type: f.type, text: f.message }));

  return {
    status,
    currentGrid,
    messages,
    playIndex,
    totalFrames,
    isPlaying,
    speed,
    errorMsg,
    startRun,
    play,
    pause,
    stepForward,
    stepBackward,
    goToStep,
    changeSpeed,
  };
}
