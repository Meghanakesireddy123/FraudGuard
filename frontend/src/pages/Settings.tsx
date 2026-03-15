import { SidebarProvider, SidebarTrigger } from "@/components/ui/sidebar";
import { AppSidebar } from "@/components/AppSidebar";
import { ChatBot } from "@/components/ChatBot";
import { Menu, Bell, Shield, User, CreditCard } from "lucide-react";
import { Switch } from "@/components/ui/switch";
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Slider } from "@/components/ui/slider";
import { useState } from "react";

export default function Settings() {
  const [amountThreshold, setAmountThreshold] = useState([10000]);
  const [emailAlerts, setEmailAlerts] = useState(true);
  const [pushAlerts, setPushAlerts] = useState(true);
  const [nightMode, setNightMode] = useState(true);

  return (
    <SidebarProvider>
      <div className="min-h-screen flex w-full bg-background">
        <AppSidebar />
        <main className="flex-1 overflow-auto">
          {/* Header */}
          <header className="sticky top-0 z-10 bg-card/80 backdrop-blur-sm border-b border-border px-6 py-4">
            <div className="flex items-center gap-4">
              <SidebarTrigger className="lg:hidden">
                <Menu className="w-5 h-5" />
              </SidebarTrigger>
              <div>
                <h1 className="text-xl font-semibold text-foreground">Settings</h1>
                <p className="text-sm text-muted-foreground">
                  Configure your fraud detection preferences
                </p>
              </div>
            </div>
          </header>

          {/* Content */}
          <div className="p-6 max-w-3xl space-y-6">
            {/* Profile Section */}
            <div className="bg-card rounded-xl border border-border shadow-card p-6">
              <div className="flex items-center gap-3 mb-6">
                <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center">
                  <User className="w-5 h-5 text-primary" />
                </div>
                <h2 className="text-lg font-semibold text-foreground">Profile Settings</h2>
              </div>
              <div className="grid gap-4 sm:grid-cols-2">
                <div className="space-y-2">
                  <Label htmlFor="name">Full Name</Label>
                  <Input id="name" defaultValue="John Doe" />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="email">Email</Label>
                  <Input id="email" type="email" defaultValue="john@company.com" />
                </div>
              </div>
            </div>

            {/* Fraud Detection Section */}
            <div className="bg-card rounded-xl border border-border shadow-card p-6">
              <div className="flex items-center gap-3 mb-6">
                <div className="w-10 h-10 rounded-lg bg-fraud/10 flex items-center justify-center">
                  <Shield className="w-5 h-5 text-fraud" />
                </div>
                <h2 className="text-lg font-semibold text-foreground">Fraud Detection</h2>
              </div>

              <div className="space-y-6">
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <Label>Amount Threshold (₹)</Label>
                    <span className="text-sm font-medium text-primary">
                      ₹{amountThreshold[0].toLocaleString("en-IN")}
                    </span>
                  </div>
                  <Slider
                    value={amountThreshold}
                    onValueChange={setAmountThreshold}
                    max={100000}
                    min={1000}
                    step={1000}
                    className="w-full"
                  />
                  <p className="text-sm text-muted-foreground">
                    Transactions above this amount will trigger additional verification
                  </p>
                </div>

                <div className="flex items-center justify-between py-3 border-t border-border">
                  <div>
                    <Label>Night Mode Detection</Label>
                    <p className="text-sm text-muted-foreground">
                      Flag transactions between 10 PM - 6 AM
                    </p>
                  </div>
                  <Switch checked={nightMode} onCheckedChange={setNightMode} />
                </div>
              </div>
            </div>

            {/* Notifications Section */}
            <div className="bg-card rounded-xl border border-border shadow-card p-6">
              <div className="flex items-center gap-3 mb-6">
                <div className="w-10 h-10 rounded-lg bg-success/10 flex items-center justify-center">
                  <Bell className="w-5 h-5 text-success" />
                </div>
                <h2 className="text-lg font-semibold text-foreground">Notifications</h2>
              </div>

              <div className="space-y-4">
                <div className="flex items-center justify-between py-3 border-b border-border">
                  <div>
                    <Label>Email Alerts</Label>
                    <p className="text-sm text-muted-foreground">
                      Receive fraud alerts via email
                    </p>
                  </div>
                  <Switch checked={emailAlerts} onCheckedChange={setEmailAlerts} />
                </div>

                <div className="flex items-center justify-between py-3">
                  <div>
                    <Label>Push Notifications</Label>
                    <p className="text-sm text-muted-foreground">
                      Get instant alerts on your device
                    </p>
                  </div>
                  <Switch checked={pushAlerts} onCheckedChange={setPushAlerts} />
                </div>
              </div>
            </div>

            {/* Billing Section */}
            <div className="bg-card rounded-xl border border-border shadow-card p-6">
              <div className="flex items-center gap-3 mb-6">
                <div className="w-10 h-10 rounded-lg bg-secondary flex items-center justify-center">
                  <CreditCard className="w-5 h-5 text-foreground" />
                </div>
                <h2 className="text-lg font-semibold text-foreground">Billing</h2>
              </div>

              <div className="flex items-center justify-between">
                <div>
                  <p className="font-medium text-foreground">Enterprise Plan</p>
                  <p className="text-sm text-muted-foreground">Unlimited transactions • Priority support</p>
                </div>
                <Button variant="outline">Manage Plan</Button>
              </div>
            </div>

            {/* Save Button */}
            <div className="flex justify-end">
              <Button className="bg-primary text-primary-foreground hover:bg-primary/90">
                Save Changes
              </Button>
            </div>
          </div>
        </main>
        <ChatBot />
      </div>
    </SidebarProvider>
  );
}
