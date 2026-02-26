/* eslint-disable @typescript-eslint/no-explicit-any */
import { NavLink } from 'react-router-dom';
import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

function cn(...inputs: any[]) {
    return twMerge(clsx(inputs));
}

export default function Sidebar() {
    return (
        <aside className="w-64 flex-shrink-0 border-r border-slate-800 bg-[#102023] flex flex-col justify-between p-4 z-20 h-full">
            <div className="flex flex-col gap-8">
                <div className="flex items-center gap-3 px-2">
                    <div className="h-10 w-10 rounded-xl bg-gradient-to-br from-primary to-cyan-700 flex items-center justify-center shadow-lg shadow-primary/20">
                        <span className="material-symbols-outlined text-white text-2xl">psychology</span>
                    </div>
                    <div className="flex flex-col">
                        <h1 className="text-white text-base font-bold leading-tight tracking-wide uppercase">PERPLEX</h1>
                        <p className="text-secondary text-xs font-normal">Engine Console</p>
                    </div>
                </div>

                <nav className="flex flex-col gap-2">
                    <p className="px-3 text-xs font-semibold text-secondary/50 uppercase tracking-wider mb-1">Main Menu</p>

                    <NavItem to="/" icon="dashboard" label="Dashboard" />
                    <NavItem to="/market-analysis" icon="analytics" label="Market Analysis" />
                    <NavItem to="/player-props" icon="bolt" label="Player Props" />
                    <NavItem to="/parlay-builder" icon="check_circle" label="Parlay Builder" />
                    <NavItem to="/shared-intel" icon="hub" label="Shared Intel" />
                </nav>
            </div>

            <div className="mt-auto px-3 py-4 rounded-xl bg-surface border border-slate-800/50">
                <div className="flex items-center gap-3">
                    <div className="bg-center bg-no-repeat bg-cover rounded-full h-9 w-9 ring-2 ring-primary/20"
                        style={{ backgroundImage: 'url("https://lh3.googleusercontent.com/aida-public/AB6AXuDqAi3iO6M8PHkZ9gRO3DmmMlw-Z-ZJrWigk8-PXYf7sEldJK3MhIy0X1NOM0zjDO8zY2zSxx0Mpc_yyGWxLqTny49lgKbUq_uarK6mwiWPnHE6RjOj08mX5h_D7eKtxLhRQHNHyhS-tJ0NEfwPgmHayWkg-ZKtMy40xez_-Up5bYVhgdtbQ-C18WN2hp9JWjgFaq0TLNpHneVutnEl7wV0vAYMGvnikgkYXkebOHM6Lummy-8B-ZS-6_d-xG3cSXNnNnpV1M8InphA")' }}>
                    </div>
                    <div className="flex flex-col overflow-hidden">
                        <span className="text-white text-sm font-medium truncate">Alex Chen</span>
                        <span className="text-secondary text-xs truncate">Lead Analyst</span>
                    </div>
                </div>
            </div>
        </aside>
    );
}

function NavItem({ to, icon, label }: { to: string; icon: string; label: string }) {
    return (
        <NavLink
            to={to}
            className={({ isActive }) => cn(
                "flex items-center gap-3 px-3 py-2.5 rounded-lg transition-all group",
                isActive
                    ? "bg-primary/10 border border-primary/20 text-white"
                    : "text-secondary hover:bg-surface-highlight hover:text-white border border-transparent"
            )}
        >
            {({ isActive }) => (
                <>
                    <span className={cn(
                        "material-symbols-outlined group-hover:scale-110 transition-transform",
                        isActive ? "text-primary" : "text-secondary"
                    )}>
                        {icon}
                    </span>
                    <span className="text-sm font-medium">{label}</span>
                </>
            )}
        </NavLink>
    );
}
