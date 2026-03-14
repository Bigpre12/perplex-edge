"use client";
import { useHealthMonitor } from "@/hooks/useHealthMonitor";
import { useLucrixStore } from "@/store";

export default function HealthCheck() {
    const { check } = useHealthMonitor();
    const { backendOnline } = useLucrixStore();

    if (backendOnline) return null;

    return (
        <div style={{
            position: "fixed", top: 0, left: 0, right: 0, zIndex: 9999,
            background: "rgba(127, 29, 29, 0.95)", color: "#f87171",
            padding: "12px 20px", textAlign: "center",
            fontSize: "13px", fontWeight: 700,
            borderBottom: "1px solid rgba(248, 113, 113, 0.2)",
            backdropFilter: "blur(10px)",
            display: "flex", alignItems: "center", justifyContent: "center", gap: "15px"
        }}>
            <span style={{ display: "flex", alignItems: "center", gap: "6px" }}>
                <span style={{
                    width: "8px", height: "8px", background: "#f87171",
                    borderRadius: "50%", display: "inline-block",
                    animation: "pulse 2s infinite"
                }}></span>
                🔴 Backend offline — Start your FastAPI server: cd backend && python -m uvicorn app.main:app --reload --port 8000
            </span>
            <button
                onClick={() => check()}
                style={{
                    background: "#f87171", color: "#450a0a",
                    border: "none", borderRadius: "6px",
                    padding: "4px 12px", fontSize: "11px",
                    fontWeight: 800, cursor: "pointer",
                    textTransform: "uppercase", letterSpacing: "0.05em",
                    transition: "all 0.2s ease"
                }}
                onMouseOver={(e) => e.currentTarget.style.opacity = "0.8"}
                onMouseOut={(e) => e.currentTarget.style.opacity = "1"}
            >
                Retry Request
            </button>
            <style>{`
                @keyframes pulse {
                    0% { transform: scale(0.95); opacity: 0.5; }
                    50% { transform: scale(1.05); opacity: 1; }
                    100% { transform: scale(0.95); opacity: 0.5; }
                }
            `}</style>
        </div>
    );
}
