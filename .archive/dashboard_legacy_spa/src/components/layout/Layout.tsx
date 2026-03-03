import { Outlet } from 'react-router-dom';
import Sidebar from './Sidebar';
import Header from './Header';
import AlertFeed from '../AlertFeed';

export default function Layout() {
    return (
        <div className="flex h-screen w-full overflow-hidden bg-background-dark text-slate-100 font-display antialiased selection:bg-primary selection:text-background-dark relative">
            {/* Animated Background Elements */}
            <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-primary/5 rounded-full blur-[120px] animate-pulse-slow"></div>
            <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] bg-emerald-primary/5 rounded-full blur-[120px] animate-pulse-slow" style={{ animationDelay: '1.5s' }}></div>

            <Sidebar />

            <main className="flex-1 flex flex-col h-full overflow-hidden bg-transparent z-10">
                <AlertFeed />
                <Header />
                <div className="flex-1 overflow-y-auto p-4 md:p-8 scroll-smooth custom-scrollbar">
                    <div className="max-w-7xl mx-auto space-y-6">
                        <Outlet />
                    </div>
                </div>
            </main>
        </div>
    );
}
