export default function AuthLayout({
    children,
}: {
    children: React.ReactNode;
}) {
    return <div className="min-h-screen w-full overflow-x-hidden bg-[#050505]">{children}</div>;
}
