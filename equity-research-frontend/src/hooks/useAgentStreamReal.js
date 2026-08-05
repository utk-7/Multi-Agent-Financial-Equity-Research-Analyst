import { useState, useCallback, useRef } from 'react';

export function useAgentStreamReal(ticker, runMode) {
  const [events, setEvents] = useState([]);
  const [latestEvent, setLatestEvent] = useState(null);
  const [isConnected, setIsConnected] = useState(false);
  const [error, setError] = useState(null);
  
  // Store the thread_id to resume later
  const threadIdRef = useRef(null);
  
  // Generate a random thread ID for this session
  if (!threadIdRef.current) {
    threadIdRef.current = `thread_${Date.now()}_${Math.random().toString(36).substring(7)}`;
  }

  const handleEvent = useCallback((type, data) => {
    const eventObj = { type, payload: data };
    
    // Convert backend events to frontend expected formats where necessary
    // Example: node_started, node_completed, etc.
    // Wait, the backend emits 'interrupt_paused', 'run_resumed', 'run_completed'
    // but the frontend UI AgentProgress.jsx expects 'node_started', 'node_completed' for progress
    // Wait, let's look at what the mock was emitting!
    
    setEvents(prev => [...prev, eventObj]);
    setLatestEvent(eventObj);
  }, []);

  const connect = useCallback(() => {
    if (!ticker) return;
    
    setIsConnected(true);
    setEvents([]);
    setLatestEvent(null);
    setError(null);

    // We will use fetch to send the POST request, and then read the body as a stream
    fetch('http://localhost:8000/run', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        ticker,
        run_mode: runMode,
        thread_id: threadIdRef.current
      })
    })
    .then(async (response) => {
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const reader = response.body.getReader();
      const decoder = new TextDecoder('utf-8');
      
      let buffer = '';
      
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        
        buffer += decoder.decode(value, { stream: true });
        
        const lines = buffer.split('\n\n');
        buffer = lines.pop() || ''; // keep the last partial chunk in the buffer
        
        for (const block of lines) {
          if (!block.trim()) continue;
          
          let eventType = 'message';
          let eventData = null;
          
          const linesInBlock = block.split('\n');
          for (const line of linesInBlock) {
            if (line.startsWith('event:')) {
              eventType = line.replace('event:', '').trim();
            } else if (line.startsWith('data:')) {
              try {
                eventData = JSON.parse(line.replace('data:', '').trim());
              } catch(e) {
                eventData = line.replace('data:', '').trim();
              }
            }
          }
          
          handleEvent(eventType, eventData);
          
          if (eventType === 'run_completed' || eventType === 'error') {
            setIsConnected(false);
          }
        }
      }
    })
    .catch(err => {
      console.error("Stream error:", err);
      setError(err.message);
      setIsConnected(false);
    });

  }, [ticker, runMode, handleEvent]);

  const disconnect = useCallback(() => {
    setIsConnected(false);
  }, []);

  const approve = useCallback(async () => {
    if (!latestEvent || latestEvent.type !== 'interrupt_paused') return;
    
    try {
      await fetch('http://localhost:8000/approve', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          thread_id: threadIdRef.current,
          red_flags: latestEvent.payload.red_flags
        })
      });
      // The open fetch stream will naturally receive run_resumed and continue
    } catch(err) {
      console.error("Approval error:", err);
      setError(err.message);
    }
  }, [latestEvent]);

  const editAndApprove = useCallback(async (editedFlags) => {
    if (!latestEvent || latestEvent.type !== 'interrupt_paused') return;
    
    try {
      await fetch('http://localhost:8000/approve', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          thread_id: threadIdRef.current,
          red_flags: editedFlags
        })
      });
    } catch(err) {
      console.error("Approval error:", err);
      setError(err.message);
    }
  }, [latestEvent]);

  return {
    events,
    latestEvent,
    isConnected,
    error,
    startStream: connect,
    disconnect,
    approve,
    editAndApprove,
    threadId: threadIdRef.current // Export threadId so ReportView can use it for PDF export!
  };
}
