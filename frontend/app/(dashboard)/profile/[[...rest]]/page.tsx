import { UserProfile } from "@clerk/nextjs";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Profile",
};

export default function ProfilePage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Profile</h1>
        <p className="text-muted-foreground mt-1">
          Manage your account, email, and security settings.
        </p>
      </div>
      <UserProfile
        appearance={{
          elements: {
            rootBox: "w-full",
            card: "shadow-sm border border-border rounded-2xl",
            navbar: "border-r border-border",
            navbarButton: "rounded-xl",
            headerTitle: "font-bold",
            pageScrollBox: "p-6",
            formButtonPrimary: "bg-blue-600 hover:bg-blue-700 rounded-xl",
            formFieldInput: "rounded-xl border-input",
            badge: "rounded-full",
            avatarImageActionsUpload: "rounded-xl",
            profileSectionPrimaryButton: "text-blue-600",
          },
        }}
      />
    </div>
  );
}
