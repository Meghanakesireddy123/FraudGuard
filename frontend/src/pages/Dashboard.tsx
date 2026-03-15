import { SidebarProvider, SidebarTrigger } from "@/components/ui/sidebar";
import { AppSidebar } from "@/components/AppSidebar";
import { StatsCard } from "@/components/StatsCard";
import { TransactionTable } from "@/components/TransactionTable";
import { ManualCheckModal } from "@/components/ManualCheckModal";
import { ChatBot } from "@/components/ChatBot";
import { Activity, ShieldAlert, ShieldCheck, IndianRupee, Menu } from "lucide-react";
import { useWebSocket } from "@/hooks/useWebSocket";

export default function Dashboard() {
  // Get real-time stats from WebSocket
  const { stats, isConnected } = useWebSocket();

  return (
    <SidebarProvider>
      <div className="min-h-screen flex w-full bg-background">
        <AppSidebar />
        <main className="flex-1 overflow-auto">
          {/* Header */}
          <header className="sticky top-0 z-10 bg-card/80 backdrop-blur-sm border-b border-border px-6 py-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-4">
                <SidebarTrigger className="lg:hidden">
                  <Menu className="w-5 h-5" />
                </SidebarTrigger>
                <div>
                  <h1 className="text-xl font-semibold text-foreground">Dashboard</h1>
                  <p className="text-sm text-muted-foreground">
                    Real-time fraud monitoring overview {isConnected ? '• Live' : '• Offline'}
                  </p>
                </div>
              </div>
              <ManualCheckModal />
            </div>
          </header>

          {/* Content */}
          <div className="p-6 space-y-6">
            {/* Stats Grid */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
              <StatsCard
                title="Total Scanned"
                value={stats.total.toLocaleString()}
                icon={Activity}
                variant="primary"
                subtitle="Real-time count"
              />
              <StatsCard
                title="Fraud Detected"
                value={stats.fraud.toLocaleString()}
                icon={ShieldAlert}
                variant="danger"
                subtitle={`${stats.fraudRate.toFixed(2)}% of total`}
              />
              <StatsCard
                title="Genuine Transactions"
                value={stats.legit.toLocaleString()}
                icon={ShieldCheck}
                variant="success"
                subtitle={`${(100 - stats.fraudRate).toFixed(2)}% success rate`}
              />
              <StatsCard
                title="Fraud Rate"
                value={`${stats.fraudRate.toFixed(2)}%`}
                icon={IndianRupee}
                variant="default"
                subtitle="Live detection rate"
              />
            </div>

            {/* Transaction Table */}
            <TransactionTable />
          </div>
        </main>
        <ChatBot />
      </div>
    </SidebarProvider>
  );
}
