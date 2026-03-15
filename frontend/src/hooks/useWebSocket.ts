import { useEffect, useState, useRef, useCallback } from 'react';

export interface Transaction {
    id: string;
    type: 'UPI' | 'CARD';
    amount: number;
    timestamp: string;
    location: string;
    merchant: string;
    currency: string;
}

export interface FraudPrediction {
    is_fraud: boolean;
    risk_score: number;
}

export interface TransactionData {
    transaction: Transaction;
    prediction: FraudPrediction;
}

interface WebSocketMessage {
    type: 'connection' | 'transaction';
    message?: string;
    client_id?: string;
    model_status?: string;
    transaction?: Transaction;
    prediction?: FraudPrediction;
    timestamp?: string;
}

interface UseWebSocketReturn {
    isConnected: boolean;
    transactions: TransactionData[];
    latestTransaction: TransactionData | null;
    stats: {
        total: number;
        fraud: number;
        legit: number;
        fraudRate: number;
    };
}

const WS_URL = import.meta.env.VITE_WS_URL || 'ws://localhost:8000/ws';
const RECONNECT_INTERVAL = 3000;

export const useWebSocket = (): UseWebSocketReturn => {
    const [isConnected, setIsConnected] = useState(false);
    const [transactions, setTransactions] = useState<TransactionData[]>([]);
    const [latestTransaction, setLatestTransaction] = useState<TransactionData | null>(null);
    const wsRef = useRef<WebSocket | null>(null);
    const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);

    const [stats, setStats] = useState({
        total: 0,
        fraud: 0,
        legit: 0,
        fraudRate: 0,
    });

    const connect = useCallback(() => {
        try {
            const ws = new WebSocket(WS_URL);
            wsRef.current = ws;

            ws.onopen = () => {
                console.log('✅ Connected to FraudGuard Backend');
                setIsConnected(true);
            };

            ws.onmessage = (event) => {
                try {
                    const data: WebSocketMessage = JSON.parse(event.data);

                    if (data.type === 'connection') {
                        console.log('🔌 Connection confirmed:', data.message);
                    } else if (data.type === 'transaction' && data.transaction && data.prediction) {
                        const transactionData: TransactionData = {
                            transaction: data.transaction,
                            prediction: data.prediction,
                        };

                        // Update transactions list (keep last 100)
                        setTransactions((prev) => {
                            const updated = [transactionData, ...prev].slice(0, 100);
                            return updated;
                        });

                        // Update latest transaction
                        setLatestTransaction(transactionData);

                        // Update stats
                        setStats((prev) => {
                            const total = prev.total + 1;
                            const fraud = data.prediction!.is_fraud ? prev.fraud + 1 : prev.fraud;
                            const legit = !data.prediction!.is_fraud ? prev.legit + 1 : prev.legit;
                            const fraudRate = total > 0 ? (fraud / total) * 100 : 0;

                            return { total, fraud, legit, fraudRate };
                        });

                        // Log transaction
                        const emoji = data.prediction!.is_fraud ? '🚨' : '✅';
                        console.log(
                            `${emoji} ${data.transaction!.type} | ₹${data.transaction!.amount.toFixed(2)} | ` +
                            `Risk: ${data.prediction!.risk_score.toFixed(3)} | ${data.transaction!.merchant}`
                        );
                    }
                } catch (error) {
                    console.error('Error parsing WebSocket message:', error);
                }
            };

            ws.onerror = (error) => {
                console.error('❌ WebSocket error:', error);
            };

            ws.onclose = () => {
                console.log('🔌 Disconnected from backend');
                setIsConnected(false);
                wsRef.current = null;

                // Attempt to reconnect
                reconnectTimeoutRef.current = setTimeout(() => {
                    console.log('🔄 Reconnecting...');
                    connect();
                }, RECONNECT_INTERVAL);
            };
        } catch (error) {
            console.error('Failed to connect to WebSocket:', error);
        }
    }, []);

    useEffect(() => {
        connect();

        // Cleanup on unmount
        return () => {
            if (reconnectTimeoutRef.current) {
                clearTimeout(reconnectTimeoutRef.current);
            }
            if (wsRef.current) {
                wsRef.current.close();
            }
        };
    }, [connect]);

    return {
        isConnected,
        transactions,
        latestTransaction,
        stats,
    };
};
