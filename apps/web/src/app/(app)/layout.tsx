import OracleChatbot from "@/components/OracleChatbot";
import { ArbNotificationBanner } from "@/components/kalshi/ArbNotificationBanner";
import CommandCenter from "@/components/CommandCenter";
import PageTransition from "@/components/layout/PageTransition";
import { TopNav } from "@/components/layout/TopNav";
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
                    <div className="flex flex-col h-screen w-full overflow-hidden bg-[#080810] text-[#f1f5f9] font-sans selection:bg-[#F5C518] selection:text-black relative">
                        <StatusBar />
                        {/* Animated Background Elements */}
                        <div className="fixed top-[-10%] left-[-10%] w-[40%] h-[40%] bg-[#F5C518]/5 rounded-full blur-[120px] animate-pulse-slow pointer-events-none"></div>
                        <div className="fixed bottom-[-10%] right-[-10%] w-[40%] h-[40%] bg-[#F5C518]/5 rounded-full blur-[120px] animate-pulse-slow pointer-events-none" style={{ animationDelay: '1.5s' }}></div>

                        {/* Navigation Layer */}
                        <TopNav />
                        <NewsTicker />
                        <TabBar />

                        {/* Main Content Scroll Area */}
                        <main className="flex-1 overflow-y-auto overflow-x-hidden scroll-smooth custom-scrollbar relative">
                            <div className="max-w-7xl mx-auto py-6">
                                <PageTransition>
                                    {children}
                                </PageTransition>
                            </div>
                        </main>

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
