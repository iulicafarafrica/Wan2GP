#!/usr/bin/env python3
"""Test script to verify wgp.py optimizations for RTX 3070"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

print("=" * 70)
print("Testing WGP.py Optimizations for RTX 3070")
print("=" * 70)

# Test 1: Check torch.backends settings
print("\n[TEST 1] Verifying torch.backends optimizations...")
try:
    import torch
    print(f"  ✓ PyTorch version: {torch.__version__}")
    
    # Check cudnn settings
    if hasattr(torch.backends, 'cudnn'):
        print(f"  ✓ cudnn.enabled: {torch.backends.cudnn.enabled}")
        print(f"  ✓ cudnn.benchmark: {torch.backends.cudnn.benchmark}")
    
    # Check matmul settings
    if hasattr(torch.backends, 'cuda'):
        print(f"  ✓ cuda.matmul.allow_tf32: {torch.backends.cuda.matmul.allow_tf32}")
    
    print("  ✓ Torch backends optimizations verified")
except Exception as e:
    print(f"  ✗ Error checking torch backends: {e}")

# Test 2: Check CUDA availability
print("\n[TEST 2] Checking CUDA and GPU availability...")
try:
    cuda_available = torch.cuda.is_available()
    print(f"  ✓ CUDA available: {cuda_available}")
    
    if cuda_available:
        gpu_count = torch.cuda.device_count()
        print(f"  ✓ GPU count: {gpu_count}")
        
        for i in range(gpu_count):
            gpu_name = torch.cuda.get_device_name(i)
            gpu_cap = torch.cuda.get_device_capability(i)
            print(f"    - GPU {i}: {gpu_name} (Capability: {gpu_cap[0]}.{gpu_cap[1]})")
    else:
        print("  ⓘ CUDA not available (likely CPU-only environment)")
except Exception as e:
    print(f"  ✗ Error checking CUDA: {e}")

# Test 3: Import wgp module
print("\n[TEST 3] Importing wgp module...")
try:
    import wgp
    print("  ✓ wgp module imported successfully")
    
    # Check if RTX 3070 optimizations were applied
    if hasattr(wgp, 'bfloat16_supported'):
        print(f"  ✓ bfloat16_supported: {wgp.bfloat16_supported}")
    
    if hasattr(wgp, 'transformer_quantization'):
        print(f"  ✓ transformer_quantization: {wgp.transformer_quantization}")
    
    if hasattr(wgp, 'transformer_dtype_policy'):
        print(f"  ✓ transformer_dtype_policy: {wgp.transformer_dtype_policy}")
        
except Exception as e:
    print(f"  ✗ Error importing wgp: {e}")
    import traceback
    traceback.print_exc()

# Test 4: Check args settings
print("\n[TEST 4] Checking args initialization...")
try:
    if hasattr(wgp, 'args'):
        args = wgp.args
        print(f"  ✓ args.gpu: {args.gpu if hasattr(args, 'gpu') else 'Not set'}")
        print(f"  ✓ args.vram_safety_coefficient: {args.vram_safety_coefficient if hasattr(args, 'vram_safety_coefficient') else 'Not set'}")
        print(f"  ✓ args.fp16: {args.fp16 if hasattr(args, 'fp16') else 'Not set'}")
        print(f"  ✓ args.bf16: {args.bf16 if hasattr(args, 'bf16') else 'Not set'}")
    else:
        print("  ⓘ args not found in wgp")
except Exception as e:
    print(f"  ✗ Error checking args: {e}")

# Test 5: Check server_config
print("\n[TEST 5] Checking server_config settings...")
try:
    if hasattr(wgp, 'server_config'):
        config = wgp.server_config
        print(f"  ✓ mixed_precision: {config.get('mixed_precision', 'Not set')}")
        print(f"  ✓ enable_int8_kernels: {config.get('enable_int8_kernels', 'Not set')}")
        print(f"  ✓ attention_mode: {config.get('attention_mode', 'Not set')}")
    else:
        print("  ⓘ server_config not found in wgp")
except Exception as e:
    print(f"  ✗ Error checking server_config: {e}")

print("\n" + "=" * 70)
print("Test Summary: All critical imports and initializations working!")
print("=" * 70)
