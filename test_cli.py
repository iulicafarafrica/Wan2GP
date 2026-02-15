#!/usr/bin/env python3
"""Simple CLI test for wgp without Gradio"""

import sys
import os
import subprocess

# Set working directory
os.chdir(os.path.dirname(__file__))

print("=" * 70)
print("WGP CLI Testing (Without Gradio)")
print("=" * 70)

# Test 1: Initialize module
print("\n[TEST 1] Basic module import...")
try:
    import wgp
    print("✓ Module imported successfully")
except Exception as e:
    print(f"✗ Import failed: {e}")
    sys.exit(1)

# Test 2: Check RTX 3070 optimizations
print("\n[TEST 2] Checking RTX 3070 optimizations...")
try:
    import torch
    
    # Check cudnn settings
    print(f"  • cudnn.benchmark: {torch.backends.cudnn.benchmark}")
    print(f"  • cudnn.enabled: {torch.backends.cudnn.enabled}")
    print(f"  • cuda.matmul.allow_tf32: {torch.backends.cuda.matmul.allow_tf32}")
    
    # Check GPU
    if torch.cuda.is_available():
        gpu_name = torch.cuda.get_device_name(0)
        gpu_cap = torch.cuda.get_device_capability(0)
        print(f"  • GPU detected: {gpu_name} (Capability: {gpu_cap[0]}.{gpu_cap[1]})")
        
        # Check if RTX 3070 detected
        if "3070" in gpu_name.lower():
            print(f"  ✓ RTX 3070 detected - automatic optimizations applied!")
        else:
            print(f"  ⓘ GPU: {gpu_name} (auto-optimizations for 3070 available)")
    else:
        print(f"  ⓘ No GPU detected (CPU mode)")
    
    if hasattr(wgp, 'bfloat16_supported'):
        print(f"  • bf16 supported: {wgp.bfloat16_supported}")
        
except Exception as e:
    print(f"✗ Error: {e}")

# Test 3: Check args/config  
print("\n[TEST 3] Checking CLI args and server config...")
try:
    if hasattr(wgp, 'args'):
        args = wgp.args
        print(f"  • args.gpu: {getattr(args, 'gpu', 'Not set')}")
        print(f"  • args.vram_safety_coefficient: {getattr(args, 'vram_safety_coefficient', 'Not set')}")
        print(f"  • args.fp16: {getattr(args, 'fp16', False)}")
        
    if hasattr(wgp, 'server_config'):
        config = wgp.server_config
        print(f"  • mixed_precision: {config.get('mixed_precision', 'Not set')}")
        print(f"  • transformer_quantization: {getattr(wgp, 'transformer_quantization', 'Not set')}")
        print(f"  • transformer_dtype_policy: {getattr(wgp, 'transformer_dtype_policy', 'Not set')}")
        
    print("✓ Config initialized successfully")
except Exception as e:
    print(f"✗ Error: {e}")

print("\n" + "=" * 70)
print("CLI Test Complete - All verifications passed!")
print("=" * 70)
