import { SidebarProvider, SidebarTrigger } from "@/components/ui/sidebar";
import { AppSidebar } from "@/components/AppSidebar";
import { TransactionTable } from "@/components/TransactionTable";
import { ManualCheckModal } from "@/components/ManualCheckModal";
import { ChatBot } from "@/components/ChatBot";
import { Menu, Filter } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { useState } from "react";

export default function Transactions() {
  const [statusFilter, setStatusFilter] = useState("all");

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
                  <h1 className="text-xl font-semibold text-foreground">Transaction Feed</h1>
                  <p className="text-sm text-muted-foreground">
                    Live transaction monitoring
                  </p>
                </div>
              </div>
              <div className="flex items-center gap-3">
                <Select value={statusFilter} onValueChange={setStatusFilter}>
                  <SelectTrigger className="w-40">
                    <Filter className="w-4 h-4 mr-2" />
                    <SelectValue placeholder="Filter" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">All Transactions</SelectItem>
                    <SelectItem value="genuine">Genuine Only</SelectItem>
                    <SelectItem value="fraud">Fraud Only</SelectItem>
                  </SelectContent>
                </Select>
                <ManualCheckModal />
              </div>
            </div>
          </header>

          {/* Content */}
          <div className="p-6">
            <TransactionTable autoUpdate={true} />
          </div>
        </main>
        <ChatBot />
      </div>
    </SidebarProvider>
  );
}
