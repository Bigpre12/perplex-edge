import { useEffect, useRef } from 'react';
import { API, apiFetch } from '@/lib/api';
import { useLucrixStore } from '@/store/useLucrixStore';
import { sendLocalAlert } from '@/lib/notifications';
import { SportKey } from '@/lib/sports.config';

export function useAlerts(sport: SportKey) {
    const { setUnreadAlerts } = useLucrixStore();
    const prevAlertsRef = useRef<string[]>([]);

    useEffect(() => {
        const poll = async () => {
            try {
                const data = await apiFetch<any>(API.alerts(sport));
                const alerts = Array.isArray(data) ? data : (data?.items || []);
                const newIds = alerts.map((a: any) => a.id);
                const fresh = newIds.filter((id: string) => !prevAlertsRef.current.includes(id));

                if (fresh.length > 0 && prevAlertsRef.current.length > 0) {
                    setUnreadAlerts(fresh.length);
                    const first = alerts.find((a: any) => a.id === fresh[0]);
                    if (first) await sendLocalAlert('⚡ Lucrix Alert', first.message);
                }

                prevAlertsRef.current = newIds;
            } catch { }
        };

        poll();
        const t = setInterval(poll, 20_000);
        return () => clearInterval(t);
    }, [sport]);
}
