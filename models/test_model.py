"""
Simple test to verify model file and view metrics
"""
import joblib
import json

print("="*80)
print("🧪 FRAUD DETECTION MODEL - VALIDATION TEST")
print("="*80)

# 1. Test model file
print("\n✅ Step 1: Verify Model File")
print("-" * 40)
try:
    import os
    file_size = os.path.getsize("fraud_detection_system.pkl")
    print(f"   📦 File: fraud_detection_system.pkl")
    print(f"   📏 Size: {file_size / 1024 / 1024:.2f} MB")
    
    model_package = joblib.load("fraud_detection_system.pkl")
    print(f"   ✅ Model loaded successfully")
    
    if isinstance(model_package, dict):
        print(f"   📋 Package contains: {', '.join(model_package.keys())}")
        print(f"   🎯 Optimized Threshold: {model_package.get('threshold', 'N/A'):.4f}")
    else:
        print(f"   📦 Model type: {type(model_package).__name__}")
        
except Exception as e:
    print(f"   ❌ Error: {e}")
    exit(1)

# 2. Test metadata
print("\n✅ Step 2: Performance Metrics")
print("-" * 40)
try:
    with open("model_metadata.json", 'r') as f:
        metadata = json.load(f)
    
    print(f"   📊 Accuracy:  {metadata.get('accuracy', 0):.4f} ({metadata.get('accuracy', 0)*100:.2f}%)")
    print(f"   📊 F1 Score:  {metadata.get('f1_score', 0):.4f}")
    print(f"   📊 ROC-AUC:   {metadata.get('roc_auc', 0):.4f}")
    print(f"   🎯 Threshold: {metadata.get('threshold', 0):.4f}")
    
    # Check confusion matrix
    if 'confusion_matrix' in metadata:
        cm = metadata['confusion_matrix']
        tn, fp = cm[0]
        fn, tp = cm[1]
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0
        
        print(f"\n   🔢 Confusion Matrix:")
        print(f"      True Negatives:  {tn:,}")
        print(f"      False Positives: {fp:,}")
        print(f"      False Negatives: {fn:,}")
        print(f"      True Positives:  {tp:,}")
        print(f"\n   📈 Derived Metrics:")
        print(f"      Recall:    {recall:.4f} ({recall*100:.1f}% of fraud caught)")
        print(f"      Precision: {precision:.4f} ({precision*100:.1f}% accuracy when flagging fraud)")
        
except Exception as e:
    print(f"   ⚠️  Could not load metadata: {e}")

# 3. Test threshold file
print("\n✅ Step 3: Threshold File")
print("-" * 40)
try:
    with open("threshold.txt", 'r') as f:
        threshold_value = f.read().strip()
    print(f"   ✅ Threshold: {threshold_value}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# 4. Requirements Check
print("\n✅ Step 4: Requirements Verification")
print("-" * 40)

requirements = {
    'Accuracy': (metadata.get('accuracy', 0), 0.995, '> 99.5%'),
    'F1 Score': (metadata.get('f1_score', 0), 0.80, '> 0.80'),
    'ROC-AUC': (metadata.get('roc_auc', 0), 0.90, '> 0.90'),
}

all_passed = True
for metric_name, (value, threshold, requirement) in requirements.items():
    passed = value >= threshold
    emoji = "✅" if passed else "❌"
    status = "PASS" if passed else "FAIL"
    print(f"   {emoji} {metric_name}: {value:.4f} (Required: {requirement}) - {status}")
    if not passed:
        all_passed = False

# 5. Final Summary
print("\n" + "="*80)
print("📊 VALIDATION SUMMARY")
print("="*80)

if all_passed:
    print("✅ ALL TESTS PASSED!")
    print("✅ Model meets all performance requirements")
    print("✅ Model is ready for production use")
    print("\n🎉 Ready for hackathon demonstration!")
else:
    print("⚠️  Some requirements not met")
    print("   Consider retraining with different parameters")

print("\n📝 Next Steps:")
print("  1. Start Backend:  cd ../backend && py main.py")
print("  2. Start Frontend: cd ../frontend && npm install && npm start")
print("  3. Open browser:   http://localhost:3000")
print("="*80)
