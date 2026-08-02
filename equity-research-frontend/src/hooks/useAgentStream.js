// This hook serves as the single switch point.
// For Phase 0, it simply exports the mock stream.
// Later in Phase 5, we will swap this to the real SSE implementation.
export { useMockAgentStream as useAgentStream } from '../mocks/mockAgentStream';
