import React, { useState } from 'react';

export const Team: React.FC = () => {
  const [showToast, setShowToast] = useState(false);
  const [members, setMembers] = useState([
    { id: 1, name: 'You', role: 'Owner', img: 'https://lh3.googleusercontent.com/aida-public/AB6AXuAmHP9GAX8n2ixx76jka6Xa40HnbCE9b7hb6n-6LkS5muPV3wbNNxO_NBbpW_tNONs0E7JsI1XqvFtBQhCM4xfnvAglOkOn3AVkuO2SH4ioTSO6YUft4AkI5L1VTz1CrfTST1hnP81LNyyrWweUqTFW5NO9ODMHqMTY5yF2j-X8mrhrHioSoEdiEuQLhKBS5tBBJfLrVuUT_zgOSen00wyP1dS7_pOyEfXW8fTySHm9s8Nvm2z9H02rAYPBAV3cU7ECx2Bc-wU765Q', status: 'online' },
    { id: 2, name: 'Sarah J.', role: 'Editor', img: 'https://i.pravatar.cc/150?u=sarah', status: 'busy' },
    { id: 3, name: 'Mike T.', role: 'Viewer', img: 'https://i.pravatar.cc/150?u=mike', status: 'offline' },
  ]);

  const handleInvite = () => {
    // Simulate copying invite link
    setShowToast(true);
    setTimeout(() => setShowToast(false), 3000);
  };

  const toggleStatus = (id: number) => {
    setMembers(members.map(m => {
        if (m.id === id) {
            const nextStatus = m.status === 'online' ? 'busy' : m.status === 'busy' ? 'offline' : 'online';
            return { ...m, status: nextStatus };
        }
        return m;
    }));
  };

  return (
    <div className="flex-1 overflow-y-auto no-scrollbar pb-24 px-4 pt-8 relative">
      
      {/* Toast */}
      <div className={`fixed top-24 left-1/2 -translate-x-1/2 z-[60] transition-all duration-300 transform ${showToast ? 'translate-y-0 opacity-100' : '-translate-y-4 opacity-0 pointer-events-none'}`}>
        <div className="bg-surface-darker border border-white/10 text-white px-4 py-2 rounded-full shadow-xl flex items-center gap-2">
          <span className="material-symbols-outlined text-green-500 text-sm">link</span>
          <span className="text-sm font-medium">Invite link copied!</span>
        </div>
      </div>

      <div className="flex items-center justify-between mb-6">
        <h1 className="text-white text-2xl font-bold tracking-tight">Team</h1>
        <button 
            onClick={handleInvite}
            className="text-primary text-sm font-bold bg-primary/10 px-3 py-1.5 rounded-lg hover:bg-primary/20 transition-colors active:scale-95"
        >
            + Invite
        </button>
      </div>

      <div className="space-y-4">
        {members.map((member) => (
            <div 
                key={member.id} 
                onClick={() => toggleStatus(member.id)}
                className="bg-surface-dark border border-white/5 rounded-xl p-4 flex items-center gap-4 cursor-pointer hover:bg-white/5 transition-colors select-none"
            >
                <div className="relative">
                    <img src={member.img} alt={member.name} className="size-12 rounded-full object-cover border border-white/10" />
                    <div className={`absolute bottom-0 right-0 size-3 rounded-full border-2 border-surface-dark transition-colors ${member.status === 'online' ? 'bg-green-500' : member.status === 'busy' ? 'bg-red-500' : 'bg-gray-500'}`}></div>
                </div>
                <div className="flex-1">
                    <h3 className="text-white font-bold text-base">{member.name}</h3>
                    <p className="text-white/40 text-xs">{member.role} • {member.status.charAt(0).toUpperCase() + member.status.slice(1)}</p>
                </div>
                <button className="size-8 rounded-full hover:bg-white/10 flex items-center justify-center text-white/40 hover:text-white">
                    <span className="material-symbols-outlined text-lg">more_vert</span>
                </button>
            </div>
        ))}
      </div>

      <div className="mt-8 bg-gradient-to-br from-primary/20 to-purple-900/20 rounded-xl p-6 border border-primary/20 text-center">
          <div className="size-12 bg-primary/20 text-primary rounded-full flex items-center justify-center mx-auto mb-3">
              <span className="material-symbols-outlined">diamond</span>
          </div>
          <h3 className="text-white font-bold mb-1">Upgrade to Pro</h3>
          <p className="text-white/60 text-xs mb-4">Collaborate with unlimited team members.</p>
          <button className="w-full bg-white text-background-dark font-bold py-2.5 rounded-lg text-sm hover:bg-white/90 active:scale-95 transition-all">
              View Plans
          </button>
      </div>
    </div>
  );
};