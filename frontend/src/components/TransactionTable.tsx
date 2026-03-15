import { useWebSocket } from "@/hooks/useWebSocket";
import { Badge } from "@/components/ui/badge";
import { CreditCard, Smartphone } from "lucide-react";

export interface Transaction {
  id: string;
  status: "genuine" | "fraud";
  time: string;
  type: "UPI" | "Card";
  amount: number;
  merchant?: string;
  riskScore?: number;
}

interface TransactionTableProps {
  autoUpdate?: boolean;
}

export function TransactionTable({ autoUpdate = true }: TransactionTableProps) {
  // Use WebSocket hook to get real transactions from backend
  const { transactions: wsTransactions, isConnected } = useWebSocket();

  // Map WebSocket transactions to component format
  const transactions: Transaction[] = wsTransactions.map((txData) => {
    const time = new Date(txData.transaction.timestamp).toLocaleTimeString("en-US", {
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit",
    });

    return {
      id: txData.transaction.id,
      status: txData.prediction.is_fraud ? "fraud" : "genuine",
      time,
      type: txData.transaction.type === "CARD" ? "Card" : "UPI",
      amount: txData.transaction.amount,
      merchant: txData.transaction.merchant,
      riskScore: txData.prediction.risk_score,
    };
  }).slice(0, 10); // Show only the 10 most recent transactions

  return (
    <div className="bg-card rounded-xl border border-border shadow-card overflow-hidden">
      <div className="p-6 border-b border-border">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-semibold text-foreground">Live Transactions</h3>
          <div className="flex items-center gap-2">
            <span className={`w-2 h-2 rounded-full ${isConnected ? 'bg-success animate-pulse' : 'bg-destructive'}`} />
            <span className="text-xs text-muted-foreground">
              {isConnected ? 'Real-time' : 'Disconnected'}
            </span>
          </div>
        </div>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="border-b border-border bg-muted/50">
              <th className="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">
                Status
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">
                Time
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">
                Transaction ID
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">
                Type
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">
                Merchant
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">
                Risk Score
              </th>
              <th className="px-6 py-3 text-right text-xs font-medium text-muted-foreground uppercase tracking-wider">
                Amount
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-border">
            {transactions.length === 0 ? (
              <tr>
                <td colSpan={7} className="px-6 py-8 text-center text-muted-foreground">
                  {isConnected ? 'Waiting for transactions...' : 'Connecting to backend...'}
                </td>
              </tr>
            ) : (
              transactions.map((transaction, index) => (
                <tr
                  key={transaction.id}
                  className={`transition-all ${index === 0 ? "animate-slide-in bg-accent/30" : "hover:bg-accent/50"}`}
                >
                  <td className="px-6 py-4 whitespace-nowrap">
                    <Badge
                      className={
                        transaction.status === "genuine"
                          ? "bg-success-soft text-success-soft-foreground border-0"
                          : "bg-fraud-soft text-fraud-soft-foreground border-0"
                      }
                    >
                      {transaction.status === "genuine" ? "Genuine" : "Fraud"}
                    </Badge>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-muted-foreground">
                    {transaction.time}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-mono text-foreground">
                    {transaction.id}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center gap-2">
                      {transaction.type === "UPI" ? (
                        <Smartphone className="w-4 h-4 text-muted-foreground" />
                      ) : (
                        <CreditCard className="w-4 h-4 text-muted-foreground" />
                      )}
                      <span className="text-sm text-foreground">{transaction.type}</span>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-foreground">
                    {transaction.merchant || 'N/A'}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">
                    <span className={transaction.status === "fraud" ? "text-destructive font-semibold" : "text-muted-foreground"}>
                      {transaction.riskScore !== undefined ? transaction.riskScore.toFixed(3) : 'N/A'}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-foreground text-right">
                    ₹{transaction.amount.toLocaleString("en-IN")}
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
