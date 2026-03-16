"use client";

import OracleChatbot from "@/components/OracleChatbot";
import { ArbNotificationBanner } from "@/components/kalshi/ArbNotificationBanner";
import CommandCenter from "@/components/CommandCenter";
import PageTransition from "@/components/layout/PageTransition";
import { TopNav } from "@/components/layout/TopNav";
import Sidebar from "@/components/layout/Sidebar";
import { SportFilterBar } from "@/components/layout/SportFilterBar";
import { TabBar } from "@/components/layout/TabBar";
import NewsTicker from "@/components/NewsTicker";
import { MobileNav } from "@/components/MobileNav";
import { OnboardingProvider } from "@/components/OnboardingProvider";
import { SubscriptionProvider } from "@/hooks/useSubscription";
import { SportProvider } from "@/context/SportContext";
import StatusBar from "@/components/shared/StatusBar";
import PrefetchWrapper from "@/components/shared/PrefetchWrapper";



export default function AppLayout({
    children,
}: {
    children: React.ReactNode;
}) {
    return (
        <SubscriptionProvider>
            <SportProvider>
                <PrefetchWrapper />
                <OnboardingProvider>
                    <div className="flex flex-col h-screen w-full overflow-hidden bg-lucrix-dark text-textPrimary font-sans selection:bg-brand-cyan selection:text-black relative">
                        <StatusBar />
                        {/* Animated Background Elements */}
                        <div className="bg-blob-tl animate-pulse-slow"></div>
                        <div className="bg-blob-br animate-pulse-slow"></div>

                        {/* Navigation Layer */}
                        <TopNav />
                        
                        {/* Main Container below TopNav */}
                        <div className="flex flex-1 overflow-hidden pt-14">
                            <Sidebar />
                            
                            <div className="flex-1 flex flex-col md:ml-[240px] w-full overflow-hidden relative">
                                <SportFilterBar />
                                <NewsTicker />
                                <TabBar />

                                {/* Main Content Scroll Area */}
                                <main className="flex-1 overflow-y-auto overflow-x-hidden scroll-smooth scrollbar-none relative">
                                    <div className="max-w-7xl mx-auto py-6 px-4 sm:px-6">
                                        <PageTransition>
                                            {children}
                                        </PageTransition>
                                    </div>
                                </main>
                            </div>
                        </div>

                        {/* Global Modals & Listeners */}
                        <CommandCenter />
                        <OracleChatbot />
                        <ArbNotificationBanner />
                        <MobileNav />
                    </div>
                </OnboardingProvider>
            </SportProvider>
        </SubscriptionProvider>
    );
}
