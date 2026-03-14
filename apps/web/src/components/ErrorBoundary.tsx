"use client";

import { Component, ReactNode } from "react";
import { AlertTriangle, RefreshCw } from "lucide-react";

interface Props { children: ReactNode; label?: string; }
interface State { hasError: boolean; }

export class ErrorBoundary extends Component<Props, State> {
    state = { hasError: false };

    static getDerivedStateFromError() { return { hasError: true }; }

    render() {
        if (this.state.hasError) return (
            <div className="flex flex-col items-center justify-center py-16 text-center space-y-3">
                <AlertTriangle size={32} className="text-red-400 opacity-60" />
                <p className="text-gray-400 text-sm">{this.props.label ?? "Something went wrong"}</p>
                <button
                    onClick={() => this.setState({ hasError: false })}
                    className="flex items-center gap-1.5 text-indigo-400 hover:text-indigo-300 text-sm transition"
                >
                    <RefreshCw size={13} /> Retry
                </button>
            </div>
        );
        return this.props.children;
    }
}
