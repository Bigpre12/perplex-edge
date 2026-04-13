"use client";

import Link from "next/link";
import { Button } from "@/components/ui/Button";

export default function LucrixLanding() {
  return (
    <section className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900/50 to-slate-900 text-white overflow-hidden">
      {/* Hero */}
      <div className="container mx-auto px-4 py-20 md:py-32 text-center">
        <h1 className="text-5xl md:text-7xl font-bold bg-gradient-to-r from-white to-purple-300 bg-clip-text text-transparent mb-6">
          Lucrix Sports Betting Intelligence
        </h1>
        <p className="text-xl md:text-2xl mb-8 max-w-3xl mx-auto opacity-90">
          Turn board chaos into <strong>clear, quantified edges</strong>.
          Fuse live odds, player data, and sharp intel to bet like a trading desk.
        </p>
        <div className="flex flex-col sm:flex-row gap-4 justify-center mb-12">
          <Link href="/signup">
            <Button size="lg" className="bg-green-500 hover:bg-green-600 text-lg px-8 py-4 font-semibold w-full sm:w-auto">
              Start Free – Sync Books Now
            </Button>
          </Link>
          <Link href="/login">
            <Button size="lg" variant="outline" className="border-white text-lg px-8 py-4 w-full sm:w-auto">
              See EV Dashboard Demo
            </Button>
          </Link>
        </div>

        <div className="grid md:grid-cols-3 gap-4 max-w-4xl mx-auto opacity-80">
          <div className="bg-gradient-to-r from-emerald-500 to-green-600 p-6 rounded-xl text-center">
            <div className="w-full h-24 bg-gradient-to-r from-red-500/30 to-emerald-500/70 rounded-lg mb-2" />
            <p className="font-mono text-sm">Prop EV +12.4%</p>
          </div>
          <div className="bg-gradient-to-r from-blue-500 to-cyan-600 p-6 rounded-xl text-center">
            <div className="w-full h-24 bg-gradient-to-r from-blue-400/30 to-cyan-500/70 rounded-lg mb-2" />
            <p className="font-mono text-sm">Parlay +18.7% ROI</p>
          </div>
          <div className="bg-gradient-to-r from-orange-500 to-amber-600 p-6 rounded-xl text-center">
            <div className="w-full h-24 bg-gradient-to-r from-amber-400/30 to-orange-500/70 rounded-lg mb-2" />
            <p className="font-mono text-sm">Whale Alert: Sharp Move</p>
          </div>
        </div>
      </div>

      {/* Features */}
      <div className="container mx-auto px-4 py-24">
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-12">
          <div className="text-center md:text-left">
            <h2 className="text-3xl font-bold mb-6">Edge Engine + Parlay Builder</h2>
            <ul className="space-y-3 text-lg">
              <li>• EV/edge % across props, lines, alts in one view</li>
              <li>• AI parlay combos with pricing and ROI tracking</li>
              <li>• Auto-updates as bets settle – refine models daily</li>
            </ul>
          </div>
          <div>
            <h2 className="text-3xl font-bold mb-6">Full Coverage</h2>
            <ul className="space-y-3 text-lg">
              <li>• NBA/NFL/MLB/NHL/NCAA/Tennis/MMA – props + alts</li>
              <li>• Real-time sync: odds, injuries, stats</li>
              <li>• Multi-book fusion for true market edges</li>
            </ul>
          </div>
          <div>
            <h2 className="text-3xl font-bold mb-6">Elite Intel</h2>
            <ul className="space-y-3 text-lg">
              <li>• Steam/whale signals on sharp money moves</li>
              <li>• Global scanner for high-EV liquidity plays</li>
              <li>• Custom thresholds, juice caps, webhook alerts</li>
            </ul>
          </div>
        </div>
      </div>

      {/* Tiers */}
      <div className="bg-slate-800/50 py-20">
        <div className="container mx-auto px-4 text-center">
          <h2 className="text-4xl font-bold mb-12">Tiers for Your Grind</h2>
          <div className="grid md:grid-cols-3 gap-8 max-w-5xl mx-auto">
            <div className="p-8 rounded-2xl border-2 border-purple-500/50 bg-gradient-to-b from-purple-500/10">
              <h3 className="text-2xl font-bold mb-4">Free – The Explorer</h3>
              <ul className="space-y-2 mb-6 text-left">
                <li>• Live odds + basic props</li>
                <li>• Simple edges to test</li>
              </ul>
              <Link href="/signup">
                <Button className="w-full bg-green-500 hover:bg-green-600">Start Free</Button>
              </Link>
            </div>
            <div className="p-8 rounded-2xl border-2 border-emerald-500/50 bg-gradient-to-b from-emerald-500/10">
              <h3 className="text-2xl font-bold mb-4">Pro – The Grinder ($29/mo)</h3>
              <ul className="space-y-2 mb-6 text-left">
                <li>• Full coverage + analytics</li>
                <li>• Parlay engine + tracking</li>
              </ul>
              <Link href="/signup">
                <Button className="w-full bg-emerald-500 hover:bg-emerald-600">Go Pro</Button>
              </Link>
            </div>
            <div className="p-8 rounded-2xl border-2 border-orange-500/50 bg-gradient-to-b from-orange-500/10">
              <h3 className="text-2xl font-bold mb-4">Elite – The Whale ($99/mo)</h3>
              <ul className="space-y-2 mb-6 text-left">
                <li>• Scanner + steam/whale intel</li>
                <li>• Webhooks + full engine</li>
              </ul>
              <Link href="/signup">
                <Button className="w-full bg-orange-500 hover:bg-orange-600">Unlock Elite</Button>
              </Link>
            </div>
          </div>
        </div>
      </div>

      {/* Social Proof */}
      <div className="container mx-auto px-4 py-20 text-center">
        <p className="text-xl mb-8 italic opacity-90">
          &ldquo;Lucrix caught +EV props I missed – up 18% ROI last NBA slate.&rdquo; – Sharp Bettor
        </p>
        <div className="flex justify-center gap-8 mb-12 text-sm opacity-75">
          <div>NBA</div><div>NFL</div><div>MLB</div><div>+10 More</div>
        </div>
        <h3 className="text-2xl font-bold mb-4">Always-On Brain Analyzer</h3>
        <p>Probes endpoints, fixes blind spots, ships upgrades automatically.</p>
      </div>

      {/* Final CTA */}
      <div className="bg-gradient-to-r from-green-600 to-emerald-600 py-16 text-center">
        <div className="container mx-auto px-4">
          <h2 className="text-4xl font-bold mb-6">Ready to Spot Tomorrow&apos;s Edges?</h2>
          <p className="text-xl mb-8 opacity-90">Create account, connect books, bet sharper today.</p>
          <Link href="/signup">
            <Button size="lg" className="bg-white text-slate-900 font-bold px-12 py-6 text-xl shadow-2xl">
              Claim Lucrix Free →
            </Button>
          </Link>
        </div>
      </div>
    </section>
  );
}
