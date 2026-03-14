import { useLucrixStore } from '@/store';

type StatusListener = (isDown: boolean) => void;

class BackendStatusManager {
    recordFailure() {
        // Now handled by CircuitBreaker in api.ts or useHealthMonitor
        useLucrixStore.getState().setBackendOnline(false);
    }

    recordSuccess() {
        useLucrixStore.getState().setBackendOnline(true);
    }

    getStatus() {
        return !useLucrixStore.getState().backendOnline;
    }

    subscribe(listener: StatusListener) {
        // Subscribe to Zustand store changes
        return useLucrixStore.subscribe((state) => {
            listener(!state.backendOnline);
        });
    }
}

export const backendStatus = new BackendStatusManager();
