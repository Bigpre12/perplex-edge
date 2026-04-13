import { cookies } from "next/headers";
import { redirect } from "next/navigation";
import LucrixLanding from "@/components/LucrixLanding";

export default function RootPage() {
    const token = cookies().get("lucrix_token")?.value;
    if (token) {
        redirect("/dashboard");
    }
    return <LucrixLanding />;
}
