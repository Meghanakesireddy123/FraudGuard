import { useState } from "react";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Search, ShieldCheck, ShieldAlert, Loader2, AlertCircle, ChevronDown, ChevronUp } from "lucide-react";
import { Alert, AlertDescription } from "@/components/ui/alert";

interface PredictionResult {
  transaction: {
    id: string;
    type: string;
    amount: number;
    merchant: string;
    category: string;
    location: string;
    timestamp: string;
    gender?: string;
    job?: string;
    age?: number;
  };
  prediction: {
    is_fraud: boolean;
    risk_score: number;
  };
  model_type: string;
}

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export function ManualCheckModal() {
  const [open, setOpen] = useState(false);
  const [showAdvanced, setShowAdvanced] = useState(false);

  // Basic fields (always shown)
  const [transactionType, setTransactionType] = useState("UPI");
  const [amount, setAmount] = useState("");
  const [merchant, setMerchant] = useState("");
  const [category, setCategory] = useState("general");
  const [location, setLocation] = useState("");

  // Advanced fields (optional, collapsible)
  const [transactionId, setTransactionId] = useState("");
  const [timestamp, setTimestamp] = useState("");
  const [gender, setGender] = useState("M");
  const [job, setJob] = useState("");
  const [age, setAge] = useState("");
  const [lat, setLat] = useState("");
  const [long, setLong] = useState("");
  const [cityPop, setCityPop] = useState("");
  const [merchLat, setMerchLat] = useState("");
  const [merchLong, setMerchLong] = useState("");

  // State
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [result, setResult] = useState<PredictionResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  const analyzeTransaction = async () => {
    setIsAnalyzing(true);
    setResult(null);
    setError(null);

    try {
      const requestBody: Record<string, string | number> = {
        transaction_type: transactionType,
        amount: parseFloat(amount),
        merchant: merchant,
        category: category,
        location: location || "Manual Entry",
      };

      // Add advanced fields if provided
      if (transactionId) requestBody.transaction_id = transactionId;
      if (timestamp) requestBody.timestamp = timestamp;
      if (gender) requestBody.gender = gender;
      if (job) requestBody.job = job;
      if (age) requestBody.age = parseInt(age);
      if (lat) requestBody.lat = parseFloat(lat);
      if (long) requestBody.long = parseFloat(long);
      if (cityPop) requestBody.city_pop = parseInt(cityPop);
      if (merchLat) requestBody.merch_lat = parseFloat(merchLat);
      if (merchLong) requestBody.merch_long = parseFloat(merchLong);

      const response = await fetch(`${API_URL}/check-transaction`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestBody),
      });

      if (!response.ok) {
        throw new Error(`API error: ${response.statusText}`);
      }

      const data: PredictionResult = await response.json();
      setResult(data);
    } catch (err) {
      console.error('Error checking transaction:', err);
      setError(err instanceof Error ? err.message : 'Failed to check transaction');
    } finally {
      setIsAnalyzing(false);
    }
  };

  const resetForm = () => {
    setTransactionType("UPI");
    setAmount("");
    setMerchant("");
    setCategory("general");
    setLocation("");
    setTransactionId("");
    setTimestamp("");
    setGender("M");
    setJob("");
    setAge("");
    setLat("");
    setLong("");
    setCityPop("");
    setMerchLat("");
    setMerchLong("");
    setResult(null);
    setError(null);
    setShowAdvanced(false);
  };

  const isFormValid = amount && merchant && parseFloat(amount) > 0;

  return (
    <Dialog open={open} onOpenChange={(isOpen) => {
      setOpen(isOpen);
      if (!isOpen) resetForm();
    }}>
      <DialogTrigger asChild>
        <Button className="gap-2 bg-primary text-primary-foreground hover:bg-primary/90">
          <Search className="w-4 h-4" />
          Check Transaction
        </Button>
      </DialogTrigger>
      <DialogContent className="sm:max-w-2xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Search className="w-5 h-5 text-primary" />
            Manual Transaction Check - Comprehensive Mode
          </DialogTitle>
        </DialogHeader>

        {!result ? (
          <div className="space-y-4 py-4">
            {/* Basic Fields Section */}
            <div className="space-y-4 p-4 border rounded-lg bg-muted/20">
              <h3 className="font-semibold text-sm text-foreground">Basic Information *</h3>

              <div className="grid grid-cols-2 gap-4">
                {/* Transaction Type */}
                <div className="space-y-2">
                  <Label htmlFor="type">Transaction Type *</Label>
                  <Select value={transactionType} onValueChange={setTransactionType}>
                    <SelectTrigger>
                      <SelectValue placeholder="Select type" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="UPI">UPI</SelectItem>
                      <SelectItem value="CARD">Card</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                {/* Amount */}
                <div className="space-y-2">
                  <Label htmlFor="amount">Amount (₹) *</Label>
                  <Input
                    id="amount"
                    type="number"
                    placeholder="Enter amount"
                    value={amount}
                    onChange={(e) => setAmount(e.target.value)}
                    min="0"
                    step="0.01"
                    required
                  />
                </div>

                {/* Merchant */}
                <div className="space-y-2">
                  <Label htmlFor="merchant">Merchant *</Label>
                  <Input
                    id="merchant"
                    placeholder="e.g., PhonePe, Amazon"
                    value={merchant}
                    onChange={(e) => setMerchant(e.target.value)}
                    required
                  />
                </div>

                {/* Category */}
                <div className="space-y-2">
                  <Label htmlFor="category">Category</Label>
                  <Select value={category} onValueChange={setCategory}>
                    <SelectTrigger>
                      <SelectValue placeholder="Select category" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="general">General</SelectItem>
                      <SelectItem value="food">Food & Dining</SelectItem>
                      <SelectItem value="shopping">Shopping</SelectItem>
                      <SelectItem value="entertainment">Entertainment</SelectItem>
                      <SelectItem value="travel">Travel</SelectItem>
                      <SelectItem value="utilities">Utilities</SelectItem>
                      <SelectItem value="healthcare">Healthcare</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                {/* Location */}
                <div className="space-y-2 col-span-2">
                  <Label htmlFor="location">Location</Label>
                  <Input
                    id="location"
                    placeholder="e.g., Mumbai, Delhi"
                    value={location}
                    onChange={(e) => setLocation(e.target.value)}
                  />
                </div>
              </div>
            </div>

            {/* Advanced Fields Toggle */}
            <Button
              variant="outline"
              className="w-full gap-2"
              onClick={() => setShowAdvanced(!showAdvanced)}
            >
              {showAdvanced ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
              {showAdvanced ? "Hide" : "Show"} Advanced Fields (Optional)
            </Button>

            {/* Advanced Fields Section */}
            {showAdvanced && (
              <div className="space-y-4 p-4 border rounded-lg bg-accent/10">
                <h3 className="font-semibold text-sm text-foreground">Advanced Information (Optional)</h3>

                <div className="grid grid-cols-2 gap-4">
                  {/* Transaction ID */}
                  <div className="space-y-2">
                    <Label htmlFor="txId">Transaction ID</Label>
                    <Input
                      id="txId"
                      placeholder="Auto-generated if empty"
                      value={transactionId}
                      onChange={(e) => setTransactionId(e.target.value)}
                    />
                  </div>

                  {/* Timestamp */}
                  <div className="space-y-2">
                    <Label htmlFor="timestamp">Timestamp</Label>
                    <Input
                      id="timestamp"
                      type="datetime-local"
                      value={timestamp}
                      onChange={(e) => setTimestamp(e.target.value)}
                    />
                  </div>

                  {/* Gender */}
                  <div className="space-y-2">
                    <Label htmlFor="gender">Gender</Label>
                    <Select value={gender} onValueChange={setGender}>
                      <SelectTrigger>
                        <SelectValue placeholder="Select gender" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="M">Male</SelectItem>
                        <SelectItem value="F">Female</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>

                  {/* Job */}
                  <div className="space-y-2">
                    <Label htmlFor="job">Job/Occupation</Label>
                    <Input
                      id="job"
                      placeholder="e.g., Engineer, Doctor"
                      value={job}
                      onChange={(e) => setJob(e.target.value)}
                    />
                  </div>

                  {/* Age */}
                  <div className="space-y-2">
                    <Label htmlFor="age">Age</Label>
                    <Input
                      id="age"
                      type="number"
                      placeholder="Customer age"
                      value={age}
                      onChange={(e) => setAge(e.target.value)}
                      min="18"
                      max="100"
                    />
                  </div>

                  {/* City Population */}
                  <div className="space-y-2">
                    <Label htmlFor="cityPop">City Population</Label>
                    <Input
                      id="cityPop"
                      type="number"
                      placeholder="e.g., 100000"
                      value={cityPop}
                      onChange={(e) => setCityPop(e.target.value)}
                    />
                  </div>

                  {/* Customer Latitude */}
                  <div className="space-y-2">
                    <Label htmlFor="lat">Customer Latitude</Label>
                    <Input
                      id="lat"
                      type="number"
                      placeholder="e.g., 19.0760"
                      value={lat}
                      onChange={(e) => setLat(e.target.value)}
                      step="0.0001"
                    />
                  </div>

                  {/* Customer Longitude */}
                  <div className="space-y-2">
                    <Label htmlFor="long">Customer Longitude</Label>
                    <Input
                      id="long"
                      type="number"
                      placeholder="e.g., 72.8777"
                      value={long}
                      onChange={(e) => setLong(e.target.value)}
                      step="0.0001"
                    />
                  </div>

                  {/* Merchant Latitude */}
                  <div className="space-y-2">
                    <Label htmlFor="merchLat">Merchant Latitude</Label>
                    <Input
                      id="merchLat"
                      type="number"
                      placeholder="e.g., 19.0760"
                      value={merchLat}
                      onChange={(e) => setMerchLat(e.target.value)}
                      step="0.0001"
                    />
                  </div>

                  {/* Merchant Longitude */}
                  <div className="space-y-2">
                    <Label htmlFor="merchLong">Merchant Longitude</Label>
                    <Input
                      id="merchLong"
                      type="number"
                      placeholder="e.g., 72.8777"
                      value={merchLong}
                      onChange={(e) => setMerchLong(e.target.value)}
                      step="0.0001"
                    />
                  </div>
                </div>
              </div>
            )}

            {/* Error Alert */}
            {error && (
              <Alert variant="destructive">
                <AlertCircle className="h-4 w-4" />
                <AlertDescription>{error}</AlertDescription>
              </Alert>
            )}

            {/* Submit Button */}
            <Button
              className="w-full gap-2 bg-primary text-primary-foreground hover:bg-primary/90"
              onClick={analyzeTransaction}
              disabled={isAnalyzing || !isFormValid}
              size="lg"
            >
              {isAnalyzing ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  Analyzing with ML Model...
                </>
              ) : (
                <>
                  <Search className="w-4 h-4" />
                  Check Fraud Risk
                </>
              )}
            </Button>
          </div>
        ) : (
          <div className="py-4 space-y-4 animate-fade-in">
            <div
              className={`p-6 rounded-xl ${result.prediction.is_fraud
                  ? "bg-fraud-soft"
                  : "bg-success-soft"
                }`}
            >
              <div className="flex items-center gap-3 mb-4">
                {result.prediction.is_fraud ? (
                  <ShieldAlert className="w-8 h-8 text-fraud-soft-foreground" />
                ) : (
                  <ShieldCheck className="w-8 h-8 text-success-soft-foreground" />
                )}
                <div>
                  <h3
                    className={`text-lg font-semibold ${result.prediction.is_fraud
                        ? "text-fraud-soft-foreground"
                        : "text-success-soft-foreground"
                      }`}
                  >
                    {result.prediction.is_fraud ? "⚠️ Potential Fraud Detected" : "✅ Transaction Safe"}
                  </h3>
                  <p
                    className={`text-sm ${result.prediction.is_fraud
                        ? "text-fraud-soft-foreground/80"
                        : "text-success-soft-foreground/80"
                      }`}
                  >
                    Risk Score: {(result.prediction.risk_score * 100).toFixed(1)}%
                  </p>
                </div>
              </div>

              <div className="space-y-3 border-t pt-4">
                <h4 className="text-sm font-semibold text-foreground/90">Transaction Details:</h4>
                <div className="grid grid-cols-2 gap-2 text-sm">
                  <div className="text-muted-foreground">ID:</div>
                  <div className="font-mono text-xs">{result.transaction.id}</div>

                  <div className="text-muted-foreground">Type:</div>
                  <div className="font-medium">{result.transaction.type}</div>

                  <div className="text-muted-foreground">Amount:</div>
                  <div className="font-medium">₹{result.transaction.amount.toLocaleString('en-IN')}</div>

                  <div className="text-muted-foreground">Merchant:</div>
                  <div className="font-medium">{result.transaction.merchant}</div>

                  <div className="text-muted-foreground">Category:</div>
                  <div className="font-medium">{result.transaction.category}</div>

                  <div className="text-muted-foreground">Location:</div>
                  <div className="font-medium">{result.transaction.location}</div>

                  {result.transaction.job && (
                    <>
                      <div className="text-muted-foreground">Job:</div>
                      <div className="font-medium">{result.transaction.job}</div>
                    </>
                  )}

                  {result.transaction.age && (
                    <>
                      <div className="text-muted-foreground">Age:</div>
                      <div className="font-medium">{result.transaction.age}</div>
                    </>
                  )}

                  <div className="text-muted-foreground">Model:</div>
                  <div className="font-medium">
                    {result.model_type === 'ml_model' ? '🤖 ML Model' : '📏 Rule-Based'}
                  </div>
                </div>
              </div>
            </div>

            <Button
              variant="outline"
              className="w-full"
              onClick={resetForm}
            >
              Check Another Transaction
            </Button>
          </div>
        )}
      </DialogContent>
    </Dialog>
  );
}
