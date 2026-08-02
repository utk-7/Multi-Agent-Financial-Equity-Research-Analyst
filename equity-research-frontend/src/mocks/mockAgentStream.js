import { useState, useCallback, useRef } from 'react';

const wait = (ms) => new Promise(resolve => setTimeout(resolve, ms));

export function useMockAgentStream(ticker, runMode) {
  const [events, setEvents] = useState([]);
  const [latestEvent, setLatestEvent] = useState(null);
  const [isConnected, setIsConnected] = useState(false);
  
  const resolveInterruptRef = useRef(null);

  const emit = (event) => {
    const timestamp = new Date().toISOString();
    const eventWithTimestamp = { ...event, payload: { ...event.payload, timestamp } };
    setEvents(prev => [...prev, eventWithTimestamp]);
    setLatestEvent(eventWithTimestamp);
  };

  const startStream = useCallback(async (startTicker, startRunMode) => {
    if (!startTicker) return;
    
    setIsConnected(true);
    setEvents([]);
    setLatestEvent(null);

    // 1. run_started
    emit({ type: 'run_started', payload: { ticker: startTicker, run_mode: startRunMode } });
    await wait(1000);

    // 2. ingestion
    emit({ type: 'node_started', payload: { node: 'ingestion' } });
    await wait(2000);
    emit({ type: 'node_completed', payload: { node: 'ingestion', output_summary: 'Pulled fundamentals + 10-K text' } });
    await wait(500);

    // 3. parallel fan-out
    emit({ type: 'node_started', payload: { node: 'ratio' } });
    emit({ type: 'node_started', payload: { node: 'sentiment' } });
    emit({ type: 'node_started', payload: { node: 'valuation' } });

    if (startTicker === 'ERR') {
        await wait(1500);
        emit({ type: 'node_error', payload: { node: 'sentiment', message: 'Failed to fetch news RSS feed', recoverable: true } });
        setIsConnected(false);
        return;
    }

    // 4. staggered completion
    await wait(1500);
    emit({ type: 'node_completed', payload: { node: 'ratio', output_summary: 'Computed financial ratios' } });
    await wait(1000);
    emit({ type: 'node_completed', payload: { node: 'valuation', output_summary: 'Built 5-year DCF' } });
    await wait(800);
    emit({ type: 'node_completed', payload: { node: 'sentiment', output_summary: 'Scored recent news tone' } });
    await wait(500);

    // 5. red_flag
    emit({ type: 'node_started', payload: { node: 'red_flag' } });
    await wait(2000);
    emit({ type: 'node_completed', payload: { node: 'red_flag', output_summary: 'Forensic checks completed' } });

    // 6. interrupt
    if (startRunMode === 'verified') {
        emit({ 
            type: 'interrupt_paused', 
            payload: { 
                red_flags: [ 
                    { id: 'flag_1', severity: 'high', description: 'FCF vs Net Income divergence', source_ref: 'Cash Flow Statement' },
                    { id: 'flag_2', severity: 'medium', description: 'High leverage compared to peers', source_ref: 'Balance Sheet' }
                ] 
            } 
        });
        
        const { approved_flags, edited_flags } = await new Promise(resolve => {
            resolveInterruptRef.current = resolve;
        });

        emit({ type: 'run_resumed', payload: { approved_flags, edited_flags } });
        await wait(500);
    }

    // 7. synthesis
    emit({ type: 'node_started', payload: { node: 'synthesis' } });
    await wait(2500);
    emit({ type: 'node_completed', payload: { node: 'synthesis', output_summary: 'Final thesis reconciled' } });
    await wait(500);

    // 8. run_completed
    emit({ 
        type: 'run_completed', 
        payload: { 
            final_report: { 
                thesis_summary: "Despite strong brand presence, the company faces headwinds in FCF conversion.",
                bull_case: "Margin expansion through cost-cutting.",
                bear_case: "Continued divergence in net income vs operating cash flow.",
                ratio_table: { "Current Ratio": 1.5, "D/E": 2.1 },
                valuation_range: { "Base": 150, "Bull": 180, "Bear": 110 },
                sensitivity_grid: {},
                red_flags: [
                    { id: 'flag_1', severity: 'high', description: 'FCF vs Net Income divergence' }
                ],
                citations: ["Source 1", "Source 2"],
                eval_metrics: { citation_coverage_pct: 100, groundedness_flag: true }
            }
        } 
    });

    setIsConnected(false);
  }, []);

  const approve = useCallback(() => {
    if (resolveInterruptRef.current) {
        resolveInterruptRef.current({ approved_flags: ['flag_1', 'flag_2'], edited_flags: [] });
        resolveInterruptRef.current = null;
    }
  }, []);

  const editAndApprove = useCallback((editedFlags, approvedFlags) => {
    if (resolveInterruptRef.current) {
        resolveInterruptRef.current({ approved_flags: approvedFlags, edited_flags: editedFlags });
        resolveInterruptRef.current = null;
    }
  }, []);

  return { events, latestEvent, isConnected, startStream, approve, editAndApprove };
}
